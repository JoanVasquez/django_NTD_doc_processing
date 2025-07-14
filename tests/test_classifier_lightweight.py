import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock dependencies before import
sklearn_mock = MagicMock()
sklearn_mock.feature_extraction = MagicMock()
sklearn_mock.feature_extraction.text = MagicMock()
sklearn_mock.linear_model = MagicMock()
sklearn_mock.pipeline = MagicMock()
sklearn_mock.model_selection = MagicMock()
sklearn_mock.metrics = MagicMock()
sys.modules['sklearn'] = sklearn_mock
sys.modules['sklearn.feature_extraction'] = sklearn_mock.feature_extraction
sys.modules['sklearn.feature_extraction.text'] = sklearn_mock.feature_extraction.text
sys.modules['sklearn.linear_model'] = sklearn_mock.linear_model
sys.modules['sklearn.pipeline'] = sklearn_mock.pipeline
sys.modules['sklearn.model_selection'] = sklearn_mock.model_selection
sys.modules['sklearn.metrics'] = sklearn_mock.metrics
sys.modules['joblib'] = MagicMock()

from documents.classifier import (
    load_documents_from_folders,
    predict_document_type,
    train_and_save_model,
)


class TestLightweightClassifier:
    
    @patch('documents.classifier.os.path.exists', return_value=True)
    @patch('documents.classifier.os.path.isdir', return_value=True)
    @patch('documents.classifier.os.listdir')
    @patch('documents.classifier.extract_text_from_image')
    def test_load_documents_success(self, mock_ocr, mock_listdir, mock_isdir, mock_exists):
        mock_listdir.side_effect = [["invoice"], ["doc1.jpg"]]
        mock_ocr.return_value = "sample text"
        
        texts, labels = load_documents_from_folders("docs-sm")
        assert len(texts) == 1
        assert labels == ["invoice"]
    
    @patch('documents.classifier.os.path.exists', return_value=True)
    @patch('documents.classifier.os.path.isdir', return_value=True)
    @patch('documents.classifier.os.listdir')
    def test_load_documents_no_images(self, mock_listdir, mock_isdir, mock_exists):
        mock_listdir.side_effect = [["invoice"], ["readme.txt"]]
        
        texts, labels = load_documents_from_folders("docs-sm")
        assert len(texts) == 0
        assert len(labels) == 0
    
    @patch('documents.classifier.load_documents_from_folders')
    @patch('documents.classifier.joblib.dump')
    @patch('documents.classifier.Pipeline')
    @patch('documents.classifier.train_test_split')
    def test_train_model_success(self, mock_split, mock_pipeline, mock_dump, mock_load):
        mock_load.return_value = (["text1", "text2"], ["invoice", "letter"])
        mock_split.return_value = (["text1"], ["text2"], ["invoice"], ["letter"])
        mock_model = MagicMock()
        mock_pipeline.return_value = mock_model
        
        train_and_save_model("model.joblib")
        mock_model.fit.assert_called_once()
        mock_dump.assert_called_once()
    
    @patch('documents.classifier.load_documents_from_folders')
    def test_train_model_no_data(self, mock_load):
        mock_load.return_value = ([], [])
        
        train_and_save_model("model.joblib")
        # Should handle empty data gracefully
    
    @patch('documents.classifier.os.path.exists', return_value=True)
    @patch('documents.classifier.joblib.load')
    def test_predict_success(self, mock_load, mock_exists):
        mock_model = MagicMock()
        mock_model.predict.return_value = ["invoice"]
        mock_load.return_value = mock_model
        
        result = predict_document_type("sample text")
        assert result == "invoice"
    
    @patch('documents.classifier.os.path.exists', return_value=False)
    def test_predict_no_model(self, mock_exists):
        with pytest.raises(FileNotFoundError):
            predict_document_type("sample text")