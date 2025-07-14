# 📄 Django Management Command: Predict Document Type from Image

import logging
from django.core.management.base import BaseCommand

from documents.ocr import extract_text_from_image
from documents.classifier import predict_document_type


# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    📑 Custom Django Command:
    Predict the document type from an image using OCR + classifier.
    """

    help = 'Predict document type for a given image path using OCR and text classification.'

    def add_arguments(self, parser):
        """
        ➕ Define CLI argument for the command.
        """
        parser.add_argument(
            'image_path',
            type=str,
            help='Path to image inside container (e.g., /docs-sm/invoice/sample1.png)'
        )

    def handle(self, *args, **kwargs):
        """
        ⚙️ Command execution: Extract text via OCR and predict document type.
        """
        path = kwargs['image_path']

        logger.info(f"🚀 Starting document type prediction for: {path}")

        try:
            # 🖼️ Step 1: OCR
            text = extract_text_from_image(path)
            logger.info(f"✅ OCR completed for: {path}")

            # 🏷️ Step 2: Predict Document Type
            doc_type = predict_document_type(text)
            logger.info(f"📄 Predicted document type: {doc_type}")

            # 📊 Output Result
            self.stdout.write(self.style.SUCCESS(f"✅ Predicted Document Type: {doc_type}"))
            logger.info(f"🎉 Document type prediction completed for: {path}")

        except Exception as e:
            logger.error(f"❌ Error predicting document type for {path}: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
