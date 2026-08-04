from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from editor.app import create_app
from tests.helpers import create_seed_repository


class EditorApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = create_seed_repository(Path(self.temporary.name) / "workspace")
        self.session = "test-session-token"
        self.auth_path = Path(self.temporary.name) / "auth.json"
        self.client = TestClient(
            create_app(
                workspace_path=self.root,
                session_token=self.session,
                auth_path=self.auth_path,
                ui_root=Path(self.temporary.name) / "missing-ui",
            )
        )
        setup = self.client.post(
            "/api/auth/setup",
            headers={"X-ISH-Setup": self.session},
            json={"username": "editor", "password": "local-password-2026"},
        )
        self.assertEqual(setup.status_code, 200, setup.text)

    def tearDown(self) -> None:
        self.client.close()
        self.temporary.cleanup()

    def test_api_requires_local_session(self) -> None:
        self.assertEqual(self.client.get("/api/bootstrap").status_code, 200)
        self.client.cookies.clear()
        self.assertEqual(self.client.get("/api/bootstrap").status_code, 401)
        denied = self.client.post("/api/auth/login", json={"username": "editor", "password": "incorrect-password"})
        self.assertEqual(denied.status_code, 401)
        login = self.client.post("/api/auth/login", json={"username": "editor", "password": "local-password-2026"})
        self.assertEqual(login.status_code, 200)
        self.assertEqual(self.client.get("/api/bootstrap").status_code, 200)

    def test_local_password_is_stored_as_hash(self) -> None:
        payload = json.loads(self.auth_path.read_text(encoding="utf-8"))
        self.assertNotIn("local-password-2026", self.auth_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["username"], "editor")
        self.assertIn("password_hash", payload)

    def test_local_password_can_be_changed_without_online_service(self) -> None:
        changed = self.client.post(
            "/api/auth/password",
            json={"current_password": "local-password-2026", "new_password": "replacement-password-2026"},
        )
        self.assertEqual(changed.status_code, 200, changed.text)
        self.client.post("/api/auth/logout")
        old_login = self.client.post(
            "/api/auth/login",
            json={"username": "editor", "password": "local-password-2026"},
        )
        self.assertEqual(old_login.status_code, 401)
        new_login = self.client.post(
            "/api/auth/login",
            json={"username": "editor", "password": "replacement-password-2026"},
        )
        self.assertEqual(new_login.status_code, 200, new_login.text)

    def test_repeated_login_failures_are_rate_limited(self) -> None:
        self.client.cookies.clear()
        for _ in range(4):
            response = self.client.post(
                "/api/auth/login",
                json={"username": "editor", "password": "incorrect-password"},
            )
            self.assertEqual(response.status_code, 401)
        limited = self.client.post(
            "/api/auth/login",
            json={"username": "editor", "password": "incorrect-password"},
        )
        self.assertEqual(limited.status_code, 429)
        self.assertIn("Retry-After", limited.headers)

    def test_preview_requires_local_session(self) -> None:
        self.client.cookies.clear()
        self.assertEqual(self.client.get("/preview/").status_code, 401)

    def test_basic_edition_separates_structural_catalogs(self) -> None:
        with patch.dict("os.environ", {"ISH_EDITOR_EDITION": "basic", "ISH_EDITOR_SCOPE": "base"}):
            payload = self.client.get("/api/bootstrap").json()
        self.assertEqual(payload["edition"]["id"], "basic")
        self.assertTrue(payload["edition"]["show_distinction"])
        self.assertFalse(payload["features"]["custom_site"])
        self.assertEqual(payload["page_catalog"], [])
        self.assertEqual(payload["section_catalog"], [])
        self.assertEqual(len(payload["edition_catalog"]), 2)

    def test_advanced_edition_exposes_page_and_section_templates(self) -> None:
        with patch.dict("os.environ", {"ISH_EDITOR_EDITION": "advanced", "ISH_EDITOR_SCOPE": "base"}):
            payload = self.client.get("/api/bootstrap").json()
        self.assertEqual(payload["edition"]["id"], "advanced")
        self.assertTrue(payload["edition"]["show_distinction"])
        self.assertTrue(payload["features"]["custom_site"])
        self.assertGreaterEqual(len(payload["page_catalog"]), 3)
        self.assertGreaterEqual(len(payload["section_catalog"]), 3)

    def test_unified_edition_hides_commercial_distinction(self) -> None:
        with patch.dict("os.environ", {"ISH_EDITOR_EDITION": "unified", "ISH_EDITOR_SCOPE": "base"}):
            payload = self.client.get("/api/bootstrap").json()
        self.assertEqual(payload["edition"]["id"], "unified")
        self.assertFalse(payload["edition"]["show_distinction"])
        self.assertTrue(payload["features"]["custom_site"])
        self.assertEqual(payload["edition_catalog"], [])
        self.assertGreaterEqual(len(payload["page_catalog"]), 3)

    def test_draft_html_is_sanitized(self) -> None:
        response = self.client.get("/api/content")
        bundle = response.json()["bundle"]
        bundle["pages"][0]["sections"][0]["data"]["body_html"] = '<p onclick="bad()">Hello<script>bad()</script></p>'
        saved = self.client.put(
            "/api/draft",
            json={"bundle": bundle, "snapshot": True},
        )
        self.assertEqual(saved.status_code, 200)
        restored = self.client.get("/api/content").json()["bundle"]
        body = restored["pages"][0]["sections"][0]["data"]["body_html"]
        self.assertNotIn("onclick", body)
        self.assertNotIn("<script", body)
        self.assertIn("Hello", body)

    def test_path_traversal_media_delete_is_blocked(self) -> None:
        response = self.client.delete("/api/media/..%2F.git%2Fconfig")
        self.assertIn(response.status_code, {404, 409})


if __name__ == "__main__":
    unittest.main()
