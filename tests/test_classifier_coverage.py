from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.classifier import predict_document_type, train_and_save_model

class ClassifierCoverageTest(TestCase):
    @patch('documents.classifier.joblib.load')
    @patch('documents.classifier.os.path.exists')
    def test_predict_document_type_success(self, mock_exists, mock_load):
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_model.predict.return_value = ['invoice']
        mock_load.return_value = mock_model
        
        result = predict_document_type("Sample invoice text")
        self.assertEqual(result, 'invoice')
    
    @patch('documents.classifier.os.path.exists')
    def test_predict_document_type_no_model(self, mock_exists):
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            predict_document_type("Sample text")
    
    @patch('documents.classifier.load_documents_from_folders')
    def test_train_and_save_model_no_data(self, mock_load):
        mock_load.return_value = ([], [])
        
        # Should return early without error
        train_and_save_model("test.joblib")
        
    @patch('documents.classifier.load_documents_from_folders')
    @patch('documents.classifier.joblib.dump')
    def test_train_and_save_model_success(self, mock_dump, mock_load):
        mock_load.return_value = (["text1", "text2"] * 10, ["invoice", "letter"] * 10)
        
        train_and_save_model("test.joblib")
        mock_dump.assert_called_once()