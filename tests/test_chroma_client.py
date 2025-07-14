# 🧪 Unit Tests: ChromaDB Client (store & query functions)

import uuid
import pytest
from unittest.mock import patch, MagicMock

from documents.chroma_client import (
    store_document_in_chromadb,
    query_similar_documents,
)


# 📄 Sample Document Fixture
@pytest.fixture
def sample_doc():
    """
    📄 Generate a sample document for testing.
    """
    return {
        "doc_id": str(uuid.uuid4()),
        "text": "Sample invoice from ACME Corp",
        "document_type": "invoice",
        "entities": {
            "vendor": "ACME Corp",
            "invoice_number": "12345",
            "tags": ["electronics", "delivery"]
        }
    }


# ✅ Test: Successful Document Storage
@patch("documents.chroma_client.logger")
@patch("documents.chroma_client.collection")
def test_store_document_success(mock_collection, mock_logger, sample_doc):
    """
    ✅ Ensure document storage calls collection.add() and logs appropriately.
    """
    store_document_in_chromadb(
        sample_doc["doc_id"],
        sample_doc["text"],
        sample_doc["document_type"],
        sample_doc["entities"]
    )

    mock_collection.add.assert_called_once()
    mock_logger.info.assert_any_call(
        f"📥 Storing document {sample_doc['doc_id']} in ChromaDB (type: {sample_doc['document_type']})"
    )
    mock_logger.info.assert_any_call(
        f"✅ Document {sample_doc['doc_id']} stored successfully."
    )


# ❌ Test: Document Storage Failure Handling
@patch("documents.chroma_client.logger")
@patch("documents.chroma_client.collection.add", side_effect=Exception("Simulated storage failure"))
def test_store_document_failure(mock_add, mock_logger, sample_doc):
    """
    ❌ Ensure errors during document storage are logged.
    """
    store_document_in_chromadb(
        sample_doc["doc_id"],
        sample_doc["text"],
        sample_doc["document_type"],
        sample_doc["entities"]
    )

    mock_logger.error.assert_called_once()
    assert "Failed to store document" in mock_logger.error.call_args[0][0]


# ✅ Test: Successful Similar Document Query
@patch("documents.chroma_client.logger")
@patch("documents.chroma_client.collection")
def test_query_similar_documents_success(mock_collection, mock_logger):
    """
    ✅ Ensure querying returns results and logs success.
    """
    mock_collection.query.return_value = {"ids": ["dummy-id"], "distances": [0.1]}

    result = query_similar_documents("Sample query", top_k=3)

    assert isinstance(result, dict)
    assert "ids" in result
    assert result["ids"] == ["dummy-id"]

    mock_logger.info.assert_any_call("🔍 Querying ChromaDB for top 3 similar documents.")
    mock_logger.info.assert_any_call("✅ Query completed successfully.")


# ❌ Test: Query Failure Handling
@patch("documents.chroma_client.logger")
@patch("documents.chroma_client.collection.query", side_effect=Exception("Simulated query failure"))
def test_query_similar_documents_failure(mock_query, mock_logger):
    """
    ❌ Ensure failed queries return empty results and log the error.
    """
    result = query_similar_documents("Failed query", top_k=2)

    assert result == {}
    mock_logger.error.assert_called_once()
    assert "Error querying ChromaDB" in mock_logger.error.call_args[0][0]
