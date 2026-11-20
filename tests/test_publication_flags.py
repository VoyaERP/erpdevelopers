"""Boolean and integer Check values must enforce the same editorial gate."""
from unittest import TestCase
from erpdevelopers.publications import normalize_publication, TOPICS


class TestPublicationCheckValues(TestCase):
    def base(self):
        return {"publication_type": "Project", "topic": TOPICS[0], "title": "Story",
                "summary": "Reviewed summary", "content": "Reviewed content"}

    def test_all_native_true_values_require_review(self):
        for enabled in (True, 1, "1"):
            for disabled in (False, 0, "0", None, ""):
                data = dict(self.base(), published=enabled, public_reviewed=disabled)
                with self.subTest(published=enabled, review=disabled), self.assertRaisesRegex(ValueError, "Review"):
                    normalize_publication(data)

    def test_all_native_true_review_values_are_accepted(self):
        for enabled in (True, 1, "1"):
            self.assertTrue(normalize_publication(dict(self.base(), published=enabled, public_reviewed=enabled)))

    def test_boolean_advice_still_requires_author(self):
        data = dict(self.base(), publication_type="Team Advice", published=True, public_reviewed=True)
        with self.assertRaisesRegex(ValueError, "author"):
            normalize_publication(data)
