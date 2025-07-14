import logging
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from documents.ocr import extract_text_from_image
from documents.classifier import predict_document_type
from documents.extractor import extract_entities
from documents.chroma_client import store_document_in_chromadb

# 🛠️ Logger Setup
logger = logging.getLogger(__name__)

def clean_text_preview(text: str, max_length: int = 200) -> str:
    """Generate a readable preview from OCR text, skipping garbage."""
    print(text)
    import re

    words = text.split()
    # Only keep words that are mostly alphabetic and at least 3 letters
    filtered = [w for w in words if len(w) >= 3 and sum(c.isalpha() for c in w) / len(w) > 0.7]

    # Join the first 30 filtered words for preview
    preview = ' '.join(filtered[:30])

    # Fallback: If not enough readable words, clean up the text
    if len(preview) < 20:
        preview = re.sub(r'[^a-zA-Z0-9\s.,!?;:()-]', ' ', text)
        preview = re.sub(r'\s+', ' ', preview.strip())
        preview = ' '.join(preview.split()[:30])

    # Truncate to max_length
    if len(preview) > max_length:
        preview = preview[:max_length].rsplit(' ', 1)[0] + "..."

    # Final fallback if preview is still garbage
    if not preview or sum(c.isalpha() for c in preview) < 10:
        return "[OCR text quality too poor for preview]"

    return preview

class DocumentProcessView(APIView):
    """
    API endpoint to upload a document, extract its type + entities, and store in ChromaDB.
    """
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Process document: OCR, classify type, extract entities",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="Image file to process",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Document processed successfully",
                examples={
                    "application/json": {
                        "document_id": "uuid-string",
                        "document_type": "letter",
                        "entities": {
                            "names": ["John Doe"],
                            "locations": ["New York, NY"]
                        }
                    }
                }
            ),
            400: "No file uploaded",
            500: "Internal server error"
        }
    )
    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            logger.warning("API called without uploading a file.")
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        temp_path = f"/tmp/{file.name}"

        try:
            logger.info(f"Received document upload: {file.name}")

            # Save uploaded file temporarily
            with open(temp_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            logger.info(f"Saved uploaded file to: {temp_path}")

            # 1️⃣ Extract text using OCR
            text = extract_text_from_image(temp_path)
            logger.info("OCR completed successfully.")

            # 2️⃣ Classify document type
            doc_type = predict_document_type(text)
            logger.info(f"Predicted document type: {doc_type}")

            # 3️⃣ Extract entities
            entities = extract_entities(doc_type, text)
            logger.info(f"Extracted {len(entities)} entity fields.")

            # 4️⃣ Store in ChromaDB
            doc_id = str(uuid.uuid4())
            store_document_in_chromadb(
                doc_id=doc_id,
                text=text,
                document_type=doc_type,
                entities=entities
            )

            logger.info(f"Stored document {doc_id} in storage.")

            result = {
                "document_id": doc_id,
                "document_type": doc_type,
                "entities": entities
            }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing uploaded document: {e}", exc_info=True)
            return Response({'error': 'Internal server error while processing document.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
