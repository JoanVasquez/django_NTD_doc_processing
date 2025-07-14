from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.extractor import get_ner_pipeline

class FinalCoverageTest(TestCase):
    @patch('documents.extractor.pipeline')
    def test_get_ner_pipeline_first_call(self, mock_pipeline_func):
        # Reset global variable
        import documents.extractor
        documents.extractor.ner_pipeline = None
        
        mock_model = MagicMock()
        mock_pipeline_func.return_value = mock_model
        
        result = get_ner_pipeline()
        self.assertEqual(result, mock_model)
        mock_pipeline_func.assert_called_once()
    
    def test_get_ner_pipeline_cached(self):
        # Set up cached pipeline
        import documents.extractor
        cached_pipeline = MagicMock()
        documents.extractor.ner_pipeline = cached_pipeline
        
        result = get_ner_pipeline()
        self.assertEqual(result, cached_pipeline)
    
    @patch('documents.extractor.extract_entities_nltk')
    def test_extract_entities_fallback_nltk(self, mock_nltk):
        from documents.extractor import extract_entities
        
        mock_nltk.return_value = {'PER': ['John Smith']}
        
        # Test with empty initial extraction
        with patch('documents.extractor.extract_generic_entities', return_value={}):
            result = extract_entities("unknown", "John Smith")
            self.assertIn('PER', result)
    
    def test_extract_entities_final_fallback(self):
        from documents.extractor import extract_entities
        
        # Test final fallback with proper nouns
        with patch('documents.extractor.extract_generic_entities', return_value={}):
            with patch('documents.extractor.extract_entities_nltk', return_value={}):
                result = extract_entities("unknown", "John Smith ACME Corp")
                # The fallback actually extracts names, so check for that
                self.assertTrue(len(result) > 0)