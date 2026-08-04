#!/usr/bin/env python3
from __future__ import annotations

import os
from html.parser import HTMLParser
from pathlib import Path

try:
    from .content_store import ContentValidationError, load_content_bundle
except ImportError:
    from content_store import ContentValidationError, load_content_bundle


SOURCE_ROOT = Path(os.environ.get("ISH_SOURCE_ROOT", Path(__file__).resolve().parents[1])).resolve()
ROOT = Path(os.environ.get("ISH_OUTPUT_ROOT", SOURCE_ROOT)).resolve()


class SiteParser(HTMLParser):
    def __init__(self, html_path: Path) -> None:
        super().__init__()
        self.html_path = html_path
        self.base = html_path.parent
        self.assets: list[str] = []
        self.images: list[dict[str, str]] = []
        self.sources: list[dict[str, str]] = []
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.external_runtime_hosts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "img":
            self.images.append(values)
            self._asset(values.get("src", ""))
        elif tag == "source":
            self.sources.append(values)
            for item in values.get("srcset", "").split(","):
                src = item.strip().split(" ")[0]
                self._asset(src)
        elif tag == "link":
            href = values.get("href", "")
            rel = values.get("rel", "")
            if rel == "stylesheet":
                self.stylesheets.append(href)
            if href.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com")):
                self.external_runtime_hosts.append(href)
            if href and not href.startswith(("http:", "https:")):
                self._asset(href.split("?", 1)[0])
        elif tag == "script":
            src = values.get("src", "")
            if src:
                self.scripts.append(src)
                self._asset(src.split("?", 1)[0])

    def _asset(self, src: str) -> None:
        if not src or src.startswith(("http:", "https:", "mailto:", "tel:", "#")):
            return
        self.assets.append(src.split("?", 1)[0])


def html_files() -> list[Path]:
    bundle = load_content_bundle()
    files = []
    for page in bundle["pages"]:
        route = str(page.get("route", "")).strip("/")
        files.append(ROOT / route / "index.html" if route else ROOT / "index.html")
    return sorted(files)


def validate() -> list[str]:
    errors: list[str] = []
    source_types = {"image/avif": 0, "image/webp": 0}

    try:
        load_content_bundle()
    except ContentValidationError as exc:
        errors.append(f"Content validation failed: {exc}")

    for html in html_files():
        if not html.exists():
            errors.append(f"Generated page is missing: {html.relative_to(ROOT)}")
            continue
        parser = SiteParser(html)
        parser.feed(html.read_text(encoding="utf-8"))

        for asset in parser.assets:
            output_asset = (parser.base / asset).resolve()
            try:
                source_asset = SOURCE_ROOT / output_asset.relative_to(ROOT)
            except ValueError:
                source_asset = output_asset
            if not output_asset.exists() and not source_asset.exists():
                errors.append(f"{html.relative_to(ROOT)} references missing asset: {asset}")

        for image in parser.images:
            src = image.get("src", "")
            if "width" not in image or "height" not in image:
                errors.append(f"{html.relative_to(ROOT)} image lacks width/height: {src}")
            if not image.get("alt") and image.get("aria-hidden") != "true":
                errors.append(f"{html.relative_to(ROOT)} non-decorative image lacks alt: {src}")

        for source in parser.sources:
            source_type = source.get("type", "")
            if source_type in source_types:
                source_types[source_type] += 1
            if not source.get("srcset"):
                errors.append(f"{html.relative_to(ROOT)} source lacks srcset")

        if not any("styles.min.css?v=" in href for href in parser.stylesheets):
            errors.append(f"{html.relative_to(ROOT)} does not link versioned styles.min.css")
        if not any("fonts.min.css?v=" in href for href in parser.stylesheets):
            errors.append(f"{html.relative_to(ROOT)} does not link versioned fonts.min.css")
        if not any("script.min.js?v=" in src for src in parser.scripts):
            errors.append(f"{html.relative_to(ROOT)} does not link versioned script.min.js")
        if parser.external_runtime_hosts:
            errors.append(f"{html.relative_to(ROOT)} links external font runtime hosts")

    styles = (SOURCE_ROOT / "styles.css").read_text(encoding="utf-8")
    if ".responsive-image {\n  display: contents;" in styles:
        errors.append("styles.css regressed responsive-image to display: contents")
    if not (ROOT / "styles.min.css").exists():
        errors.append("styles.min.css is missing")
    if not (ROOT / "script.min.js").exists():
        errors.append("script.min.js is missing")
    if not (ROOT / "fonts.min.css").exists():
        errors.append("fonts.min.css is missing")
    if source_types["image/avif"] == 0:
        errors.append("No AVIF sources found in generated HTML")
    if source_types["image/webp"] == 0:
        errors.append("No WebP sources found in generated HTML")

    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Site validation passed.")


if __name__ == "__main__":
    main()
