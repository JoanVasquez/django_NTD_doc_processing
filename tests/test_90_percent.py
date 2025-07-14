from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.extractor import extract_entities

class NinetyPercentTest(TestCase):
    def test_extract_entities_empty_content(self):
        """Test extraction with empty content"""
        result = extract_entities("unknown", "")
        self.assertIsInstance(result, dict)
    
    def test_extract_entities_whitespace_only(self):
        """Test extraction with whitespace only"""
        result = extract_entities("unknown", "   \n\t  ")
        self.assertIsInstance(result, dict)
    
    @patch('documents.extractor._merge_ner')
    def test_extract_entities_merge_ner_called(self, mock_merge):
        """Test that merge_ner is called for business documents"""
        mock_merge.return_value = {'PER': ['John']}
        
        result = extract_entities("letter", "John Smith")
        mock_merge.assert_called()
        self.assertIn('recipient', result)
    
    def test_extract_entities_all_document_types(self):
        """Test extraction for all supported document types"""
        doc_types = ['advertisement', 'budget', 'email', 'file_folder', 'form', 
                    'handwritten', 'invoice', 'letter', 'memo', 'news_article',
                    'presentation', 'questionnaire', 'resume', 'scientific_publication',
                    'scientific_report', 'specification']
        
        for doc_type in doc_types:
            result = extract_entities(doc_type, "John Smith ACME Corp")
            self.assertIsInstance(result, dict)
    
    def test_extract_entities_special_characters(self):
        """Test extraction with special characters"""
        result = extract_entities("unknown", "John@Smith #123 $%^&*()")
        self.assertIsInstance(result, dict)