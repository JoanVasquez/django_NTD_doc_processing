# 🛠️ Django Management Command: OCR + Classification + Entity Extraction

import json
import logging

from django.core.management.base import BaseCommand
from documents.ocr import extract_text_from_image
from documents.classifier import predict_document_type
from documents.extractor import extract_entities


# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    📄 Custom Django Command: Process a document image to extract entities.

    Steps:
    1. Perform OCR to extract raw text.
    2. Classify the document type.
    3. Extract relevant entities using Regex + NER.
    """

    help = 'Extract entities from a document using OCR, classifier, and Hugging Face NER.'

    def add_arguments(self, parser):
        """
        ➕ Define command-line argument: image_path
        """
        parser.add_argument(
            'image_path',
            type=str,
            help='Path to image inside container (e.g. /docs-sm/invoice/sample.jpg)'
        )

    def handle(self, *args, **kwargs):
        """
        ⚙️ Command execution entry point.
        """
        image_path = kwargs['image_path']

        logger.info(f"🚀 Starting entity extraction for document: {image_path}")
        self.stdout.write(f"📄 Extracting text from: {image_path}")

        try:
            # 🖼️ OCR
            text = extract_text_from_image(image_path)
            logger.info(f"✅ OCR completed for: {image_path}")

            # 📑 Document Classification
            doc_type = predict_document_type(text)
            logger.info(f"📄 Predicted document type: {doc_type}")
            self.stdout.write(self.style.SUCCESS(f"📄 Detected document type: {doc_type}"))

            # 🏷️ Entity Extraction
            entities = extract_entities(doc_type, text)
            logger.info(f"📦 Extracted {len(entities)} entity fields.")

            # 📊 Output
            self.stdout.write(self.style.SUCCESS("\n✅ Extracted Entities:"))
            self.stdout.write(json.dumps(entities, indent=2))

            logger.info(f"🎉 Entity extraction completed successfully for: {image_path}")

        except Exception as e:
            logger.error(f"❌ Error processing {image_path}: {e}", exc_info=True)
            self.stderr.write(f"❌ Error: {e}")
