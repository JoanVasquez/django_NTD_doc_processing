# 📁 Django Management Command: Batch Process Dataset and Store in ChromaDB

import os
import uuid
import logging

from django.core.management.base import BaseCommand
from documents.ocr import extract_text_from_image
from documents.classifier import predict_document_type
from documents.extractor import extract_entities
from documents.chroma_client import store_document_in_chromadb


# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    📦 Custom Django Command:
    Batch process an entire dataset folder:
    - OCR extraction
    - Document type classification
    - Entity extraction
    - Store results in ChromaDB
    """

    help = 'Batch process an entire dataset folder and store results in ChromaDB.'

    def add_arguments(self, parser):
        """
        ➕ Define CLI argument for the command.
        """
        parser.add_argument(
            'folder_path',
            type=str,
            help='Root folder of your document dataset'
        )

    def handle(self, *args, **options):
        """
        ⚙️ Main execution method.
        """
        folder_path = options['folder_path']

        logger.info(f"🚀 Starting batch processing for dataset: {folder_path}")

        if not os.path.exists(folder_path):
            logger.error(f"❌ Folder not found: {folder_path}")
            self.stdout.write(self.style.ERROR(f"❌ Folder not found: {folder_path}"))
            return

        total_processed = 0

        # 📂 Loop through dataset folders (each folder = label)
        for label_folder in os.listdir(folder_path):
            full_label_path = os.path.join(folder_path, label_folder)
            if not os.path.isdir(full_label_path):
                continue

            logger.info(f"📂 Processing folder: {label_folder}")
            self.stdout.write(self.style.SUCCESS(f"\n🔍 Processing folder: {label_folder}"))

            # 📄 Process each image in the label folder
            for file in os.listdir(full_label_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(full_label_path, file)
                    logger.info(f"📄 Processing document: {file_path}")
                    self.stdout.write(f"📄 Processing: {file}")

                    try:
                        # 🖼️ Step 1: OCR
                        text = extract_text_from_image(file_path)
                        logger.info(f"✅ OCR completed for: {file_path}")

                        # 📑 Step 2: Document Classification
                        doc_type = predict_document_type(text)
                        logger.info(f"📄 Predicted document type: {doc_type}")

                        # 🏷️ Step 3: Entity Extraction
                        entities = extract_entities(doc_type, text)
                        logger.info(f"📦 Extracted {len(entities)} entity fields.")

                        # 🗃️ Step 4: Store in ChromaDB
                        doc_id = str(uuid.uuid4())
                        store_document_in_chromadb(
                            doc_id=doc_id,
                            text=text,
                            document_type=doc_type,
                            entities=entities
                        )
                        logger.info(f"🗄️ Stored document {doc_id} in ChromaDB.")

                        total_processed += 1

                    except Exception as e:
                        logger.error(f"❌ Failed to process {file_path}: {e}", exc_info=True)
                        self.stdout.write(self.style.ERROR(f"❌ Failed to process {file}: {e}"))

        # ✅ Summary
        logger.info(f"🎉 Batch processing complete. Total documents processed: {total_processed}")
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Batch processing complete. Total documents processed: {total_processed}"
        ))
