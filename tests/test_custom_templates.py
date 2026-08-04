from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from editor.app import PAGE_CATALOG
from scripts.content_store import load_content_bundle, validate_content_bundle


ROOT = Path(__file__).resolve().parents[1]


class CustomTemplateTests(unittest.TestCase):
    def test_every_page_template_generates_a_static_page(self) -> None:
        bundle = load_content_bundle()
        for index, template in enumerate(PAGE_CATALOG, start=1):
            route = f"template-test-{index}"
            sections = [
                {
                    "id": "hero",
                    "type": "page_hero",
                    "visible": True,
                    "locked": True,
                    "data": {
                        "eyebrow": "ISH",
                        "title": template["label"],
                        "lede": "Template test",
                        "image": "ui/social-preview.jpg",
                        "breadcrumbs": True,
                        "actions": [],
                    },
                }
            ]
            for section_index, template_section in enumerate(template["sections"], start=1):
                section = deepcopy(template_section)
                section.update(
                    {
                        "id": f'{section["type"]}-{section_index}',
                        "visible": True,
                    }
                )
                sections.append(section)
            bundle["pages"].append(
                {
                    "id": route,
                    "route": route,
                    "title": template["label"],
                    "description": template["description"],
                    "social_image": "ui/social-preview.jpg",
                    "hero_image": "ui/social-preview.jpg",
                    "conference_page": False,
                    "core_route": False,
                    "sections": sections,
                }
            )

        validate_content_bundle(bundle)
        with tempfile.TemporaryDirectory() as name:
            temporary = Path(name)
            output = temporary / "preview"
            bundle_path = temporary / "preview-bundle.json"
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(ROOT)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "editor.launcher",
                    "--internal-generate",
                    str(ROOT),
                    str(output),
                    str(bundle_path),
                ],
                cwd=ROOT,
                env=environment,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for index, template in enumerate(PAGE_CATALOG, start=1):
                generated = output / f"template-test-{index}" / "index.html"
                self.assertTrue(generated.exists())
                self.assertIn(template["label"], generated.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
