from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from editor.config import custom_site_enabled, editor_edition, editor_edition_catalog, editor_edition_id


class EditorEditionTests(unittest.TestCase):
    def edition_environment(self, edition: str = "", legacy_scope: str = "base"):
        return patch.dict(
            os.environ,
            {"ISH_EDITOR_EDITION": edition, "ISH_EDITOR_SCOPE": legacy_scope},
            clear=False,
        )

    def test_basic_is_the_default_delivery(self) -> None:
        with self.edition_environment(), patch("editor.config.load_config", return_value={}):
            self.assertEqual(editor_edition_id(), "basic")
            self.assertFalse(custom_site_enabled())
            self.assertTrue(editor_edition()["show_distinction"])
            self.assertEqual(len(editor_edition_catalog()), 2)

    def test_advanced_enables_structural_features(self) -> None:
        with self.edition_environment("advanced"):
            self.assertEqual(editor_edition_id(), "advanced")
            self.assertTrue(custom_site_enabled())
            self.assertTrue(editor_edition()["show_distinction"])

    def test_unified_enables_everything_without_package_labels(self) -> None:
        with self.edition_environment("unified"):
            self.assertTrue(custom_site_enabled())
            self.assertFalse(editor_edition()["show_distinction"])
            self.assertEqual(editor_edition_catalog(), [])

    def test_legacy_custom_scope_maps_to_advanced(self) -> None:
        with self.edition_environment("", "custom"), patch("editor.config.load_config", return_value={}):
            self.assertEqual(editor_edition_id(), "advanced")

    def test_saved_edition_is_used_without_environment_override(self) -> None:
        with self.edition_environment(), patch("editor.config.load_config", return_value={"edition": "unified"}):
            self.assertEqual(editor_edition_id(), "unified")


if __name__ == "__main__":
    unittest.main()
