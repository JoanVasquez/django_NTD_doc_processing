# 🧪 API Integration Test: Document Processing Endpoint

import os

from django.test import Client, TestCase


class DocumentProcessAPITest(TestCase):
    """
    🧪 Test Case:
    Simulate API request to process a document image and verify response.
    """

    def setUp(self):
        """
        ⚙️ Set up test client before each test.
        """
        self.client = Client()

    def test_api_process_document(self):
        """
        📄 Test /api/process-document/ endpoint using sample image.
        """
        image_path = "docs-sm/invoice/00920717.jpg"
        self.assertTrue(os.path.exists(image_path), "❌ Test image does not exist.")

        with open(image_path, "rb") as image_file:
            # 📡 Simulate POST request with image file
            response = self.client.post(
                "/api/process-document/",
                {"file": image_file},
                format="multipart"
            )

        # ✅ Validate API Response
        self.assertEqual(response.status_code, 200, "❌ API did not return HTTP 200 OK.")
        data = response.json()
        self.assertIn("document_type", data, "❌ 'document_type' missing in API response.")
        self.assertIn("entities", data, "❌ 'entities' missing in API response.")
