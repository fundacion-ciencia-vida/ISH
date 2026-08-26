from __future__ import annotations

import copy
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from editor.workspace import EditorError, Workspace
from scripts.content_store import ContentValidationError, load_content_bundle
from tests.helpers import create_seed_repository, run


class WorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = create_seed_repository(self.base / "workspace")
        self.workspace = Workspace(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_draft_snapshot_can_be_restored(self) -> None:
        bundle = load_content_bundle(self.root / "content")
        bundle["pages"][0]["title"] = "Draft title"
        self.workspace.save_draft(bundle, snapshot=True)
        history = self.workspace.draft_history()
        self.assertEqual(len(history), 1)
        restored = self.workspace.restore_draft_snapshot(history[0]["id"])
        self.assertEqual(restored["pages"][0]["title"], "Draft title")

    def test_referenced_pending_media_cannot_be_removed(self) -> None:
        stream = io.BytesIO()
        Image.new("RGB", (24, 18), "white").save(stream, "PNG")
        item = self.workspace.add_pending_upload("sample.png", stream.getvalue(), "image")
        bundle = load_content_bundle(self.root / "content")
        bundle["pages"][0]["hero_image"] = item["asset"]
        with self.assertRaises(EditorError):
            self.workspace.remove_media(item["path"], bundle)
        bundle["pages"][0]["hero_image"] = "test.png"
        self.workspace.remove_media(item["path"], bundle)
        self.assertFalse((self.workspace.pending_root / item["path"]).exists())

    def test_detects_fundacion_ssh_remote(self) -> None:
        run("git", "remote", "add", "fcv", "git@github-fcv:fundacion-ciencia-vida/ISH.git", cwd=self.root)
        self.assertEqual(self.workspace.publish_remote(), "fcv")

    def test_published_media_deletion_can_be_restored(self) -> None:
        bundle = load_content_bundle(self.root / "content")
        bundle["pages"][0]["social_image"] = ""
        bundle["pages"][0]["hero_image"] = ""
        self.workspace.remove_media("assets/images/test.png", bundle)
        self.assertEqual(self.workspace._load_deletions(), ["assets/images/test.png"])
        item = next(item for item in self.workspace.media_items() if item["path"] == "assets/images/test.png")
        self.assertTrue(item["pending_delete"])
        self.workspace.restore_media("assets/images/test.png")
        self.assertEqual(self.workspace._load_deletions(), [])

    def test_publish_blocks_unpublished_local_commits(self) -> None:
        remote_head = self.workspace.head()
        run("git", "commit", "--allow-empty", "-m", "Local only", cwd=self.root)
        bundle = load_content_bundle(self.root / "content")
        self.workspace.save_draft(bundle)
        with patch.object(self.workspace, "_remote_head", return_value=remote_head):
            with self.assertRaisesRegex(EditorError, "commits sin publicar"):
                self.workspace.publish(bundle, "test-token", "Should not publish")

    def test_publish_blocks_incomplete_shared_content(self) -> None:
        bundle = load_content_bundle(self.root / "content")
        bundle["collections"]["board"] = [
            {"id": "new-board-member", "name": "", "role": "", "country": "", "image": "", "url": "", "officer": False}
        ]
        with self.assertRaisesRegex(ContentValidationError, "Consejo asesor"):
            self.workspace.publish(bundle, "test-token", "Should not publish")

    def test_publish_uses_temporary_worktree_and_pushes(self) -> None:
        remote = self.base / "remote.git"
        run("git", "clone", "--bare", str(self.root), str(remote), cwd=self.base)
        clone = self.base / "clone"
        run("git", "clone", "--branch", "gh-pages", str(remote), str(clone), cwd=self.base)
        run("git", "config", "user.name", "ISH Editor Tests", cwd=clone)
        run("git", "config", "user.email", "tests@example.test", cwd=clone)
        workspace = Workspace(clone)
        bundle = load_content_bundle(clone / "content")
        bundle["site"]["name"] = "Published by editor"
        workspace.save_draft(bundle, snapshot=True)

        fake_generator = [sys.executable, "-c", "print('validated fixture')"]
        with patch("editor.workspace.AUTHENTICATED_REPOSITORY_URL", str(remote)), patch(
            "editor.workspace._generator_command", return_value=fake_generator
        ):
            result = workspace.publish(bundle, "test-token", "Editor publication test")

        self.assertTrue(result["published"])
        remote_site = subprocess.run(
            ["git", f"--git-dir={remote}", "show", "gh-pages:content/site.json"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        self.assertIn("Published by editor", remote_site)
        message = subprocess.run(
            ["git", f"--git-dir={remote}", "log", "-1", "--format=%B", "gh-pages"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        self.assertIn("ISH-Editor: true", message)


class GeneratorIntegrationTests(unittest.TestCase):
    def test_internal_generator_builds_and_validates_preview(self) -> None:
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bundle = root / "bundle.json"
            output = root / "preview"
            bundle.write_text(
                __import__("json").dumps(load_content_bundle(project / "content")),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "editor.launcher",
                    "--internal-generate",
                    str(project),
                    str(output),
                    str(bundle),
                ],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "ich2026" / "abstracts-registration" / "index.html").is_file())
            self.assertTrue((output / "awards" / "index.html").is_file())

            registration = (output / "ich2026" / "abstracts-registration" / "index.html").read_text(
                encoding="utf-8"
            )
            awards = (output / "awards" / "index.html").read_text(encoding="utf-8")
            communications = (output / "communications" / "index.html").read_text(encoding="utf-8")
            venue = (output / "ich2026" / "venue" / "index.html").read_text(encoding="utf-8")
            self.assertIn("August 16, 2026", registration)
            self.assertIn("September 1, 2026", registration)
            self.assertIn("https://forms.gle/SqXDscDq8BuauHgP6", registration)
            self.assertIn("https://forms.gle/Ak6Bkg3GCUzKKMrw7", registration)
            self.assertIn("Connie S. Schmaljohn", awards)
            self.assertNotIn("Earlier conference materials list this lectureship as", awards)
            self.assertIn("https://who.zoom.us/j/95193938502", communications)
            self.assertIn('class="news-event-feature', communications)
            self.assertIn('id="hantavirus-corc-vaccine-working-group"', communications)
            self.assertIn('datetime="2026-09-10"', communications)
            self.assertIn("@Hanta!1", communications)
            self.assertIn('data-copy-text="@Hanta!1"', communications)
            self.assertIn("Copy Zoom password", communications)
            self.assertIn("CLP 22,500", venue)
            self.assertIn("Puerto Montt Airport (PMC) to Puerto Varas, and return.", venue)
            self.assertIn("Ground transfer", venue)
            self.assertNotIn("El Tepual Airport (PMC) to Puerto Varas, and return.", venue)
            self.assertIn("US$25", venue)
            self.assertIn("Minimum 2 passengers", venue)
            self.assertIn("CLP 253,000", venue)
            self.assertIn("CLP 328,000", venue)
            self.assertIn("CLP 110,000", venue)
            self.assertIn("CLP 99,900", venue)
            self.assertIn("CLP 80,000", venue)
            self.assertIn("reservas@hotelelgreco.cl", venue)
            self.assertNotIn("$80.000", venue)
            self.assertNotIn("CLP 394,000", venue)
            self.assertLess(venue.index("Radisson Hotel Puerto Varas"), venue.index("Hotel Cabaña del Lago"))
            self.assertLess(venue.index("Hotel Cabaña del Lago"), venue.index("Hotel Germania"))
            self.assertLess(venue.index("Hotel Germania"), venue.index("Hotel Weisserhaus"))
            self.assertLess(venue.index("Hotel Weisserhaus"), venue.index("El Greco Hotel Museo"))
            self.assertIn("A stay in Santiago is optional and is not required to reach ICH2026", venue)
            self.assertIn("not organized by, included in, or paid through ICH2026", venue)
            self.assertNotIn("{{conference.", registration)

    def test_internal_generator_allows_incomplete_draft_preview(self) -> None:
        project = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            bundle = root / "preview-bundle.json"
            output = root / "preview"
            content = load_content_bundle(project / "content")
            content["collections"]["board"].append(
                {"id": "new-board-member", "name": "", "role": "", "country": "", "image": "", "url": "", "officer": False}
            )
            bundle.write_text(__import__("json").dumps(content), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "editor.launcher",
                    "--internal-generate",
                    str(project),
                    str(output),
                    str(bundle),
                ],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertNotIn('src="assets/images/"', (output / "index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
