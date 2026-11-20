#!/usr/bin/env python3
"""Prepare full-resolution JPEG downloads outside Git without recompressing pixels."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import zipfile

from PIL import Image

try:
    from .import_conference_photos import ALBUMS, ROOT
except ImportError:
    from import_conference_photos import ALBUMS, ROOT


def prepare(archives: list[Path], output: Path, exiftool: str) -> None:
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("Original downloads must remain outside the Git repository.")
    output.mkdir(parents=True, exist_ok=True)
    bundle = json.loads((ROOT / "content/collections/conference_photos.json").read_text(encoding="utf-8"))
    folders = {album_id: folder for folder, album_id, *_ in ALBUMS}
    sources = {}
    for archive_path in archives:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                sources.setdefault(info.filename, archive_path)
    manifest = []
    for album in bundle["items"]:
        folder = output / album["id"]
        folder.mkdir(exist_ok=True)
        expected = []
        for photo in album["photos"]:
            entry = f"All_selected/{folders[album['id']]}/{photo['source_filename']}"
            target = folder / (photo["id"] + ".jpg")
            with zipfile.ZipFile(sources[entry]) as archive:
                target.write_bytes(archive.read(entry))
            with Image.open(target) as image:
                width, height = image.size
                orientation = image.getexif().get(274, 1)
                if orientation in {5, 6, 7, 8}:
                    width, height = height, width
                colour_profile = image.info.get("icc_profile")
            expected.append((photo, target, width, height, orientation, colour_profile))
        # ExifTool rewrites metadata only; preserve orientation and the colour profile.
        subprocess.run([exiftool, "-overwrite_original", "-all=", "--ICC_Profile:all", "-tagsFromFile", "@",
                        "-Orientation", "-ColorSpace", str(folder)], check=True)
        for photo, target, width, height, orientation, colour_profile in expected:
            with Image.open(target) as image:
                if (image.getexif().get(34853) or image.getexif().get(274, 1) != orientation
                        or image.info.get("icc_profile") != colour_profile):
                    raise ValueError(f"Metadata verification failed: {target}")
            manifest.append({"id": photo["id"], "album_id": album["id"], "path": str(target),
                             "filename": target.name, "source_filename": photo["source_filename"],
                             "width": width, "height": height, "bytes": target.stat().st_size})
        print(f"Prepared {len(expected)} full-resolution photos: {album['title']}", flush=True)
    output.with_name(output.name + ".manifest.json").write_text(
        json.dumps({"photos": manifest}, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--exiftool", default="exiftool")
    args = parser.parse_args()
    prepare(args.archives, args.output, args.exiftool)


if __name__ == "__main__":
    main()
