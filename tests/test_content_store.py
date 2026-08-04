from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from scripts.content_store import (
    ContentValidationError,
    load_content_bundle,
    normalize_content_bundle,
    sanitize_rich_html,
    validate_content_bundle,
    validate_publishable_content,
    write_content_bundle,
)
from tests.helpers import minimal_bundle


class ContentStoreTests(unittest.TestCase):
    def test_current_content_is_valid(self) -> None:
        validate_content_bundle(load_content_bundle())

    def test_round_trip_split_content(self) -> None:
        bundle = minimal_bundle()
        with tempfile.TemporaryDirectory() as name:
            root = Path(name) / "content"
            write_content_bundle(bundle, root)
            self.assertEqual(load_content_bundle(root), bundle)

    def test_rejects_unsafe_page_identifier(self) -> None:
        bundle = minimal_bundle()
        bundle["pages"][0]["id"] = "../outside"
        with self.assertRaises(ContentValidationError):
            validate_content_bundle(bundle)

    def test_rejects_unknown_navigation_page(self) -> None:
        bundle = minimal_bundle()
        bundle["site"]["navigation"]["groups"] = [
            {"id": "main", "label": "Main", "items": [{"page_id": "missing", "label": "Missing"}]}
        ]
        with self.assertRaises(ContentValidationError):
            validate_content_bundle(bundle)

    def test_rejects_script_link(self) -> None:
        bundle = minimal_bundle()
        bundle["site"]["links"]["registration"] = "javascript:alert(1)"
        with self.assertRaises(ContentValidationError):
            validate_content_bundle(bundle)

    def test_sanitizes_rich_html(self) -> None:
        raw = '<p onclick="bad()">Safe <strong>text</strong><script>alert(1)</script></p><a href="javascript:bad()">link</a>'
        clean = sanitize_rich_html(raw)
        self.assertNotIn("onclick", clean)
        self.assertNotIn("<script", clean)
        self.assertNotIn("alert(1)", clean)
        self.assertNotIn("javascript:", clean)
        self.assertIn("<strong>text</strong>", clean)

    def test_duplicate_route_is_rejected(self) -> None:
        bundle = minimal_bundle()
        duplicate = copy.deepcopy(bundle["pages"][0])
        duplicate["id"] = "second"
        bundle["pages"].append(duplicate)
        with self.assertRaises(ContentValidationError):
            validate_content_bundle(bundle)

    def test_incomplete_collection_item_is_valid_only_as_draft(self) -> None:
        bundle = load_content_bundle()
        bundle["collections"]["board"].append(
            {"id": "new-board-member", "name": "", "role": "", "country": "", "image": "", "url": "", "officer": False}
        )
        validate_content_bundle(bundle)
        with self.assertRaisesRegex(ContentValidationError, "Consejo asesor"):
            validate_publishable_content(bundle)

    def test_communications_receive_local_editor_defaults(self) -> None:
        bundle = load_content_bundle()
        bundle["collections"]["communications"].append(
            {
                "id": "normalized-news",
                "category": "News",
                "date": "August 4, 2026",
                "title": "Normalized communication",
                "description": "Test communication",
                "url": "https://example.test/news",
                "label": "Read more",
            }
        )
        normalize_content_bundle(bundle)
        item = bundle["collections"]["communications"][-1]
        self.assertTrue(item["published"])
        self.assertEqual(item["image"], "")
        self.assertEqual(item["image_alt"], "")
        self.assertEqual(item["body_html"], "")

    def test_unpublished_incomplete_communication_can_remain_as_draft(self) -> None:
        bundle = load_content_bundle()
        bundle["collections"]["communications"].append(
            {
                "id": "draft-news",
                "title": "",
                "url": "",
                "published": False,
                "image": "",
                "image_alt": "",
                "body_html": "",
            }
        )
        validate_publishable_content(bundle)

    def test_incomplete_communication_is_normalized_as_unpublished(self) -> None:
        bundle = load_content_bundle()
        bundle["collections"]["communications"].append(
            {"id": "new-draft", "title": "", "url": "", "published": True}
        )
        normalize_content_bundle(bundle)
        self.assertFalse(bundle["collections"]["communications"][-1]["published"])
        validate_publishable_content(bundle)


if __name__ == "__main__":
    unittest.main()
