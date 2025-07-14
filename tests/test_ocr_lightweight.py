import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
from PIL import Image

from documents.ocr import extract_text_from_image


class TestLightweightOCR:
    
    def test_extract_text_file_not_found(self):
        """Test OCR with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_image("nonexistent.jpg")
    
    def test_extract_text_cache_hit(self):
        """Test OCR cache hit"""
        with patch("os.path.exists") as mock_exists:
            # Image exists, then cache exists
            mock_exists.side_effect = lambda path: True
            with patch("builtins.open", mock_open(read_data="cached text")):
                result = extract_text_from_image("test.jpg")
                assert result == "cached text"
    
    def test_extract_text_cache_miss(self):
        """Test OCR cache miss with successful processing"""
        # Mock file existence
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: not path.endswith(".txt")  # No cache
            
            # Mock PIL Image
            mock_image = MagicMock()
            mock_gray = MagicMock()
            mock_image.convert.return_value = mock_gray
            mock_gray.filter.return_value = mock_gray
            
            with patch("PIL.Image.open", return_value=mock_image):
                with patch("PIL.ImageEnhance.Contrast") as mock_contrast:
                    mock_enhancer = MagicMock()
                    mock_enhancer.enhance.return_value = mock_gray
                    mock_contrast.return_value = mock_enhancer
                    
                    with patch("documents.ocr.pytesseract.image_to_string", return_value="extracted text"):
                        with patch("documents.preprocessing.clean_text", return_value="clean text"):
                            with patch("os.makedirs"):
                                with patch("builtins.open", mock_open()):
                                    result = extract_text_from_image("test.jpg")
                                    # Should return the cleaned text
                                    assert isinstance(result, str)
    
    def test_extract_text_image_open_error(self):
        """Test OCR with image open error"""
        with patch("os.path.exists") as mock_exists:
            # Image exists but cache doesn't
            mock_exists.side_effect = lambda path: not path.endswith(".txt")
            with patch("os.makedirs"):
                with patch("PIL.Image.open", side_effect=Exception("Cannot open image")):
                    with pytest.raises(ValueError, match="Failed to read image"):
                        extract_text_from_image("test.jpg")
    
    def test_extract_text_with_debug_dir(self):
        """Test OCR with debug directory"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: not path.endswith(".txt")
            
            mock_image = MagicMock()
            mock_gray = MagicMock()
            mock_image.convert.return_value = mock_gray
            mock_gray.filter.return_value = mock_gray
            
            with patch("PIL.Image.open", return_value=mock_image):
                with patch("PIL.ImageEnhance.Contrast") as mock_contrast:
                    mock_enhancer = MagicMock()
                    mock_enhancer.enhance.return_value = mock_gray
                    mock_contrast.return_value = mock_enhancer
                    
                    with patch("documents.ocr.pytesseract.image_to_string", return_value="text"):
                        with patch("documents.preprocessing.clean_text", return_value="clean"):
                            with patch("os.makedirs") as mock_makedirs:
                                with patch("builtins.open", mock_open()):
                                    result = extract_text_from_image("test.jpg", debug_dir="/debug")
                                    mock_makedirs.assert_called()
                                    mock_gray.save.assert_called()
    
    def test_extract_text_preprocessing_steps(self):
        """Test that image preprocessing steps are called"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: not path.endswith(".txt")
            
            mock_image = MagicMock()
            mock_gray = MagicMock()
            mock_enhanced = MagicMock()
            mock_filtered = MagicMock()
            
            mock_image.convert.return_value = mock_gray
            mock_gray.filter.return_value = mock_filtered
            
            with patch("PIL.Image.open", return_value=mock_image):
                with patch("PIL.ImageEnhance.Contrast") as mock_contrast:
                    mock_enhancer = MagicMock()
                    mock_enhancer.enhance.return_value = mock_enhanced
                    mock_contrast.return_value = mock_enhancer
                    mock_enhanced.filter.return_value = mock_filtered
                    
                    with patch("documents.ocr.pytesseract.image_to_string", return_value="text"):
                        with patch("documents.preprocessing.clean_text", return_value="clean"):
                            with patch("os.makedirs"):
                                with patch("builtins.open", mock_open()):
                                    extract_text_from_image("test.jpg")
                                    
                                    # Verify preprocessing steps
                                    mock_image.convert.assert_called_with('L')  # Grayscale
                                    mock_contrast.assert_called()  # Contrast enhancement
                                    mock_enhancer.enhance.assert_called_with(2.0)  # Enhance factor
    
    def test_extract_text_tesseract_config(self):
        """Test that correct Tesseract config is used"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: not path.endswith(".txt")
            
            mock_image = MagicMock()
            mock_gray = MagicMock()
            mock_image.convert.return_value = mock_gray
            mock_gray.filter.return_value = mock_gray
            
            with patch("PIL.Image.open", return_value=mock_image):
                with patch("PIL.ImageEnhance.Contrast") as mock_contrast:
                    mock_enhancer = MagicMock()
                    mock_enhancer.enhance.return_value = mock_gray
                    mock_contrast.return_value = mock_enhancer
                    
                    with patch("documents.ocr.pytesseract.image_to_string") as mock_tesseract:
                        mock_tesseract.return_value = "text"
                        with patch("documents.preprocessing.clean_text", return_value="clean"):
                            with patch("os.makedirs"):
                                with patch("builtins.open", mock_open()):
                                    extract_text_from_image("test.jpg")
                                    
                                    # Verify Tesseract was called with correct config
                                    mock_tesseract.assert_called_once()
                                    args, kwargs = mock_tesseract.call_args
                                    assert kwargs.get('config') == "--oem 3 --psm 4"
                                    assert kwargs.get('lang') == "eng"
    
    def test_extract_text_caching_behavior(self):
        """Test that results are properly cached"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda path: not path.endswith(".txt")
            
            mock_image = MagicMock()
            mock_gray = MagicMock()
            mock_image.convert.return_value = mock_gray
            mock_gray.filter.return_value = mock_gray
            
            with patch("PIL.Image.open", return_value=mock_image):
                with patch("PIL.ImageEnhance.Contrast") as mock_contrast:
                    mock_enhancer = MagicMock()
                    mock_enhancer.enhance.return_value = mock_gray
                    mock_contrast.return_value = mock_enhancer
                    
                    with patch("documents.ocr.pytesseract.image_to_string", return_value="extracted"):
                        with patch("documents.preprocessing.clean_text", return_value="cleaned"):
                            with patch("os.makedirs"):
                                with patch("builtins.open", mock_open()) as mock_file:
                                    extract_text_from_image("test.jpg", cache_dir="/cache")
                                    
                                    # Verify cache file was written
                                    mock_file.assert_called()
                                    write_calls = [call for call in mock_file().write.call_args_list]
                                    assert len(write_calls) > 0