from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.content_store import write_content_bundle


def minimal_bundle() -> dict:
    return {
        "schema_version": 1,
        "site": {
            "name": "ISH Test",
            "language": "en",
            "public_url": "https://example.test",
            "links": {"registration": "https://example.test/register"},
            "navigation": {"groups": [], "conference_subnav": []},
        },
        "collections": {},
        "pages": [
            {
                "id": "home",
                "route": "",
                "title": "Home",
                "description": "Test home",
                "social_image": "test.png",
                "hero_image": "test.png",
                "conference_page": False,
                "core_route": True,
                "sections": [
                    {
                        "id": "intro",
                        "type": "rich_text",
                        "visible": True,
                        "data": {"heading": "Welcome", "body_html": "<p>Hello</p>"},
                    }
                ],
            }
        ],
    }


def run(*command: str, cwd: Path) -> str:
    return subprocess.run(
        list(command),
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.strip()


def create_seed_repository(root: Path) -> Path:
    root.mkdir(parents=True)
    write_content_bundle(minimal_bundle(), root / "content")
    (root / "scripts").mkdir()
    (root / "scripts" / "build_site.py").write_text("print('fixture')\n", encoding="utf-8")
    (root / "assets" / "images").mkdir(parents=True)
    (root / "assets" / "images" / "test.png").write_bytes(b"fixture")
    for relative in ("index.html", "sitemap.xml", "styles.min.css", "fonts.min.css", "script.min.js"):
        (root / relative).write_text(f"fixture {relative}\n", encoding="utf-8")
    (root / ".gitignore").write_text(".ish-editor/\n", encoding="utf-8")
    run("git", "init", "-b", "gh-pages", cwd=root)
    run("git", "config", "user.name", "ISH Editor Tests", cwd=root)
    run("git", "config", "user.email", "tests@example.test", cwd=root)
    run("git", "add", ".", cwd=root)
    run("git", "commit", "-m", "Initial fixture", cwd=root)
    return root
