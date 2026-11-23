from html.parser import HTMLParser
from pathlib import Path
import unittest
from unittest.mock import patch

from PIL import Image

from scripts.content_store import load_content_bundle
from scripts import build_site
from scripts.import_conference_photos import preserve_editorial_order
from scripts.prepare_original_photos import prepare
from scripts.link_photo_downloads import match_downloads, numbered_photo_order


ROOT = Path(__file__).resolve().parents[1]


class GalleryParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tiles = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("class") == "photo-tile":
            self.tiles.append(values)


class ConferenceGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_content_bundle(ROOT / "content")
        cls.albums = cls.bundle["collections"]["conference_photos"]

    def test_all_eight_albums_and_unique_photos_are_retained(self):
        self.assertEqual([len(album["photos"]) for album in self.albums], [4, 18, 72, 49, 74, 92, 35, 89])
        ids = [photo["id"] for album in self.albums for photo in album["photos"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 433)
        for album in self.albums:
            if album.get("cover_id"):
                self.assertIn(album["cover_id"], [photo["id"] for photo in album["photos"]])

    def test_images_are_web_sized_and_do_not_expose_original_metadata(self):
        for album in self.albums:
            for photo in album["photos"]:
                for field, width, height, limit in (
                    ("image", "width", "height", 1920),
                    ("thumbnail", "thumbnail_width", "thumbnail_height", 640),
                ):
                    path = ROOT / "assets/images" / photo[field]
                    with self.subTest(path=path), Image.open(path) as image:
                        self.assertEqual(image.format, "WEBP")
                        self.assertEqual(image.size, (photo[width], photo[height]))
                        self.assertLessEqual(max(image.size), limit)
                        self.assertFalse(image.getexif())
                        self.assertNotIn("xmp", image.info)

    def test_all_photos_are_in_the_viewer_but_only_first_batch_is_visible(self):
        section = {"id": "albums", "type": "photo_albums", "data": {"collection": "conference_photos"}}
        parser = GalleryParser(build_site.render_photo_albums("../../", section))
        self.assertEqual(len(parser.tiles), 433)
        self.assertEqual(sum("hidden" not in tile for tile in parser.tiles), 88)
        self.assertEqual(len({tile["data-lightbox-group"] for tile in parser.tiles}), 8)
        self.assertTrue(all(tile["href"] == tile["data-lightbox-src"] for tile in parser.tiles))

    def test_home_is_an_archive_entry_not_a_countdown(self):
        home = next(page for page in self.bundle["pages"] if page["id"] == "home")
        html = build_site.render_home_hero("", home["sections"][0])
        self.assertNotIn("data-countdown", html)
        self.assertIn('href="former-meetings/ich2026/"', html)
        self.assertIn("Conference memories", html)
        self.assertNotIn('href="ich2026/abstracts-registration/"', html)

    def test_workshop_uses_nicoles_numbered_order_without_losing_photos(self):
        album = next(album for album in self.albums if album["id"] == "andv-workshop")
        self.assertEqual([photo["source_filename"] for photo in album["photos"][:3]], ["Andes_Virus_Workshop-05-11-57.jpg", "DSC_6581.JPG", "DSC_6585.JPG"])
        self.assertEqual(album["photos"][-1]["source_filename"], "DSC_6711.JPG")
        self.assertEqual(len(album["photos"]), 89)

    def test_numbered_order_is_stable_and_keeps_unmatched_photos(self):
        photos = [{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "missing"}]
        files = [{"id": "fa", "title": "7 a.jpg"}, {"id": "fb", "title": "1 b.jpg"}, {"id": "fc", "title": "7 c.jpg"}]
        links = [{"id": item, "drive_file_id": "f" + item} for item in ("a", "b", "c")]
        self.assertEqual([photo["id"] for photo in numbered_photo_order(photos, files, links)], ["b", "a", "c", "missing"])

    def test_reimport_preserves_custom_order_cover_and_appends_new_photos(self):
        previous = [{"id": "album", "cover_id": "b", "photos": [{"id": "b"}, {"id": "a"}]}]
        albums = [{"id": "album", "photos": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}]
        preserve_editorial_order(albums, previous)
        self.assertEqual([photo["id"] for photo in albums[0]["photos"]], ["b", "a", "c"])
        self.assertEqual(albums[0]["cover_id"], "b")

    def test_full_resolution_files_cannot_be_exported_into_the_repository(self):
        with self.assertRaisesRegex(ValueError, "outside the Git"):
            prepare([], ROOT / "assets/images/originals", "exiftool")

    def test_original_download_is_separate_from_the_fast_preview(self):
        photo = self.albums[0]["photos"][0]
        downloads = [{"id": photo["id"], "url": "https://drive.google.com/file/d/test-photo/view",
                      "width": 5568, "height": 3712, "bytes": 12_000_000}]
        section = {"id": "albums", "type": "photo_albums", "data": {"collection": "conference_photos"}}
        with patch.dict(build_site.COLLECTIONS, {"photo_downloads": downloads}):
            parser = GalleryParser(build_site.render_photo_albums("../../", section))
        self.assertEqual(parser.tiles[0]["data-lightbox-download"], downloads[0]["url"])
        self.assertIn("5,568 × 3,712 px", parser.tiles[0]["data-lightbox-download-info"])
        self.assertTrue(parser.tiles[0]["data-lightbox-src"].endswith(".webp"))
        self.assertNotIn("data-lightbox-download", parser.tiles[1])
        downloads[0]["url"] = "javascript:alert(1)"
        with patch.dict(build_site.COLLECTIONS, {"photo_downloads": downloads}):
            parser = GalleryParser(build_site.render_photo_albums("../../", section))
        self.assertNotIn("data-lightbox-download", parser.tiles[0])

    def test_hd_links_support_verified_file_sizes_without_assuming_dimensions(self):
        photo = self.albums[0]["photos"][0]
        downloads = [{"id": photo["id"], "url": "https://drive.google.com/file/d/test-photo/view", "bytes": 12_000_000}]
        section = {"id": "albums", "type": "photo_albums", "data": {"collection": "conference_photos"}}
        with patch.dict(build_site.COLLECTIONS, {"photo_downloads": downloads}):
            parser = GalleryParser(build_site.render_photo_albums("../../", section))
        self.assertEqual(parser.tiles[0]["data-lightbox-download-info"], "HD · 12.0 MB")

    def test_hd_matching_uses_file_names_not_workshop_photo_numbers(self):
        albums = [{"id": "andv-workshop", "photos": [
            {"id": "opening", "source_filename": "DSC_6581.JPG"},
            {"id": "renamed", "source_filename": "DSC_6141.JPG"},
            {"id": "missing", "source_filename": "DSC_6711.JPG"},
        ]}]
        def file(name, identifier):
            return {"title": name, "id": identifier, "url": f"https://drive.google.com/file/d/{identifier}/view", "size": "10000000", "mime_type": "image/jpeg"}
        inventory = [{"folder": {"title": "Nov 05 ANDV Workshop"}, "files": [
            file("37 ANDV Workshop.png", "different-photo"),
            file("2 DSC_6581.JPG", "correct-photo"),
            file("DSC_6141 (1).JPG", "renamed-photo"),
        ]}]
        downloads, missing = match_downloads(albums, inventory)
        self.assertEqual([item["drive_file_id"] for item in downloads], ["correct-photo", "renamed-photo"])
        self.assertEqual(missing, [{"album": "andv-workshop", "filename": "DSC_6711.JPG"}])

    def test_hd_entries_are_unique_and_do_not_replace_preview_assets(self):
        downloads = self.bundle["collections"]["photo_downloads"]
        photos = {photo["id"]: photo for album in self.albums for photo in album["photos"]}
        self.assertEqual(len(downloads), len({item["id"] for item in downloads}))
        for item in downloads:
            self.assertIn(item["id"], photos)
            self.assertTrue(item["url"].startswith("https://drive.google.com/file/d/"))
            self.assertGreater(item["bytes"], 0)
            self.assertTrue(photos[item["id"]]["image"].endswith(".webp"))

    def test_former_meetings_has_one_completed_2026_entry(self):
        timeline = build_site.former_meetings_timeline("")
        self.assertEqual(timeline.count('datetime="2026"'), 1)
        self.assertNotIn("Next ICH", timeline)
        self.assertIn('href="former-meetings/ich2026/"', timeline)


if __name__ == "__main__":
    unittest.main()
