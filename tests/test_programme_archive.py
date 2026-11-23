from pathlib import Path
import unittest

from scripts.content_store import load_content_bundle


ROOT = Path(__file__).resolve().parents[1]


class ProgrammeArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_content_bundle(ROOT / "content")
        cls.pages = {page["id"]: page for page in cls.bundle["pages"]}

    def test_workshop_has_its_own_route_and_navigation_after_programme(self):
        self.assertEqual(self.pages["workshop"]["route"], "ich2026/andv-workshop")
        nav = self.bundle["site"]["navigation"]
        items = [item["page_id"] for group in nav["groups"] if group["id"] == "conference" for item in group["items"]]
        self.assertEqual(items[items.index("programme") + 1], "workshop")
        self.assertEqual(nav["conference_subnav"][nav["conference_subnav"].index("programme") + 1], "workshop")

    def test_final_conference_agenda_matches_supplied_summary(self):
        agenda = next(section["data"] for section in self.pages["programme"]["sections"] if section["type"] == "programme_agenda")
        days = {day["day"]: day for day in agenda["days"]}
        self.assertNotIn("Thursday", days)
        self.assertEqual([event["time"] for event in days["Monday"]["events"]], ["08:45–10:56", "11:45–13:25", "14:45–18:44"])
        self.assertEqual(days["Tuesday"]["events"][1]["title"], "Pathogenesis")
        self.assertIn("16:50–17:45", [event["time"] for event in days["Wednesday"]["events"]])
        self.assertEqual(days["Sunday"]["events"][1]["time"], "19:00")

    def test_workshop_programme_is_public_and_unreleased_materials_have_no_buttons(self):
        workshop = self.pages["workshop"]
        urls = [action.get("url", "") for section in workshop["sections"] for action in section["data"].get("actions", [])]
        self.assertIn("assets/documents/ich2026/andv-workshop-programme.pdf", urls)
        self.assertIn("assets/documents/ich2026/andv-workshop-flyer-en.pdf", urls)
        self.assertIn("assets/images/ich2026/andv-workshop-flyer-es.png", urls)
        self.assertFalse(any("zoom.us" in url or ".ppt" in url for url in urls))
        for url in urls:
            if url.startswith("assets/"):
                self.assertTrue((ROOT / url).is_file())


if __name__ == "__main__":
    unittest.main()
