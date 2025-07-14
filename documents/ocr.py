from __future__ import annotations

import os
import logging
from typing import Optional

import pytesseract
from PIL import Image, ImageFilter, ImageEnhance

from documents.preprocessing import clean_text

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)

# 🖼️ OCR Text Extraction with Caching (Improved)
def extract_text_from_image(image_path: str, cache_dir: Optional[str] = None, debug_dir: Optional[str] = None) -> str:
    """
    🖼️ Extract text from an image using Tesseract OCR (with caching and enhanced preprocessing).

    Args:
        image_path (str): Full path to the image file.
        cache_dir (str): Directory to store cached OCR results.
        debug_dir (str|None): If provided, saves preprocessed images for debugging.

    Returns:
        str: Cleaned OCR text from image.
    """
    # Validate Image Path
    if not os.path.exists(image_path):
        logger.error(f"❌ Image not found: {image_path}")
        raise FileNotFoundError(f"Image not found: {image_path}")

    if cache_dir is None:
        cache_dir = os.environ.get('OCR_CACHE_DIR', '/app/ocr-cache')
    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    cache_path = os.path.join(cache_dir, filename + ".txt")

    # Return cached text if exists
    if os.path.exists(cache_path):
        logger.info(f"⚡ OCR cache hit for: {filename}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    logger.info(f"⏳ OCR cache miss. Processing image: {image_path}")

    # Read and preprocess image with Pillow
    try:
        image = Image.open(image_path)
    except Exception as e:
        logger.error(f"❌ Failed to read image: {image_path} - {e}")
        raise ValueError(f"Failed to read image: {image_path}")

    # Convert to grayscale and enhance
    gray = image.convert('L')
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    # Apply filter to reduce noise
    gray = gray.filter(ImageFilter.MedianFilter())

    # Save debug image if needed
    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, filename)
        gray.save(debug_path)
        logger.info(f"🐞 Saved debug preprocessed image: {debug_path}")

    # Tesseract config: LSTM engine + single column of text
    custom_config = r"--oem 3 --psm 4"

    # Run OCR
    raw_text = pytesseract.image_to_string(
        gray, config=custom_config, lang="eng"
    ).strip()

    # Clean OCR text
    cleaned_text = clean_text(raw_text)

    # Cache result
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    logger.info(f"✅ OCR completed and cached for: {filename}")
    return cleaned_text
