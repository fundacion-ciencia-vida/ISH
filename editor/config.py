from __future__ import annotations

import json
import os
import platform
import tempfile
from pathlib import Path
from typing import Any


APP_NAME = "ISH Editor"
REPOSITORY_URL = "https://github.com/fundacion-ciencia-vida/ISH.git"
AUTHENTICATED_REPOSITORY_URL = "https://x-access-token@github.com/fundacion-ciencia-vida/ISH.git"
PUBLISH_BRANCH = "gh-pages"

EDITION_CATALOG: list[dict[str, Any]] = [
    {
        "id": "basic",
        "label": "Basica",
        "price_label": "$800.000 liquido",
        "features": [
            "Editar textos, enlaces e imagenes existentes",
            "Crear, ordenar y publicar comunicaciones",
            "Medios, vista previa, historial y publicacion",
        ],
    },
    {
        "id": "advanced",
        "label": "Avanzada",
        "price_label": "$1.200.000 liquido",
        "features": [
            "Todo lo incluido en la edicion basica",
            "Crear y eliminar paginas",
            "Plantillas, secciones, rutas y navegacion",
            "Reordenar, ocultar y cambiar la estructura",
        ],
    },
]

EDITION_ALIASES = {
    "base": "basic",
    "basic": "basic",
    "custom": "advanced",
    "extended": "advanced",
    "advanced": "advanced",
    "complete": "unified",
    "full": "unified",
    "unified": "unified",
}


def _platform_directory(kind: str) -> Path:
    system = platform.system()
    if system == "Windows":
        variable = "APPDATA" if kind == "config" else "LOCALAPPDATA"
        base = Path(os.environ.get(variable, tempfile.gettempdir()))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        variable = "XDG_CONFIG_HOME" if kind == "config" else "XDG_STATE_HOME"
        fallback = Path.home() / (".config" if kind == "config" else ".local/state")
        base = Path(os.environ.get(variable, fallback))
    return base / "ish-editor"


CONFIG_DIR = _platform_directory("config")
STATE_DIR = _platform_directory("state")
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        payload = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def save_config(payload: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(CONFIG_FILE)


def configured_workspace() -> Path | None:
    override = os.environ.get("ISH_EDITOR_REPO")
    if override:
        return Path(override).expanduser().resolve()
    configured = load_config().get("workspace")
    if configured:
        return Path(str(configured)).expanduser().resolve()
    development_root = Path(__file__).resolve().parents[1]
    if (development_root / ".git").exists() and (development_root / "scripts" / "build_site.py").exists():
        return development_root
    return None


def set_workspace(path: Path) -> None:
    payload = load_config()
    payload["workspace"] = str(path.resolve())
    save_config(payload)


def editor_edition_id() -> str:
    configured = os.environ.get("ISH_EDITOR_EDITION", "").strip().lower()
    if configured:
        return EDITION_ALIASES.get(configured, "basic")
    saved = str(load_config().get("edition", "")).strip().lower()
    if saved:
        return EDITION_ALIASES.get(saved, "basic")
    legacy_scope = os.environ.get("ISH_EDITOR_SCOPE", "base").strip().lower()
    return EDITION_ALIASES.get(legacy_scope, "basic")


def set_editor_edition(edition: str) -> str:
    normalized = EDITION_ALIASES.get(edition.strip().lower())
    if normalized is None:
        raise ValueError("Edicion de editor invalida.")
    payload = load_config()
    payload["edition"] = normalized
    save_config(payload)
    return normalized


def editor_edition() -> dict[str, Any]:
    edition_id = editor_edition_id()
    if edition_id == "unified":
        return {
            "id": "unified",
            "label": "Completa",
            "price_label": "",
            "show_distinction": False,
            "advanced_features": True,
        }
    selected = next(item for item in EDITION_CATALOG if item["id"] == edition_id)
    return {
        "id": edition_id,
        "label": selected["label"],
        "price_label": selected["price_label"],
        "show_distinction": True,
        "advanced_features": edition_id == "advanced",
    }


def editor_edition_catalog() -> list[dict[str, Any]]:
    return [] if editor_edition_id() == "unified" else EDITION_CATALOG


def custom_site_enabled() -> bool:
    return bool(editor_edition()["advanced_features"])
