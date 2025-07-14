import pytesseract
import cv2
import os
import logging

from documents.preprocessing import clean_text

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)

# 🖼️ OCR Text Extraction with Caching (Improved)
def extract_text_from_image(image_path: str, cache_dir="/app/ocr-cache", debug_dir=None) -> str:
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

    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    cache_path = os.path.join(cache_dir, filename + ".txt")

    # Return cached text if exists
    if os.path.exists(cache_path):
        logger.info(f"⚡ OCR cache hit for: {filename}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    logger.info(f"⏳ OCR cache miss. Processing image: {image_path}")

    # Read and preprocess image
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"❌ Failed to read image: {image_path}")
        raise ValueError(f"Failed to read image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Reduce noise while keeping edges
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # Adaptive threshold to binarize
    gray = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
    )

    # Save debug image if needed
    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, filename)
        cv2.imwrite(debug_path, gray)
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
