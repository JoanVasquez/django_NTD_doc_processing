# 🧹 Text Preprocessing Module

from __future__ import annotations

import logging
import re
import unicodedata

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


# 🧹 Clean & Normalize Text
def clean_text(text: str) -> str:
    """
    🧹 Preprocess text for consistent handling.

    Steps:
    - Normalize Unicode accents to ASCII (e.g., café ➔ cafe).
    - Remove non-ASCII characters.
    - Replace multiple whitespaces/newlines with a single space.
    - Lowercase all text.

    Args:
        text (str): Raw input text.

    Returns:
        str: Cleaned and normalized text.
    """
    original_length = len(text)
    logger.debug(f"🛠️ Starting text cleaning. Original length: {original_length} characters.")

    # ✂️ Normalize Unicode accents
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

    # ✂️ Replace multiple whitespaces and newlines with single space
    text = re.sub(r'\s+', ' ', text)

    # 🔡 Convert to lowercase
    text = text.lower()

    cleaned_length = len(text.strip())
    logger.debug(f"✅ Text cleaned. Final length: {cleaned_length} characters.")

    return text.strip()
