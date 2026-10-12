import unittest
from utils import clean_text, word_count, compression_percent


class TestTextUtilities(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("  News\n\tarticle  "), "News article")

    def test_word_count(self):
        self.assertEqual(word_count("one two three"), 3)
        self.assertEqual(word_count("  "), 0)

    def test_compression_percent(self):
        self.assertEqual(compression_percent("one two three four", "one two"), 50.0)
        self.assertEqual(compression_percent("", "summary"), 0.0)


if __name__ == "__main__":
    unittest.main()
