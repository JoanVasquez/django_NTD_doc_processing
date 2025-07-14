# 🧹 Unit Tests: Text Preprocessing (clean_text function)

import logging
from unittest import TestCase
from unittest.mock import patch

from documents.preprocessing import clean_text


class TextPreprocessingTest(TestCase):
    """
    🧹 Unit Tests:
    Covers Unicode normalization, space reduction, lowercasing, and special cases.
    """

    @patch("documents.preprocessing.logger")
    def test_clean_text_basic_flow(self, mock_logger):
        """
        ✅ Ensure basic Unicode normalization, space reduction, and lowercasing.
        Also validates logger messages.
        """
        raw_text = "Thís is   á  TéSt\n\nString."
        expected = "this is a test string."

        result = clean_text(raw_text)
        self.assertEqual(result, expected)

        mock_logger.debug.assert_any_call(f"🛠️ Starting text cleaning. Original length: {len(raw_text)} characters.")
        mock_logger.debug.assert_any_call(f"✅ Text cleaned. Final length: {len(result)} characters.")


    def test_clean_text_removes_non_ascii(self):
        """
        🛑 Ensure accents are removed and characters normalized to ASCII.
        """
        raw_text = "Café naïve résumé"
        result = clean_text(raw_text)
        self.assertEqual(result, "cafe naive resume")


    def test_clean_text_reduces_spaces_and_linebreaks(self):
        """
        ✅ Ensure multiple spaces and newlines are reduced to single spaces.
        """
        raw_text = "Hello   World\n\nNew   Line"
        result = clean_text(raw_text)
        self.assertEqual(result, "hello world new line")


    def test_clean_text_already_clean(self):
        """
        🛑 Ensure clean text remains unchanged.
        """
        raw_text = "simple text"
        result = clean_text(raw_text)
        self.assertEqual(result, "simple text")


    def test_clean_text_empty_string(self):
        """
        ⚙️ Handle empty string input gracefully.
        """
        result = clean_text("")
        self.assertEqual(result, "")


    def test_clean_text_only_non_ascii(self):
        """
        ✅ Ensure string with only accented letters is cleaned correctly.
        """
        raw_text = "áéíóúüñ"
        result = clean_text(raw_text)
        self.assertEqual(result, "aeiouun")  # Accents removed, base letters preserved


    def test_clean_text_large_input(self):
        """
        ✅ Ensure large text input is handled without errors.
        """
        raw_text = "  Hello!! 😀\n" * 1000
        result = clean_text(raw_text)

        self.assertTrue(result.startswith("hello!!"))
        self.assertNotIn("\n", result)
        self.assertTrue(len(result) > 0)
