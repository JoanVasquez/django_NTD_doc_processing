# 🧪 API Integration Test: Full Document Processing Flow

import os
import pytest


@pytest.mark.django_db
def test_full_document_processing_api(client):
    """
    📡 End-to-End API Test:
    - Upload image via /api/process-document/
    - Validate status code, document_type, and extracted entities.
    """
    image_path = "docs-sm/invoice/00920717.jpg"
    assert os.path.exists(image_path), "❌ Test image does not exist."

    # 📤 Simulate API POST request with image file
    with open(image_path, "rb") as image_file:
        response = client.post(
            "/api/process-document/",
            {"file": image_file},
            format="multipart"
        )

    # ✅ Validate Response Status
    assert response.status_code == 200, "❌ API did not return HTTP 200 OK."

    # 📊 Parse JSON response
    data = response.json()

    # 📄 Supported Document Types (Mirror from backend)
    SUPPORTED_DOC_TYPES = [
        "invoice", "advertisement", "form", "resume",
        "file_folder", "budget", "email", "scientific_report",
        "scientific_publication", "handwritten", "memo",
        "letter", "presentation", "questionnaire", "news_article",
        "specification"
    ]

    # ✅ Validate document type
    assert data["document_type"] in SUPPORTED_DOC_TYPES, \
        f"❌ Unexpected document_type: {data['document_type']}"

    # ✅ Validate entities
    assert isinstance(data["entities"], dict), "❌ Entities must be returned as a dictionary."
