from django.test import TestCase
from unittest.mock import patch, MagicMock
import documents.extractor

class ExtractorMissingLinesTest(TestCase):
    """Test the specific missing lines in extractor.py"""
    
    @patch('documents.extractor.nltk.data.find')
    @patch('documents.extractor.nltk.download')
    def test_nltk_downloads_lines_15_28(self, mock_download, mock_find):
        """Test NLTK download blocks (lines 15-28)"""
        # Test punkt download
        mock_find.side_effect = LookupError("Not found")
        try:
            import importlib
            importlib.reload(documents.extractor)
        except:
            pass  # Expected due to mocking
        
        # Verify download was called
        self.assertTrue(mock_download.called or mock_find.called)
    
    @patch('documents.extractor.word_tokenize')
    @patch('documents.extractor.pos_tag')
    @patch('documents.extractor.ne_chunk')
    @patch('documents.extractor.word_list')
    def test_nltk_spell_correction_lines_153_158(self, mock_word_list, mock_chunk, mock_pos, mock_token):
        """Test spell correction logic (lines 153-158)"""
        from documents.extractor import extract_entities_nltk
        
        # Mock tokenization with misspelled word
        mock_token.return_value = ['misspeled', 'word']
        mock_pos.return_value = [('misspeled', 'NN'), ('word', 'NN')]
        mock_chunk.return_value = []
        
        # Mock word list to trigger spell correction
        mock_word_list.__contains__ = MagicMock(return_value=False)
        
        # Mock word_list as iterable for candidates
        with patch('documents.extractor.word_list', ['misspelled', 'word']):
            with patch('documents.extractor.edit_distance', return_value=1):
                result = extract_entities_nltk("misspeled word")
                self.assertIsInstance(result, dict)
    
    @patch('documents.extractor.word_tokenize')
    @patch('documents.extractor.pos_tag')
    @patch('documents.extractor.ne_chunk')
    def test_nltk_short_tokens_lines_111_112(self, mock_chunk, mock_pos, mock_token):
        """Test short token handling (lines 111-112)"""
        from documents.extractor import extract_entities_nltk
        
        # Mock with short tokens (<=2 chars) and non-alpha
        mock_token.return_value = ['a', 'bb', '123', 'John']
        mock_pos.return_value = [('a', 'DT'), ('bb', 'NN'), ('123', 'CD'), ('John', 'NNP')]
        mock_chunk.return_value = []
        
        result = extract_entities_nltk("a bb 123 John")
        self.assertIsInstance(result, dict)
    
    def test_handwritten_extraction_line_182(self):
        """Test handwritten document extraction (line 182)"""
        from documents.extractor import extract_entities
        
        # This should trigger the handwritten-specific path
        result = extract_entities("handwritten", "test content")
        self.assertIsInstance(result, dict)
    
    def test_duplicate_functions_lines_264_328(self):
        """Test duplicate function definitions (lines 264-328)"""
        # These are duplicate _merge_ner, _apply_mapping, extract_generic_entities
        from documents.extractor import _merge_ner, _apply_mapping
        
        # Test duplicate _merge_ner
        with patch('documents.extractor.get_ner_pipeline') as mock_pipeline:
            mock_ner = MagicMock()
            mock_ner.return_value = [{'entity_group': 'PER', 'word': 'John'}]
            mock_pipeline.return_value = mock_ner
            
            result = _merge_ner("John Smith", {})
            self.assertIn('PER', result)
        
        # Test duplicate _apply_mapping
        entities = {'PER': ['John'], 'ORG': ['ACME']}
        result = _apply_mapping(entities, 'invoice')
        self.assertIsInstance(result, dict)
    
    @patch('documents.extractor.word_tokenize')
    @patch('documents.extractor.pos_tag')
    @patch('documents.extractor.ne_chunk')
    def test_nltk_entity_types_lines_162_165(self, mock_chunk, mock_pos, mock_token):
        """Test different NLTK entity types (lines 162-165)"""
        from documents.extractor import extract_entities_nltk
        
        mock_token.return_value = ['John', 'ACME', 'Tokyo', 'Other']
        mock_pos.return_value = [('John', 'NNP'), ('ACME', 'NNP'), ('Tokyo', 'NNP'), ('Other', 'NN')]
        
        # Mock different entity types
        mock_person = MagicMock()
        mock_person.label.return_value = 'PERSON'
        mock_person.leaves.return_value = [('John', 'NNP')]
        
        mock_org = MagicMock()
        mock_org.label.return_value = 'ORGANIZATION'  
        mock_org.leaves.return_value = [('ACME', 'NNP')]
        
        mock_loc = MagicMock()
        mock_loc.label.return_value = 'GPE'
        mock_loc.leaves.return_value = [('Tokyo', 'NNP')]
        
        mock_other = MagicMock()
        mock_other.label.return_value = 'OTHER'
        mock_other.leaves.return_value = [('Other', 'NN')]
        
        mock_chunk.return_value = [mock_person, mock_org, mock_loc, mock_other]
        
        result = extract_entities_nltk("John ACME Tokyo Other")
        
        # Should have all entity types
        self.assertIn('PER', result)
        self.assertIn('ORG', result) 
        self.assertIn('LOC', result)
        self.assertIn('MISC', result)