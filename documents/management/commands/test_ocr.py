# 🛠️ Django Management Command: Batch OCR Test for Images in /docs-sm

import logging
import os

from django.core.management.base import BaseCommand

from documents.ocr import extract_text_from_image

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    🖼️ Custom Django Command:
    Perform OCR on all images inside the /docs-sm directory and print a text preview.
    """

    help = 'Test OCR on all images in /docs-sm.'

    def handle(self, *args, **kwargs):
        """
        ⚙️ Command execution entry point.
        """
        docs_path = 'docs-sm'

        logger.info(f"🚀 Starting OCR batch test in: {docs_path}")

        # 📂 Walk through the /docs-sm directory recursively
        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.join(root, file)

                    logger.info(f"🖼️ Processing image: {full_path}")
                    print(f"\n📄 Processing: {full_path}")

                    try:
                        # 🛠️ OCR Processing
                        text = extract_text_from_image(full_path)
                        logger.info(f"✅ OCR completed for: {full_path}")

                        # 📝 Output Text Preview (up to 300 characters)
                        preview = text[:300] + "..." if len(text) > 300 else text
                        print(preview)

                    except Exception as e:
                        logger.error(f"❌ Error processing image {full_path}: {e}", exc_info=True)
                        print(f"❌ Error: {e}")

        logger.info("🎉 OCR batch test complete.")
