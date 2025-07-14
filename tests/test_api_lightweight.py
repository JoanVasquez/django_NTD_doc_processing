import json
from unittest.mock import MagicMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class TestLightweightAPI(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/process-document/'
    
    def test_process_document_no_file(self):
        """Test API with no file uploaded"""
        response = self.client.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    @patch('api.views.store_document_in_chromadb')
    def test_process_document_success(self, mock_store, mock_extract, mock_predict, mock_ocr):
        """Test successful document processing"""
        # Setup mocks
        mock_ocr.return_value = "extracted text"
        mock_predict.return_value = "letter"
        mock_extract.return_value = {"recipient": ["John Doe"]}
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'document_id' in response.data
        assert response.data['document_type'] == 'letter'
        assert response.data['entities'] == {"recipient": ["John Doe"]}
        
        # Verify all functions were called
        mock_ocr.assert_called_once()
        mock_predict.assert_called_once_with("extracted text")
        mock_extract.assert_called_once_with("letter", "extracted text")
        mock_store.assert_called_once()
    
    @patch('api.views.extract_text_from_image')
    def test_process_document_ocr_error(self, mock_ocr):
        """Test API with OCR error"""
        mock_ocr.side_effect = Exception("OCR failed")
        
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    def test_process_document_classifier_error(self, mock_predict, mock_ocr):
        """Test API with classifier error"""
        mock_ocr.return_value = "text"
        mock_predict.side_effect = Exception("Classification failed")
        
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    def test_process_document_extractor_error(self, mock_extract, mock_predict, mock_ocr):
        """Test API with entity extraction error"""
        mock_ocr.return_value = "text"
        mock_predict.return_value = "letter"
        mock_extract.side_effect = Exception("Extraction failed")
        
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    @patch('api.views.store_document_in_chromadb')
    def test_process_document_storage_error(self, mock_store, mock_extract, mock_predict, mock_ocr):
        """Test API with storage error"""
        mock_ocr.return_value = "text"
        mock_predict.return_value = "letter"
        mock_extract.return_value = {}
        mock_store.side_effect = Exception("Storage failed")
        
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    @patch('api.views.store_document_in_chromadb')
    def test_process_document_different_types(self, mock_store, mock_extract, mock_predict, mock_ocr):
        """Test API with different document types"""
        mock_ocr.return_value = "invoice text"
        mock_predict.return_value = "invoice"
        mock_extract.return_value = {"vendor": ["ABC Corp"], "invoice_number": ["INV-123"]}
        
        test_file = SimpleUploadedFile(
            "invoice.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['document_type'] == 'invoice'
        assert 'vendor' in response.data['entities']
        assert 'invoice_number' in response.data['entities']
    
    def test_process_document_invalid_method(self):
        """Test API with invalid HTTP method"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    @patch('api.views.store_document_in_chromadb')
    def test_process_document_empty_entities(self, mock_store, mock_extract, mock_predict, mock_ocr):
        """Test API with empty entity extraction results"""
        mock_ocr.return_value = "text with no entities"
        mock_predict.return_value = "memo"
        mock_extract.return_value = {}
        
        test_file = SimpleUploadedFile(
            "memo.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['entities'] == {}
    
    @patch('api.views.extract_text_from_image')
    @patch('api.views.predict_document_type')
    @patch('api.views.extract_entities')
    @patch('api.views.store_document_in_chromadb')
    @patch('uuid.uuid4')
    def test_process_document_uuid_generation(self, mock_uuid, mock_store, mock_extract, mock_predict, mock_ocr):
        """Test that UUID is properly generated for document ID"""
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__ = MagicMock(return_value="test-uuid-123")
        
        mock_ocr.return_value = "text"
        mock_predict.return_value = "letter"
        mock_extract.return_value = {}
        
        test_file = SimpleUploadedFile(
            "test.jpg", 
            b"fake image content", 
            content_type="image/jpeg"
        )
        
        response = self.client.post(self.url, {'file': test_file})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['document_id'] == "test-uuid-123"
        mock_uuid.assert_called_once()
    
    def test_clean_text_preview_function(self):
        """Test the clean_text_preview utility function"""
        from api.views import clean_text_preview

        # Test normal text
        result = clean_text_preview("This is a normal text with good words")
        assert "This" in result and "normal" in result
        
        # Test text with garbage characters
        result = clean_text_preview("Good text @@##$$ more good text")
        assert len(result) > 0
        
        # Test very short text
        result = clean_text_preview("ab cd")
        assert isinstance(result, str)
        
        # Test garbage text
        result = clean_text_preview("@@##$$%%^^&&")
        assert "[OCR text quality too poor for preview]" in result
        
        # Test long text truncation
        long_text = " ".join(["word" for _ in range(100)])
        result = clean_text_preview(long_text, max_length=50)
        assert len(result) <= 53  # 50 + "..."