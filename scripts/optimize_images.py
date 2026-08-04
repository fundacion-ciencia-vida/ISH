#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "assets" / "images"
OUTPUT_ROOT = SOURCE_ROOT / "optimized"
MANIFEST = OUTPUT_ROOT / "manifest.json"
SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
BUILD_SCRIPT = ROOT / "scripts" / "build_site.py"
CONTENT_ROOT = ROOT / "content"
DEFAULT_WIDTHS = (320, 480, 640, 960, 1280)
HERO_WIDTHS = (320, 480, 640, 960, 1280, 1600, 1920)
PROFILE_WIDTHS = (160, 240, 320, 480)
LOGO_WIDTHS = (120, 160, 240, 320)
SPONSOR_WIDTHS = (160, 240, 320, 480, 640)


def tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required image tool: {name}")
    return path


IDENTIFY = tool("identify")
CONVERT = tool("convert")


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def dimensions(path: Path) -> tuple[int, int]:
    output = run([IDENTIFY, "-format", "%w %h", str(path)])
    width, height = output.split()
    return int(width), int(height)


def quality_for(path: Path) -> str:
    parts = path.relative_to(SOURCE_ROOT).parts
    if parts[0] in {"board", "speakers"}:
        return "82"
    if parts[0] == "ich2026" and (parts[-1].startswith("local-") or parts[-1].startswith("scientific-")):
        return "82"
    if path.suffix.lower() == ".png":
        return "86"
    return "78"


def avif_quality_for(path: Path) -> str:
    parts = path.relative_to(SOURCE_ROOT).parts
    if parts[0] in {"board", "speakers"}:
        return "50"
    if parts[0] == "ich2026" and (parts[-1].startswith("local-") or parts[-1].startswith("scientific-")):
        return "50"
    if path.suffix.lower() == ".png":
        return "52"
    return "48"


def referenced_assets() -> set[str]:
    source_text = BUILD_SCRIPT.read_text(encoding="utf-8") if BUILD_SCRIPT.exists() else ""
    if CONTENT_ROOT.exists():
        source_text += "\n".join(
            path.read_text(encoding="utf-8") for path in CONTENT_ROOT.rglob("*.json")
        )
    return {
        str(path.relative_to(SOURCE_ROOT))
        for path in SOURCE_ROOT.rglob("*")
        if OUTPUT_ROOT not in path.parents
        and path.is_file()
        and path.suffix.lower() in SOURCE_EXTENSIONS
        and str(path.relative_to(SOURCE_ROOT)) in source_text
    }


def widths_for(source: Path) -> tuple[int, ...]:
    relative = str(source.relative_to(SOURCE_ROOT))
    parts = source.relative_to(SOURCE_ROOT).parts
    filename = parts[-1]

    if relative == "ui/logo.png":
        return LOGO_WIDTHS
    if parts[0] in {"board", "speakers"}:
        return PROFILE_WIDTHS
    if parts[0] == "ich2026" and (filename.startswith("local-") or filename.startswith("scientific-")):
        return PROFILE_WIDTHS
    if parts[0] == "sponsors":
        return SPONSOR_WIDTHS
    if parts[0] == "ui" and filename.startswith("home-hero-"):
        return HERO_WIDTHS
    if relative in {
        "about-hantavirus-microscopy-pixnio.jpg",
        "ui/home-science-hero.webp",
        "ich2026/conference-volcano.jpg",
        "venue/hotel-bellavista.jpg",
        "venue/conference-landscape.png",
        "venue/puerto-varas-waterfront.jpg",
        "ui/society-archive-1.png",
        "ui/society-archive-2.png",
    }:
        return HERO_WIDTHS
    return DEFAULT_WIDTHS


def candidate_widths(source: Path, source_width: int) -> list[int]:
    widths = [width for width in widths_for(source) if width <= source_width]
    if source_width <= max(HERO_WIDTHS):
        widths.append(source_width)
    return sorted(set(widths))


def source_images() -> list[Path]:
    used_assets = referenced_assets()
    images = []
    for path in SOURCE_ROOT.rglob("*"):
        if OUTPUT_ROOT in path.parents:
            continue
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS and str(path.relative_to(SOURCE_ROOT)) in used_assets:
            images.append(path)
    return sorted(images)


def optimized_path(source: Path, width: int, extension: str) -> Path:
    relative = source.relative_to(SOURCE_ROOT)
    stem = relative.with_suffix("")
    return OUTPUT_ROOT / stem.parent / f"{stem.name}-{width}.{extension}"


def convert_image(source: Path, width: int, extension: str) -> Path:
    target = optimized_path(source, width, extension)
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [CONVERT, str(source), "-auto-orient", "-strip", "-resize", f"{width}x>"]
    if extension == "avif":
        command += ["-quality", avif_quality_for(source)]
    else:
        command += ["-quality", quality_for(source), "-define", "webp:method=6"]
    command.append(str(target))
    run(command)
    return target


def main() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)

    manifest: dict[str, dict[str, object]] = {}
    original_total = 0
    optimized_total = 0
    variant_count = 0

    for source in source_images():
        source_width, source_height = dimensions(source)
        source_size = source.stat().st_size
        original_total += source_size
        formats: dict[str, list[dict[str, object]]] = {"avif": [], "webp": []}

        for width in candidate_widths(source, source_width):
            webp_target = None
            for extension in ("webp", "avif"):
                target = convert_image(source, width, extension)
                target_width, target_height = dimensions(target)
                target_size = target.stat().st_size

                if target_width >= source_width and target_size >= source_size:
                    target.unlink()
                    continue

                if extension == "avif" and webp_target is not None and target_size >= webp_target["bytes"]:
                    target.unlink()
                    continue

                entry = {
                    "width": target_width,
                    "height": target_height,
                    "bytes": target_size,
                    "path": str(target.relative_to(SOURCE_ROOT)),
                }
                if extension == "webp":
                    webp_target = entry

                optimized_total += target_size
                variant_count += 1
                formats[extension].append(entry)

        formats = {extension: variants for extension, variants in formats.items() if variants}
        if formats:
            relative_source = str(source.relative_to(SOURCE_ROOT))
            manifest[relative_source] = {
                "width": source_width,
                "height": source_height,
                "bytes": source_size,
                "formats": formats,
                "variants": formats.get("webp", []),
            }

    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    original_mb = original_total / 1024 / 1024
    optimized_mb = optimized_total / 1024 / 1024
    print(f"Optimized {len(manifest)} source images into {variant_count} AVIF/WebP variants.")
    print(f"Original source total: {original_mb:.2f} MB")
    print(f"Generated variants total: {optimized_mb:.2f} MB")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
