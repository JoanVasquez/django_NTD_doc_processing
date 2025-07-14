from unittest.mock import MagicMock, patch

import pytest

from documents.chroma_client import query_similar_documents, store_document_in_chromadb


class TestChromaClient:
    
    @patch('documents.chroma_client.collection')
    @patch('documents.chroma_client.logger')
    def test_store_document_success(self, mock_logger, mock_collection):
        """Test successful document storage in ChromaDB"""
        doc_id = "test-doc-123"
        text = "This is test document text"
        document_type = "letter"
        entities = {"names": ["John Doe"], "locations": ["New York"]}
        
        store_document_in_chromadb(doc_id, text, document_type, entities)
        
        mock_collection.add.assert_called_once_with(
            ids=[doc_id],
            documents=[text],
            metadatas=[{
                "document_type": document_type,
                "names": "John Doe",
                "locations": "New York"
            }]
        )
        mock_logger.info.assert_called()
    
    @patch('documents.chroma_client.collection')
    @patch('documents.chroma_client.logger')
    def test_store_document_with_complex_entities(self, mock_logger, mock_collection):
        """Test document storage with complex entity structures"""
        doc_id = "test-doc-456"
        text = "Invoice document"
        document_type = "invoice"
        entities = {
            "vendor": ["ABC Corp", "XYZ Ltd"],
            "amount": "1000.50",
            "date": "2024-01-15"
        }
        
        store_document_in_chromadb(doc_id, text, document_type, entities)
        
        expected_metadata = {
            "document_type": "invoice",
            "vendor": "ABC Corp, XYZ Ltd",
            "amount": "1000.50",
            "date": "2024-01-15"
        }
        
        mock_collection.add.assert_called_once_with(
            ids=[doc_id],
            documents=[text],
            metadatas=[expected_metadata]
        )
    
    @patch('documents.chroma_client.collection')
    @patch('documents.chroma_client.logger')
    def test_store_document_error(self, mock_logger, mock_collection):
        """Test document storage with error"""
        mock_collection.add.side_effect = Exception("ChromaDB error")
        
        doc_id = "test-doc-error"
        text = "Test text"
        document_type = "memo"
        entities = {}
        
        store_document_in_chromadb(doc_id, text, document_type, entities)
        
        mock_logger.error.assert_called()
    
    @patch('documents.chroma_client.collection')
    @patch('documents.chroma_client.logger')
    def test_query_similar_documents_success(self, mock_logger, mock_collection):
        """Test successful document query"""
        mock_results = {
            "ids": [["doc1", "doc2"]],
            "distances": [[0.1, 0.3]],
            "documents": [["text1", "text2"]]
        }
        mock_collection.query.return_value = mock_results
        
        query_text = "search query"
        results = query_similar_documents(query_text, top_k=2)
        
        mock_collection.query.assert_called_once_with(
            query_texts=[query_text],
            n_results=2
        )
        assert results == mock_results
        mock_logger.info.assert_called()
    
    @patch('documents.chroma_client.collection')
    @patch('documents.chroma_client.logger')
    def test_query_similar_documents_error(self, mock_logger, mock_collection):
        """Test document query with error"""
        mock_collection.query.side_effect = Exception("Query error")
        
        query_text = "search query"
        results = query_similar_documents(query_text)
        
        assert results == {}
        mock_logger.error.assert_called()
    
    @patch('documents.chroma_client.collection')
    def test_query_similar_documents_default_params(self, mock_collection):
        """Test query with default parameters"""
        mock_collection.query.return_value = {"results": []}
        
        query_similar_documents("test query")
        
        mock_collection.query.assert_called_once_with(
            query_texts=["test query"],
            n_results=5
        )