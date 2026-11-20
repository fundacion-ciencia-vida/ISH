#!/usr/bin/env python3
"""Import the selected ICH2026 ZIPs as web-sized albums, without retaining originals."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ALBUMS = [
    ("Group Pictures", "group-pictures", "Group Pictures", "November 2026"),
    ("Nov 01 Opening Event", "opening-event", "Opening Event", "November 1"),
    ("Nov 02 ICH2026 day 1", "scientific-day-1", "Scientific Meeting · Day 1", "November 2"),
    ("Nov 03 ICH2026 day 2", "scientific-day-2", "Scientific Meeting · Day 2", "November 3"),
    ("Nov 03 Excursion Petrohue & Todos los Santos", "excursion", "Petrohué & Todos los Santos", "November 3"),
    ("Nov 04 ICH2026 day 3", "scientific-day-3", "Scientific Meeting · Day 3", "November 4"),
    ("Nov 04 ICH2026 Closing Dinner", "closing-dinner", "Closing Dinner", "November 4"),
    ("Nov 05 ANDV Workshop", "andv-workshop", "ANDV Workshop", "November 5"),
]


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def convert_photo(job: tuple[Path, str, int, str]) -> dict[str, object]:
    archive_path, name, crc, album_id = job
    stem = re.sub(r"[^a-z0-9]+", "-", Path(name).stem.lower()).strip("-")
    photo_id = f"{stem}-{crc:08x}"
    relative = Path("former-meetings/ich2026") / album_id
    folder = ROOT / "assets/images" / relative
    folder.mkdir(parents=True, exist_ok=True)
    full = folder / f"{photo_id}.webp"
    thumb = folder / f"{photo_id}-thumb.webp"
    if not full.exists() or not thumb.exists():
        with tempfile.TemporaryDirectory(prefix="ich2026-photo-") as temporary:
            source = Path(temporary) / ("source" + Path(name).suffix.lower())
            with zipfile.ZipFile(archive_path) as archive:
                source.write_bytes(archive.read(name))
            run("convert", str(source), "-auto-orient", "-colorspace", "sRGB", "-strip",
                "-resize", "1920x1920>", "-quality", "84", "-define", "webp:method=4", str(full))
            run("convert", str(full), "-strip", "-resize", "640x640>", "-quality", "80", str(thumb))
    width, height = map(int, run("identify", "-format", "%w %h", str(full)).split())
    thumb_width, thumb_height = map(int, run("identify", "-format", "%w %h", str(thumb)).split())
    return {"id": photo_id, "image": str(relative / full.name), "thumbnail": str(relative / thumb.name),
            "width": width, "height": height, "thumbnail_width": thumb_width,
            "thumbnail_height": thumb_height, "source_filename": Path(name).name}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    sources = {folder: [] for folder, *_ in ALBUMS}
    seen: dict[tuple[int, int], tuple[Path, str]] = {}
    for archive_path in sorted(args.archives):
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                parts = Path(info.filename).parts
                if info.is_dir() or Path(info.filename).suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                if len(parts) != 3 or parts[1] not in sources:
                    raise ValueError(f"Unexpected photo folder: {info.filename}")
                key = (info.CRC, info.file_size)
                if key in seen:
                    previous_path, previous_name = seen[key]
                    with zipfile.ZipFile(previous_path) as previous:
                        if archive.read(info.filename) == previous.read(previous_name):
                            print(f"Skipping exact duplicate: {info.filename}", flush=True)
                            continue
                seen[key] = (archive_path, info.filename)
                sources[parts[1]].append((archive_path, info.filename, info.CRC))
    albums = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for folder, album_id, title, date in ALBUMS:
            jobs = [(path, name, crc, album_id) for path, name, crc in sorted(sources[folder], key=lambda item: item[1].lower())]
            photos = list(executor.map(convert_photo, jobs))
            albums.append({"id": album_id, "title": title, "date": date, "photos": photos})
            print(f"{title}: {len(photos)} photos", flush=True)
    target = ROOT / "content/collections/conference_photos.json"
    previous = json.loads(target.read_text(encoding="utf-8")).get("items", []) if target.exists() else []
    preserve_editorial_order(albums, previous)
    target.write_text(json.dumps({"items": albums}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Imported {sum(len(album['photos']) for album in albums)} photos into {target}")
    update_manifest(albums)


def preserve_editorial_order(albums: list[dict[str, object]], previous: list[dict[str, object]]) -> None:
    previous_lookup = {album["id"]: album for album in previous}
    for album in albums:
        old = previous_lookup.get(album["id"], {})
        if any(photo["id"] == old.get("cover_id") for photo in album["photos"]):
            album["cover_id"] = old["cover_id"]
        order = {photo["id"]: index for index, photo in enumerate(old.get("photos", []))}
        album["photos"].sort(key=lambda photo: order.get(photo["id"], len(order)))


def update_manifest(albums: list[dict[str, object]]) -> None:
    manifest_path = ROOT / "assets/images/optimized/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for album in albums:
        for photo in album["photos"]:
            full = ROOT / "assets/images" / photo["image"]
            thumb = ROOT / "assets/images" / photo["thumbnail"]
            variants = [
                {"path": photo["thumbnail"], "width": photo["thumbnail_width"],
                 "height": photo["thumbnail_height"], "bytes": thumb.stat().st_size},
                {"path": photo["image"], "width": photo["width"],
                 "height": photo["height"], "bytes": full.stat().st_size},
            ]
            manifest[photo["image"]] = {"width": photo["width"], "height": photo["height"],
                "bytes": full.stat().st_size, "formats": {"webp": variants}, "variants": variants}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
