# 🤖 Django Management Command: Train Document Classifier

import logging

from django.core.management.base import BaseCommand

from documents.classifier import train_and_save_model

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    🎓 Custom Django Command:
    Train and save the document classification model using OCR-extracted text.
    """

    help = "Train the document classifier using OCR-extracted text."

    def handle(self, *args, **kwargs):
        """
        ⚙️ Main command execution.
        """
        logger.info("🚀 Starting document classifier training...")

        try:
            # 🤖 Train Model
            train_and_save_model()

            # ✅ Success
            logger.info("🎉 Document classifier training completed successfully.")
            self.stdout.write(self.style.SUCCESS("✅ Document classifier training completed successfully."))

        except Exception as e:
            # ❌ Failure
            logger.error(f"❌ Error during classifier training: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"❌ Training failed: {e}"))
