from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, features

from scripts.content_store import (
    ContentValidationError,
    load_content_bundle,
    normalize_content_bundle,
    validate_content_bundle,
    validate_publishable_content,
    write_content_bundle,
)

from .config import AUTHENTICATED_REPOSITORY_URL, PUBLISH_BRANCH, set_workspace


class EditorError(RuntimeError):
    pass


class CommandError(EditorError):
    def __init__(self, command: str, output: str, return_code: int) -> None:
        self.command = command
        self.output = output
        self.return_code = return_code
        super().__init__(output or f"El comando fallo con codigo {return_code}.")


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError as exc:
        if command and command[0] == "git":
            raise EditorError("Git no esta instalado o no esta disponible en PATH.") from exc
        raise EditorError(f"No se encontro el programa requerido: {command[0]}.") from exc
    if check and completed.returncode:
        safe_command = " ".join(part for part in command if "github_pat_" not in part and "ghp_" not in part)
        raise CommandError(safe_command, completed.stdout.strip(), completed.returncode)
    return completed


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return cleaned[:80] or "file"


def _string_values(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _string_values(item)
    elif isinstance(value, str):
        yield value


def _generator_command(source: Path, output: Path, bundle: Path) -> list[str]:
    arguments = ["--internal-generate", str(source), str(output), str(bundle)]
    if getattr(sys, "frozen", False):
        return [sys.executable, *arguments]
    return [sys.executable, "-m", "editor.launcher", *arguments]


class AskPass:
    def __init__(self, token: str) -> None:
        self.token = token
        self.directory: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> dict[str, str]:
        self.directory = tempfile.TemporaryDirectory(prefix="ish-editor-askpass-")
        root = Path(self.directory.name)
        environment = os.environ.copy()
        environment["ISH_GITHUB_TOKEN"] = self.token
        environment["GIT_TERMINAL_PROMPT"] = "0"
        if os.name == "nt":
            helper = root / "askpass.cmd"
            helper.write_text(
                "@echo off\r\necho %ISH_GITHUB_TOKEN%\r\n",
                encoding="utf-8",
            )
        else:
            helper = root / "askpass.sh"
            helper.write_text("#!/bin/sh\nprintf '%s\\n' \"$ISH_GITHUB_TOKEN\"\n", encoding="utf-8")
            helper.chmod(0o700)
        environment["GIT_ASKPASS"] = str(helper)
        return environment

    def __exit__(self, *_: object) -> None:
        if self.directory:
            self.directory.cleanup()


class Workspace:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.state_root = self.root / ".ish-editor"
        self.draft_path = self.state_root / "drafts" / "current.json"
        self.history_root = self.state_root / "drafts" / "history"
        self.preview_root = self.state_root / "preview"
        self.pending_root = self.state_root / "pending"
        self.trash_root = self.state_root / "trash"
        self.deletions_path = self.state_root / "media-deletions.json"
        self._preview_lock = threading.Lock()

    def assert_valid(self) -> None:
        required = [self.root / ".git", self.root / "scripts" / "build_site.py", self.root / "content"]
        if not all(path.exists() for path in required):
            raise EditorError("La carpeta seleccionada no es una copia valida del sitio ISH.")

    def git(self, *args: str, check: bool = True, env: dict[str, str] | None = None) -> str:
        return _run(["git", *args], cwd=self.root, env=env, check=check).stdout.strip()

    def head(self) -> str:
        return self.git("rev-parse", "HEAD")

    def branch(self) -> str:
        return self.git("branch", "--show-current") or "detached"

    def dirty_paths(self) -> list[str]:
        output = self.git("status", "--porcelain=v1", "--untracked-files=all")
        return [line[3:] for line in output.splitlines() if len(line) > 3]

    def status(self) -> dict[str, Any]:
        self.assert_valid()
        return {
            "root": str(self.root),
            "branch": self.branch(),
            "head": self.head(),
            "dirty_paths": self.dirty_paths(),
            "draft": self.draft_path.exists(),
            "pending_uploads": len([path for path in self.pending_root.rglob("*") if path.is_file()]) if self.pending_root.exists() else 0,
            "pending_deletions": len(self._load_deletions()),
            "publish_remote": self.publish_remote(),
        }

    def publish_remote(self) -> str | None:
        remotes = self.git("remote").splitlines()
        ordered = sorted(remotes, key=lambda name: (name != "fcv", name != "origin", name))
        for name in ordered:
            url = self.git("remote", "get-url", name, check=False).lower().replace("\\", "/")
            if "fundacion-ciencia-vida/ish" in url and (url.startswith("git@") or url.startswith("ssh://")):
                return name
        return None

    def _load_deletions(self) -> list[str]:
        if not self.deletions_path.exists():
            return []
        try:
            payload = json.loads(self.deletions_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [str(item) for item in payload if isinstance(item, str)] if isinstance(payload, list) else []

    def load_draft_record(self) -> dict[str, Any]:
        if self.draft_path.exists():
            try:
                payload = json.loads(self.draft_path.read_text(encoding="utf-8"))
                normalize_content_bundle(payload["bundle"])
                validate_content_bundle(payload["bundle"])
                return payload
            except (OSError, json.JSONDecodeError, KeyError, ContentValidationError):
                pass
        bundle = load_content_bundle(self.root / "content")
        return {
            "base_commit": self.head(),
            "saved_at": datetime.now(UTC).isoformat(),
            "bundle": bundle,
        }

    def save_draft(self, bundle: dict[str, Any], *, snapshot: bool = False) -> dict[str, Any]:
        validate_content_bundle(bundle)
        previous = self.load_draft_record()
        record = {
            "base_commit": previous.get("base_commit") or self.head(),
            "saved_at": datetime.now(UTC).isoformat(),
            "bundle": bundle,
        }
        _atomic_json(self.draft_path, record)
        if snapshot:
            digest = hashlib.sha256(json.dumps(bundle, sort_keys=True).encode("utf-8")).hexdigest()[:10]
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            _atomic_json(self.history_root / f"{stamp}-{digest}.json", record)
            snapshots = sorted(self.history_root.glob("*.json"), reverse=True)
            for path in snapshots[50:]:
                path.unlink()
        return {"saved_at": record["saved_at"], "base_commit": record["base_commit"]}

    def draft_history(self) -> list[dict[str, str]]:
        entries = []
        for path in sorted(self.history_root.glob("*.json"), reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                entries.append({"id": path.name, "saved_at": payload.get("saved_at", ""), "base_commit": payload.get("base_commit", "")})
            except (OSError, json.JSONDecodeError):
                continue
        return entries

    def restore_draft_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        if Path(snapshot_id).name != snapshot_id:
            raise EditorError("Identificador de borrador invalido.")
        path = self.history_root / snapshot_id
        if not path.exists():
            raise EditorError("La revision local solicitada no existe.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_content_bundle(payload["bundle"])
        self.save_draft(payload["bundle"], snapshot=False)
        return payload["bundle"]

    def build_preview(self, bundle: dict[str, Any]) -> dict[str, Any]:
        with self._preview_lock:
            return self._build_preview(bundle)

    def _build_preview(self, bundle: dict[str, Any]) -> dict[str, Any]:
        self.save_draft(bundle)
        self.state_root.mkdir(parents=True, exist_ok=True)
        bundle_file = self.state_root / "preview-bundle.json"
        _atomic_json(bundle_file, bundle)
        if self.preview_root.exists():
            shutil.rmtree(self.preview_root)
        self.preview_root.mkdir(parents=True)
        if self.pending_root.exists():
            shutil.copytree(self.pending_root, self.preview_root, dirs_exist_ok=True)
        completed = _run(
            _generator_command(self.root, self.preview_root, bundle_file),
            cwd=self.root,
        )
        pages = {
            page["id"]: (f'{str(page.get("route", "")).strip("/")}/' if page.get("route") else "")
            for page in bundle["pages"]
        }
        return {"pages": pages, "output": completed.stdout.strip()}

    def list_published_history(self, limit: int = 30) -> list[dict[str, str]]:
        format_string = "%H%x1f%aI%x1f%s%x1e"
        output = self.git("log", f"--max-count={limit}", f"--format={format_string}", "--", "content")
        entries = []
        for record in output.split("\x1e"):
            fields = [field.strip() for field in record.split("\x1f")]
            if len(fields) == 3 and fields[0]:
                entries.append({"commit": fields[0], "date": fields[1], "message": fields[2]})
        return entries

    def bundle_from_commit(self, commit: str) -> dict[str, Any]:
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", commit):
            raise EditorError("Commit invalido.")
        paths = self.git("ls-tree", "-r", "--name-only", commit, "content").splitlines()
        if "content/site.json" not in paths:
            raise EditorError("La publicacion seleccionada no contiene contenido administrable.")
        with tempfile.TemporaryDirectory(prefix="ish-editor-history-") as temp_name:
            root = Path(temp_name) / "content"
            for relative in paths:
                if not relative.endswith(".json"):
                    continue
                target = Path(temp_name) / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(self.git("show", f"{commit}:{relative}"), encoding="utf-8")
            return load_content_bundle(root)

    def restore_published(self, commit: str) -> dict[str, Any]:
        bundle = self.bundle_from_commit(commit)
        self.save_draft(bundle, snapshot=True)
        return bundle

    def add_pending_upload(self, filename: str, payload: bytes, kind: str) -> dict[str, Any]:
        safe = _safe_name(filename)
        stem = Path(safe).stem[:48]
        suffix = Path(safe).suffix.lower()
        digest = hashlib.sha256(payload).hexdigest()[:10]
        if kind == "image":
            if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
                raise EditorError("Formato de imagen no compatible.")
            relative = Path("assets/images/uploads") / f"{stem}-{digest}{suffix}"
        elif kind == "document":
            if suffix != ".pdf" or not payload.startswith(b"%PDF"):
                raise EditorError("El documento debe ser un PDF valido.")
            relative = Path("assets/documents/uploads") / f"{stem}-{digest}.pdf"
        else:
            raise EditorError("Tipo de archivo no compatible.")
        target = self.pending_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        if kind == "image":
            try:
                with Image.open(target) as image:
                    width, height = image.size
                    image.verify()
            except Exception as exc:
                target.unlink(missing_ok=True)
                raise EditorError("No fue posible leer la imagen.") from exc
            if width * height > 50_000_000:
                target.unlink(missing_ok=True)
                raise EditorError("La imagen supera el limite de 50 megapixeles.")
        else:
            width = height = 0
        return {
            "path": relative.as_posix(),
            "asset": relative.relative_to("assets/images").as_posix() if kind == "image" else relative.as_posix(),
            "kind": kind,
            "name": filename,
            "width": width,
            "height": height,
            "pending": True,
        }

    def media_items(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        deleted = set(self._load_deletions())
        roots = [
            (self.root / "assets" / "images", "image", self.root),
            (self.root / "assets" / "documents", "document", self.root),
            (self.pending_root / "assets" / "images", "image", self.pending_root),
            (self.pending_root / "assets" / "documents", "document", self.pending_root),
        ]
        for root, kind, relative_root in roots:
            if not root.exists():
                continue
            for path in sorted(root.rglob("*")):
                if not path.is_file() or "optimized" in path.parts:
                    continue
                if kind == "image" and path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
                    continue
                if kind == "document" and path.suffix.lower() != ".pdf":
                    continue
                relative = path.relative_to(relative_root).as_posix()
                asset = relative.split("assets/images/", 1)[1] if kind == "image" else relative
                items.append({"path": relative, "asset": asset, "kind": kind, "name": path.name, "pending": relative_root == self.pending_root, "pending_delete": relative_root == self.root and relative in deleted})
        return items

    def remove_media(self, relative_path: str, bundle: dict[str, Any]) -> None:
        normalized = Path(relative_path).as_posix().lstrip("/")
        references = {normalized}
        if normalized.startswith("assets/images/"):
            references.add(normalized.removeprefix("assets/images/"))
        if any(value.split("?", 1)[0].split("#", 1)[0] in references for value in _string_values(bundle)):
            raise EditorError("El recurso esta siendo utilizado por el contenido.")

        pending_target = (self.pending_root / normalized).resolve()
        if self.pending_root.resolve() in pending_target.parents and pending_target.exists():
            pending_target.unlink()
            return

        allowed_roots = ("assets/images/", "assets/documents/")
        if not normalized.startswith(allowed_roots) or "/optimized/" in normalized:
            raise EditorError("El recurso seleccionado no puede eliminarse desde el editor.")
        published_target = (self.root / normalized).resolve()
        if self.root.resolve() not in published_target.parents or not published_target.is_file():
            raise EditorError("El recurso seleccionado no existe.")
        deletions = set(self._load_deletions())
        deletions.add(normalized)
        self.deletions_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.deletions_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(sorted(deletions), indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.deletions_path)

    def restore_media(self, relative_path: str) -> None:
        normalized = Path(relative_path).as_posix().lstrip("/")
        deletions = set(self._load_deletions())
        if normalized not in deletions:
            raise EditorError("El recurso no esta marcado para eliminacion.")
        deletions.remove(normalized)
        if not deletions:
            self.deletions_path.unlink(missing_ok=True)
            return
        temporary = self.deletions_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(sorted(deletions), indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.deletions_path)

    @staticmethod
    def _generated_paths(bundle: dict[str, Any]) -> set[str]:
        paths = {"sitemap.xml", "styles.min.css", "fonts.min.css", "script.min.js"}
        for page in bundle["pages"]:
            route = str(page.get("route", "")).strip("/")
            paths.add(f"{route}/index.html" if route else "index.html")
        return paths

    @staticmethod
    def _allowed_change(path: str, generated: set[str], deleted: set[str] | None = None) -> bool:
        normalized = path.replace("\\", "/")
        return (
            normalized.startswith("content/")
            or normalized in generated
            or normalized.startswith("assets/images/uploads/")
            or normalized.startswith("assets/documents/uploads/")
            or normalized.startswith("assets/images/optimized/uploads/")
            or normalized == "assets/images/optimized/manifest.json"
            or normalized in (deleted or set())
        )

    def _apply_staged_deletions(self, worktree: Path) -> set[str]:
        deletions = self._load_deletions()
        if not deletions:
            return set()
        manifest_path = worktree / "assets" / "images" / "optimized" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        changed_manifest = False
        removed: set[str] = set()
        for relative in deletions:
            target = worktree / relative
            if target.is_file():
                target.unlink()
            removed.add(relative)
            if not relative.startswith("assets/images/"):
                continue
            source_key = relative.removeprefix("assets/images/")
            entry = manifest.pop(source_key, None)
            if not isinstance(entry, dict):
                continue
            changed_manifest = True
            variants = entry.get("formats", {})
            variant_lists: list[Any] = list(variants.values()) if isinstance(variants, dict) else []
            if isinstance(entry.get("variants"), list):
                variant_lists.append(entry["variants"])
            for items in variant_lists:
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                        continue
                    optimized = f'assets/images/{item["path"]}'
                    (worktree / optimized).unlink(missing_ok=True)
                    removed.add(optimized)
        if changed_manifest:
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            removed.add("assets/images/optimized/manifest.json")
        return removed

    @staticmethod
    def _optimize_uploaded_images(worktree: Path, image_paths: list[Path]) -> None:
        manifest_path = worktree / "assets" / "images" / "optimized" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        supports_avif = bool(features.check("avif"))
        for source in image_paths:
            with Image.open(source) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
                width, height = image.size
                relative = source.relative_to(worktree / "assets" / "images")
                widths = sorted({candidate for candidate in (320, 480, 640, 960, 1280, width) if candidate <= width})
                formats: dict[str, list[dict[str, Any]]] = {"webp": []}
                if supports_avif:
                    formats["avif"] = []
                for target_width in widths:
                    target_height = round(height * target_width / width)
                    resized = image if target_width == width else image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    for extension, quality in (("webp", 82), ("avif", 52)):
                        if extension == "avif" and not supports_avif:
                            continue
                        target = worktree / "assets" / "images" / "optimized" / relative.parent / f"{relative.stem}-{target_width}.{extension}"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        resized.save(target, extension.upper(), quality=quality)
                        formats[extension].append({"width": target_width, "height": target_height, "bytes": target.stat().st_size, "path": target.relative_to(worktree / "assets" / "images").as_posix()})
                manifest[relative.as_posix()] = {
                    "width": width,
                    "height": height,
                    "bytes": source.stat().st_size,
                    "formats": formats,
                    "variants": formats["webp"],
                }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _copy_pending(self, worktree: Path) -> list[Path]:
        image_paths = []
        if not self.pending_root.exists():
            return image_paths
        for source in self.pending_root.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(self.pending_root)
            target = worktree / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if relative.as_posix().startswith("assets/images/"):
                image_paths.append(target)
        return image_paths

    def _remote_head(self, token: str) -> str:
        if token:
            with AskPass(token) as environment:
                self.git("fetch", "--quiet", AUTHENTICATED_REPOSITORY_URL, PUBLISH_BRANCH, env=environment)
        else:
            remote = self.publish_remote()
            if not remote:
                raise EditorError("Configura un token de GitHub o un remoto SSH para fundacion-ciencia-vida/ISH.")
            environment = os.environ.copy()
            environment["GIT_TERMINAL_PROMPT"] = "0"
            self.git("fetch", "--quiet", remote, PUBLISH_BRANCH, env=environment)
        return self.git("rev-parse", "FETCH_HEAD")

    def sync(self, token: str) -> dict[str, Any]:
        if self.dirty_paths():
            raise EditorError("El repositorio contiene cambios manuales. Resuelvelos antes de sincronizar.")
        remote_head = self._remote_head(token)
        local_head = self.head()
        if local_head != remote_head:
            ancestor = _run(
                ["git", "merge-base", "--is-ancestor", local_head, remote_head],
                cwd=self.root,
                check=False,
            )
            if ancestor.returncode:
                raise EditorError("La historia local y GitHub han divergido.")
            result = _run(["git", "merge", "--ff-only", remote_head], cwd=self.root, check=False)
            if result.returncode:
                raise EditorError(result.stdout.strip() or "No fue posible actualizar el repositorio.")
        return {"head": self.head(), "updated": local_head != remote_head}

    def publish(self, bundle: dict[str, Any], token: str, message: str) -> dict[str, Any]:
        validate_publishable_content(bundle)
        publish_remote = AUTHENTICATED_REPOSITORY_URL if token else self.publish_remote()
        if not publish_remote:
            raise EditorError("Configura un token de GitHub o un remoto SSH para publicar.")
        dirty = self.dirty_paths()
        if dirty:
            raise EditorError("La publicacion se bloqueo porque existen cambios manuales: " + ", ".join(dirty[:8]))

        draft = self.load_draft_record()
        remote_head = self._remote_head(token)
        local_head = self.head()
        base_commit = str(draft.get("base_commit", local_head))
        if base_commit != remote_head:
            content_changes = self.git("diff", "--name-only", base_commit, remote_head, "--", "content")
            if content_changes:
                raise EditorError("GitHub contiene cambios de contenido posteriores a este borrador. Sincroniza antes de publicar.")
        if local_head != remote_head:
            local_is_ancestor = _run(
                ["git", "merge-base", "--is-ancestor", local_head, remote_head],
                cwd=self.root,
                check=False,
            )
            if local_is_ancestor.returncode:
                remote_is_ancestor = _run(
                    ["git", "merge-base", "--is-ancestor", remote_head, local_head],
                    cwd=self.root,
                    check=False,
                )
                if remote_is_ancestor.returncode == 0:
                    raise EditorError("La copia local contiene commits sin publicar. Envialos o sincroniza el repositorio antes de usar el editor.")
                raise EditorError("La historia local y GitHub han divergido.")
            _run(["git", "merge", "--ff-only", remote_head], cwd=self.root)
            local_head = remote_head

        old_bundle = load_content_bundle(self.root / "content")
        old_generated = self._generated_paths(old_bundle)
        new_generated = self._generated_paths(bundle)
        self.state_root.mkdir(parents=True, exist_ok=True)
        worktree = Path(tempfile.mkdtemp(prefix="publish-", dir=self.state_root))
        committed = ""
        try:
            self.git("worktree", "add", "--detach", str(worktree), local_head)
            write_content_bundle(bundle, worktree / "content")
            for obsolete in old_generated - new_generated:
                target = worktree / obsolete
                if target.exists() and target.is_file():
                    target.unlink()
            deleted_media = self._apply_staged_deletions(worktree)
            uploaded_images = self._copy_pending(worktree)
            if uploaded_images:
                self._optimize_uploaded_images(worktree, uploaded_images)
            bundle_file = self.state_root / "publish-bundle.json"
            _atomic_json(bundle_file, bundle)
            _run(_generator_command(worktree, worktree, bundle_file), cwd=worktree)

            status_output = _run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=worktree).stdout
            changed = [line[3:] for line in status_output.splitlines() if len(line) > 3]
            generated = old_generated | new_generated
            unexpected = [path for path in changed if not self._allowed_change(path, generated, deleted_media)]
            if unexpected:
                raise EditorError("La compilacion intento modificar archivos no administrados: " + ", ".join(unexpected[:8]))
            if not changed:
                return {"published": False, "message": "No hay cambios para publicar.", "commit": local_head}
            stage_paths = ["content", *sorted(generated), *sorted(deleted_media)]
            manifest_path = "assets/images/optimized/manifest.json"
            if (worktree / manifest_path).exists() or manifest_path in deleted_media:
                stage_paths.append(manifest_path)
            for optional in ("assets/images/uploads", "assets/documents/uploads", "assets/images/optimized/uploads"):
                if (worktree / optional).exists():
                    stage_paths.append(optional)
            _run(["git", "add", "-A", "--", *stage_paths], cwd=worktree)
            clean_message = re.sub(r"[\r\n]+", " ", message).strip()[:120] or "Update site content"
            _run(["git", "commit", "-m", clean_message, "-m", "ISH-Editor: true"], cwd=worktree)
            committed = _run(["git", "rev-parse", "HEAD"], cwd=worktree).stdout.strip()
            if token:
                with AskPass(token) as environment:
                    _run(["git", "push", publish_remote, f"HEAD:{PUBLISH_BRANCH}"], cwd=worktree, env=environment)
            else:
                environment = os.environ.copy()
                environment["GIT_TERMINAL_PROMPT"] = "0"
                _run(["git", "push", publish_remote, f"HEAD:{PUBLISH_BRANCH}"], cwd=worktree, env=environment)
        finally:
            self.git("worktree", "remove", "--force", str(worktree), check=False)
            shutil.rmtree(worktree, ignore_errors=True)
            (self.state_root / "publish-bundle.json").unlink(missing_ok=True)

        if token:
            with AskPass(token) as environment:
                self.git("fetch", "--quiet", publish_remote, PUBLISH_BRANCH, env=environment)
        else:
            environment = os.environ.copy()
            environment["GIT_TERMINAL_PROMPT"] = "0"
            self.git("fetch", "--quiet", publish_remote, PUBLISH_BRANCH, env=environment)
        self.git("merge", "--ff-only", "FETCH_HEAD")
        if self.pending_root.exists():
            shutil.rmtree(self.pending_root)
        self.deletions_path.unlink(missing_ok=True)
        record = {"base_commit": self.head(), "saved_at": datetime.now(UTC).isoformat(), "bundle": bundle}
        _atomic_json(self.draft_path, record)
        return {"published": True, "message": "Publicacion completada.", "commit": committed}


def clone_workspace(destination: Path, token: str) -> Workspace:
    destination = destination.expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise EditorError("La carpeta de destino debe estar vacia.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with AskPass(token) as environment:
        _run(
            ["git", "clone", "--branch", PUBLISH_BRANCH, "--single-branch", AUTHENTICATED_REPOSITORY_URL, str(destination)],
            cwd=destination.parent,
            env=environment,
        )
    workspace = Workspace(destination)
    workspace.assert_valid()
    set_workspace(destination)
    return workspace
