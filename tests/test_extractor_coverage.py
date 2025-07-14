from django.test import TestCase
from unittest.mock import patch, MagicMock
from documents.extractor import _merge_ner, _apply_mapping

class ExtractorCoverageTest(TestCase):
    @patch('documents.extractor.get_ner_pipeline')
    def test_merge_ner_success(self, mock_pipeline):
        mock_ner = MagicMock()
        mock_ner.return_value = [
            {'entity_group': 'PER', 'word': 'John'},
            {'entity_group': 'ORG', 'word': 'ACME'}
        ]
        mock_pipeline.return_value = mock_ner
        
        entities = {'MISC': ['test']}
        result = _merge_ner("John works at ACME", entities)
        
        self.assertIn('PER', result)
        self.assertIn('ORG', result)
        self.assertIn('MISC', result)
    
    @patch('documents.extractor.get_ner_pipeline')
    def test_merge_ner_error(self, mock_pipeline):
        mock_pipeline.side_effect = Exception("NER error")
        
        entities = {'MISC': ['test']}
        result = _merge_ner("test text", entities)
        
        self.assertEqual(result, {'MISC': ['test']})
    
    def test_apply_mapping(self):
        entities = {
            'PER': ['John Smith'],
            'ORG': ['ACME Corp'],
            'MISC': ['12345']
        }
        
        result = _apply_mapping(entities, 'invoice')
        
        self.assertIn('vendor', result)
        self.assertIn('contact_person', result)
        self.assertEqual(result['vendor'], ['ACME Corp'])
        self.assertEqual(result['contact_person'], ['John Smith'])
    
    def test_apply_mapping_unknown_type(self):
        entities = {
            'PER': ['John Smith'],
            'ORG': ['ACME Corp']
        }
        
        result = _apply_mapping(entities, 'unknown_type')
        
        # Should keep original keys for unknown document types
        self.assertIn('PER', result)
        self.assertIn('ORG', result)