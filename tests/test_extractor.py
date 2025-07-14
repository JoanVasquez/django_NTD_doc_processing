from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.extractor import (
    extract_entities, extract_news_article_entities, extract_business_document_entities,
    extract_generic_entities, extract_entities_nltk
)

class EntityExtractorTest(TestCase):
    def test_extract_entities_news_article(self):
        text = "Tuesday, July 20, 1999 MARK GORSKI San Diego University of California 30 percent"
        entities = extract_entities("news_article", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_business_document(self):
        text = "Development Center Work Request J. F. Wilhelm ACME Company Ltd. #1984-29 Tokyo, Japan"
        entities = extract_entities("letter", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_handwritten(self):
        text = "winston salem p.o. box 2506 mail receipts information"
        entities = extract_entities("handwritten", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_entities_generic(self):
        text = "John Smith ACME Corp New York 12345"
        entities = extract_entities("unknown", text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_news_article_entities(self):
        text = "MARK GORSKI San Diego University of California 30 percent"
        entities = extract_news_article_entities(text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_business_document_entities(self):
        text = "J. F. Wilhelm Development Center #1984-29 340 cartons"
        entities = extract_business_document_entities(text)
        self.assertIsInstance(entities, dict)
    
    def test_extract_generic_entities(self):
        text = "John Smith ACME Corp 2024 12345"
        entities = extract_generic_entities(text)
        self.assertIsInstance(entities, dict)
    

    
    @patch('documents.extractor.word_tokenize')
    @patch('documents.extractor.pos_tag')
    @patch('documents.extractor.ne_chunk')
    def test_extract_entities_nltk(self, mock_chunk, mock_pos, mock_token):
        mock_token.return_value = ['John', 'Smith']
        mock_pos.return_value = [('John', 'NNP'), ('Smith', 'NNP')]
        mock_chunk.return_value = []
        
        entities = extract_entities_nltk("John Smith")
        self.assertIsInstance(entities, dict)
    
    def test_fallback_extraction(self):
        # Test fallback when no entities found
        text = "Xyz Abc Def"
        entities = extract_entities("unknown", text)
        self.assertIsInstance(entities, dict)