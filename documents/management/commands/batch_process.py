import logging
import os
import uuid

from django.core.management.base import BaseCommand

from documents.card_parser import extract_card_fields
from documents.chroma_client import store_document_in_chromadb
from documents.classifier import predict_document_type
from documents.extractor import extract_entities

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    📁 Batch process an entire dataset folder:
    1. Crop card into fields
    2. OCR full image (optional)
    3. Classify using comment region
    4. Extract entities from comment
    5. Store results & metadata in ChromaDB
    """
    help = 'Batch process an entire dataset folder and store results in ChromaDB.'

    def add_arguments(self, parser):
        parser.add_argument(
            'folder_path',
            type=str,
            help='Root folder of your document dataset'
        )

    def handle(self, *args, **options):
        folder_path = options['folder_path']

        logger.info(f"🚀 Starting batch processing for dataset: {folder_path}")

        if not os.path.exists(folder_path):
            logger.error(f"❌ Folder not found: {folder_path}")
            self.stdout.write(self.style.ERROR(f"❌ Folder not found: {folder_path}"))
            return

        total_processed = 0

        # Loop through each labeled subfolder
        for label_folder in os.listdir(folder_path):
            full_label_path = os.path.join(folder_path, label_folder)
            if not os.path.isdir(full_label_path):
                continue

            logger.info(f"📂 Processing label folder: {label_folder}")
            self.stdout.write(self.style.SUCCESS(f"\n🔍 Processing folder: {label_folder}"))

            for file in os.listdir(full_label_path):
                if not file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                file_path = os.path.join(full_label_path, file)
                logger.info(f"🖼️ Processing document: {file_path}")
                self.stdout.write(f"📄 Processing: {file}")

                try:
                    # 1️⃣ Crop form and OCR comment region
                    fields = extract_card_fields(file_path)
                    comment_text = fields.get('comment', '')

                    # 2️⃣ (Optional) Full-image OCR for other purposes
                    # full_text = extract_text_from_image(file_path)

                    # 3️⃣ Classify based on comment region
                    doc_type = predict_document_type(comment_text)
                    logger.info(f"📄 Predicted document type: {doc_type}")

                    # 4️⃣ Extract entities from comment
                    entities = extract_entities(doc_type, comment_text)
                    logger.info(f"📦 Extracted {len(entities)} entity fields.")

                    # 5️⃣ Store in ChromaDB
                    doc_id = str(uuid.uuid4())
                    metadata = {
                        'division': fields.get('division'),
                        'week_ending': fields.get('week_ending'),
                        'account_no': fields.get('account_no'),
                        'document_type': doc_type,
                    }
                    store_document_in_chromadb(
                        doc_id=doc_id,
                        text=comment_text,
                        document_type=doc_type,
                        entities={**metadata, **entities}
                    )

                    logger.info(f"🗄️ Stored document {doc_id} in ChromaDB.")
                    total_processed += 1

                except Exception as e:
                    logger.error(f"❌ Failed to process {file_path}: {e}", exc_info=True)
                    self.stdout.write(self.style.ERROR(f"❌ Failed to process {file}: {e}"))

        # Summary
        logger.info(f"🎉 Batch processing complete. Total documents processed: {total_processed}")
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Batch processing complete. Total documents processed: {total_processed}"
        ))
