from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch

class OCRCommandTest(TestCase):
    @patch("documents.management.commands.test_ocr.extract_text_from_image", return_value="sample text")
    @patch("documents.management.commands.test_ocr.os.walk")
    @patch("documents.management.commands.test_ocr.os.path.exists", return_value=True)
    def test_test_ocr_command(self, mock_exists, mock_walk, mock_ocr):
        mock_walk.return_value = [('docs-sm/invoice', [], ['file1.jpg'])]

        call_command('test_ocr')

        mock_ocr.assert_called_once()
