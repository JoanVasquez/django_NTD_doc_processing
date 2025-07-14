import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock dependencies before import
chromadb_mock = MagicMock()
chromadb_mock.utils = MagicMock()
chromadb_mock.utils.embedding_functions = MagicMock()
sys.modules['chromadb'] = chromadb_mock
sys.modules['chromadb.utils'] = chromadb_mock.utils
sys.modules['chromadb.utils.embedding_functions'] = chromadb_mock.utils.embedding_functions
sys.modules['sentence_transformers'] = MagicMock()

from documents.chroma_client import query_similar_documents, store_document_in_chromadb


class TestLightweightChroma:
    
    @patch('documents.chroma_client.collection')
    def test_store_document_in_chromadb(self, mock_collection):
        store_document_in_chromadb("test-id", "test text", "letter", {"name": ["John"]})
        mock_collection.add.assert_called_once()
    
    @patch('documents.chroma_client.collection')
    def test_query_similar_documents(self, mock_collection):
        mock_collection.query.return_value = {"documents": [["test"]], "metadatas": [[{"type": "letter"}]]}
        
        results = query_similar_documents("query text", top_k=5)
        assert "documents" in results
        mock_collection.query.assert_called_once()