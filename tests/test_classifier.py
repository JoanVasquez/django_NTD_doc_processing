# 🧪 Unit Tests: Document Classifier (Loading, Training, Predicting)

from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.classifier import (
    load_documents_from_folders,
    train_and_save_model,
    predict_document_type
)
import os


class DocumentClassifierMainFlowTest(TestCase):
    """
    🧪 Unit Tests:
    Covers loading documents, model training, and document type prediction.
    """

    # ✅ Test: Successful document loading with images
    @patch("documents.classifier.logger")
    @patch("documents.classifier.extract_text_from_image", side_effect=["text1", "text2", "text3"])
    @patch("documents.classifier.os.listdir")
    @patch("documents.classifier.os.path.isdir", return_value=True)
    @patch("documents.classifier.os.path.exists", return_value=True)
    def test_load_documents_from_folders_full_flow(self, mock_exists, mock_isdir, mock_listdir, mock_ocr, mock_logger):
        """
        ✅ Ensure documents are correctly loaded from folders with images.
        """
        mock_listdir.side_effect = [
            ["invoices"],  # Folder list
            ["doc1.jpg", "doc2.png", "doc3.jpeg"]  # Files inside folder
        ]

        texts, labels = load_documents_from_folders(base_path="docs-sm")

        self.assertEqual(len(texts), 3)
        self.assertEqual(labels, ["invoices", "invoices", "invoices"])
        mock_ocr.assert_called()
        mock_logger.info.assert_any_call("📄 Processed: doc3.jpeg")


    # ❌ Test: Error handling when OCR fails
    @patch("documents.classifier.logger")
    @patch("documents.classifier.extract_text_from_image", side_effect=Exception("OCR failed"))
    @patch("documents.classifier.os.listdir")
    @patch("documents.classifier.os.path.isdir", return_value=True)
    @patch("documents.classifier.os.path.exists", return_value=True)
    def test_load_documents_error_handling(self, mock_exists, mock_isdir, mock_listdir, mock_ocr, mock_logger):
        """
        ❌ Ensure OCR errors are handled gracefully during document loading.
        """
        mock_listdir.side_effect = [
            ["invoices"],
            ["error_doc.jpg"]
        ]

        texts, labels = load_documents_from_folders(base_path="docs-sm")

        self.assertEqual(texts, [])
        self.assertEqual(labels, [])
        mock_logger.error.assert_called()


    # 🛑 Test: Skip non-image files during loading
    @patch("documents.classifier.logger")
    @patch("documents.classifier.os.listdir")
    @patch("documents.classifier.os.path.isdir", return_value=True)
    @patch("documents.classifier.os.path.exists", return_value=True)
    def test_load_documents_skips_non_images(self, mock_exists, mock_isdir, mock_listdir, mock_logger):
        """
        🛑 Ensure non-image files are skipped during loading.
        """
        mock_listdir.side_effect = [
            ["invoices"],
            ["ignore.txt", "readme.md"]
        ]

        with patch("documents.classifier.extract_text_from_image") as mock_extract:
            texts, labels = load_documents_from_folders(base_path="docs-sm")
            self.assertEqual(texts, [])
            self.assertEqual(labels, [])
            mock_extract.assert_not_called()
            mock_logger.debug.assert_called()


    # 🛑 Test: Training skips empty datasets
    @patch("documents.classifier.logger")
    @patch("documents.classifier.load_documents_from_folders", return_value=([], []))
    def test_train_and_save_model_empty_dataset(self, mock_loader, mock_logger):
        """
        🛑 Ensure training is skipped with empty datasets.
        """
        train_and_save_model(output_path="dummy.joblib")
        mock_logger.error.assert_any_call(
            "❌ No data to train on. Check your '/docs-sm' directory and file formats."
        )


    # ✅ Test: Successful model training full flow
    @patch("documents.classifier.load_documents_from_folders", return_value=(["sample"] * 10, ["invoice"] * 10))
    @patch("documents.classifier.joblib.dump")
    @patch("documents.classifier.Pipeline.fit")
    @patch("documents.classifier.Pipeline.predict")
    @patch("documents.classifier.logger")
    def test_train_and_save_model_full_flow(self, mock_logger, mock_predict, mock_fit, mock_dump, mock_loader):
        """
        ✅ Ensure full training pipeline runs and model is saved.
        """
        mock_predict.side_effect = lambda X: ["invoice"] * len(X)

        train_and_save_model(output_path="dummy_model.joblib")

        mock_fit.assert_called_once()
        mock_predict.assert_called_once()
        mock_dump.assert_called_once()
        mock_logger.info.assert_any_call("🤖 Training document classifier...")
        mock_logger.info.assert_any_call("💾 Model saved to: dummy_model.joblib")


    # ❌ Test: Predict raises error if model file missing
    @patch("documents.classifier.logger")
    @patch("documents.classifier.os.path.exists", return_value=False)
    def test_predict_document_type_model_missing(self, mock_exists, mock_logger):
        """
        ❌ Ensure prediction fails gracefully when model is missing.
        """
        with self.assertRaises(FileNotFoundError):
            predict_document_type("dummy text", model_path="missing_model.joblib")
        mock_logger.error.assert_called()


    # ✅ Test: Successful prediction
    @patch("documents.classifier.os.path.exists", return_value=True)
    @patch("documents.classifier.joblib.load")
    @patch("documents.classifier.logger")
    def test_predict_document_type_success(self, mock_logger, mock_joblib_load, mock_exists):
        """
        ✅ Ensure document type is predicted correctly.
        """
        mock_model = MagicMock()
        mock_model.predict.return_value = ["invoice"]
        mock_joblib_load.return_value = mock_model

        result = predict_document_type("sample text", model_path="existing_model.joblib")
        self.assertEqual(result, "invoice")
        mock_logger.debug.assert_called()
