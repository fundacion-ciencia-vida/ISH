from html.parser import HTMLParser
from pathlib import Path
import unittest

from PIL import Image

from scripts.content_store import load_content_bundle
from scripts import build_site


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

    def test_former_meetings_has_one_completed_2026_entry(self):
        timeline = build_site.former_meetings_timeline("")
        self.assertEqual(timeline.count('datetime="2026"'), 1)
        self.assertNotIn("Next ICH", timeline)
        self.assertIn('href="former-meetings/ich2026/"', timeline)


if __name__ == "__main__":
    unittest.main()
