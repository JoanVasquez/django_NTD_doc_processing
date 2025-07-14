# 🧪 Unit Tests: OCR Extraction (Coverage & Cache Handling)

import os
from unittest.mock import patch, MagicMock
from django.test import TestCase
from documents.ocr import extract_text_from_image


# 🔗 Save original os.path.exists to avoid recursion in tests
REAL_OS_PATH_EXISTS = os.path.exists  


class OCRExtractionCoverageTest(TestCase):
    """
    🧪 Unit Tests:
    Covers OCR failure handling, cache handling, and extraction logic.
    """

    @patch("documents.ocr.logger")
    def test_image_not_found_raises_file_not_found(self, mock_logger):
        """
        ❌ Validate FileNotFoundError when image does not exist.
        """
        with self.assertRaises(FileNotFoundError):
            extract_text_from_image("nonexistent.jpg")

        mock_logger.error.assert_called_with("❌ Image not found: nonexistent.jpg")


    @patch("documents.ocr.os.path.exists")
    @patch("documents.ocr.cv2.imread", return_value=None)
    @patch("documents.ocr.logger")
    def test_ocr_processing_exception(self, mock_logger, mock_imread, mock_exists):
        """
        ❌ Simulate cv2.imread() failure after cache miss.
        Validate that exception is raised and error logged.
        """
        image_path = "docs-sm/invoice/invalid_image.jpg"
        filename = os.path.basename(image_path)
        cache_path = os.path.join("/ocr-cache", filename + ".txt")

        # Simulate file existence logic
        def exists_side_effect(path):
            if path == image_path:
                return True  # Pretend image exists
            if path == cache_path:
                return False  # Pretend cache doesn't exist
            return REAL_OS_PATH_EXISTS(path)

        mock_exists.side_effect = exists_side_effect

        with self.assertRaises(Exception):
            extract_text_from_image(image_path)

        mock_logger.error.assert_called()  # Should log processing failure


    @patch("documents.ocr.clean_text", return_value="cleaned result")
    @patch("documents.ocr.pytesseract.image_to_string", return_value="OCR RAW RESULT")
    @patch("documents.ocr.cv2.cvtColor")
    @patch("documents.ocr.cv2.imread", return_value=MagicMock())
    @patch("documents.ocr.os.path.exists")
    def test_extract_text_from_image_cache_miss_and_write(self, mock_exists, mock_imread, mock_cvtcolor, mock_ocr, mock_clean):
        """
        ✅ Simulate full OCR processing flow after cache miss.
        Validate:
        - OCR and cleaning are invoked.
        - Result is cached and written to disk.
        - Cache file content matches cleaned result.
        """
        image_path = "docs-sm/invoice/new_image.jpg"
        filename = os.path.basename(image_path)
        cache_dir = "/ocr-cache"
        cache_path = os.path.join(cache_dir, filename + ".txt")

        # Simulate file existence logic
        def exists_side_effect(path):
            if path == image_path:
                return True
            if path == cache_path:
                return False
            return REAL_OS_PATH_EXISTS(path)

        mock_exists.side_effect = exists_side_effect

        # Ensure cache file doesn't exist before test
        if os.path.exists(cache_path):
            os.remove(cache_path)

        result = extract_text_from_image(image_path)
        self.assertEqual(result, "cleaned result")

        # ✅ Verify cache directory and file creation
        self.assertTrue(os.path.exists(cache_dir))
        self.assertTrue(os.path.isfile(cache_path))

        # 📄 Verify cached content matches cleaned result
        with open(cache_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "cleaned result")
