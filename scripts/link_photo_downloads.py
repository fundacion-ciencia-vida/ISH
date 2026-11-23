"""Match a Drive folder inventory to gallery photographs without changing previews."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

try:
    from .import_conference_photos import ALBUMS, ROOT
except ImportError:
    from import_conference_photos import ALBUMS, ROOT


def normalize_filename(name: str) -> str:
    return re.sub(r"^\d+\s+", "", name).casefold()


def match_downloads(albums: list[dict], inventory: list[dict]) -> tuple[list[dict], list[dict]]:
    folder_names = {album_id: folder for folder, album_id, *_ in ALBUMS}
    folders = {entry["folder"]["title"]: entry["files"] for entry in inventory}
    downloads, missing = [], []
    for album in albums:
        files = folders.get(folder_names.get(album["id"]), [])
        exact = {}
        aliases = {}
        for file in files:
            if not file.get("mime_type", "").startswith("image/") or file.get("can_download") is False:
                continue
            name = normalize_filename(file["title"])
            exact.setdefault(name, []).append(file)
            alias = re.sub(r"\s*\(1\)(?=\.[^.]+$)", "", name)
            aliases.setdefault(alias, []).append(file)
        for photo in album["photos"]:
            name = photo["source_filename"].casefold()
            candidates = exact.get(name) or aliases.get(name, [])
            if len(candidates) != 1:
                missing.append({"album": album["id"], "filename": photo["source_filename"]})
                continue
            file = candidates[0]
            downloads.append({"id": photo["id"], "url": file["url"],
                              "bytes": int(file["size"]), "drive_file_id": file["id"]})
    return downloads, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    albums = json.loads((ROOT / "content/collections/conference_photos.json").read_text())["items"]
    downloads, missing = match_downloads(albums, json.loads(args.inventory.read_text()))
    target = ROOT / "content/collections/photo_downloads.json"
    target.write_text(json.dumps({"items": downloads}, indent=2) + "\n")
    print(f"Linked {len(downloads)} HD photos. Unmatched photographs: {json.dumps(missing)}")


if __name__ == "__main__":
    main()
