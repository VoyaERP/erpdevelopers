from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestBrandContract(unittest.TestCase):
    def test_brand_words(self):
        template = (ROOT / "erpdevelopers/www/index.html").read_text(encoding="utf-8")
        for word in ("Engage.", "Reason.", "Progress.", "Developers", "AI"):
            self.assertIn(word, template)

    def test_no_active_integrations_claimed(self):
        template = (ROOT / "erpdevelopers/www/index.html").read_text(encoding="utf-8")
        self.assertIn("Planned module", template)
        self.assertIn("not active on this preview site", template)

    def test_version_boundary(self):
        config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('frappe = ">=16.0.0,<17.0.0"', config)


if __name__ == "__main__":
    unittest.main()
