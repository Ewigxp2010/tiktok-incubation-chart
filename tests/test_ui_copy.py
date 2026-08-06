import unittest

from ui_copy import ENHANCEMENT_TEXT


class EnhancementCopyTests(unittest.TestCase):
    def test_all_languages_have_the_same_keys(self):
        expected = set(ENHANCEMENT_TEXT["en"])
        self.assertEqual(set(ENHANCEMENT_TEXT), {"en", "zh", "de", "nl"})
        for language, copy in ENHANCEMENT_TEXT.items():
            self.assertEqual(set(copy), expected, language)
            self.assertTrue(all(str(value).strip() for value in copy.values()), language)


if __name__ == "__main__":
    unittest.main()
