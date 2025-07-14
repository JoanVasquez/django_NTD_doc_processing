# Document Processor API

A Django-based document processing system that performs OCR, document classification, and entity extraction using machine learning models and ChromaDB for vector storage.

## Features

- **OCR Text Extraction** - Extract text from images using Tesseract
- **Document Classification** - Classify documents into types (letter, invoice, form, etc.)
- **Entity Extraction** - Extract names, organizations, and locations from text
- **Vector Storage** - Store document embeddings in ChromaDB for similarity search
- **REST API** - Simple API for document processing

## Configuration

### Environment Variables

Create a `.env` file:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000
```

## Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to project**
   ```bash
   cd doc_processor
   ```

2. **Start the application**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the API**
   - API: http://localhost:8000/api/process-document/
   - ChromaDB: http://localhost:8001

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Start development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## API Usage

### Process Document

**Endpoint:** `POST /api/process-document/`

**Request:** Upload an image file using form-data with key `file`

**Response:**
```json
{
    "document_id": "uuid-string",
    "document_type": "letter",
    "entities": {
        "sender_organization": ["Company Name"],
        "names": ["John Doe"],
        "locations": ["New York, NY"]
    }
}
```

### Example with curl

```bash
curl -X POST -F "file=@document.jpg" http://localhost:8000/api/process-document/
```

## Project Structure

```
doc_processor/
├── api/                    # REST API endpoints
├── documents/              # Core processing logic
│   ├── ocr.py             # OCR text extraction
│   ├── classifier.py      # Document classification
│   ├── extractor.py       # Entity extraction
│   └── chroma_client.py   # Vector database client
├── docs-sm/               # Training data
├── tests/                 # Test files
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Development container
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests

```bash
# Local - Install test dependencies first
pip install -r requirements.txt
pip install -r requirements.dev.txt
python -m pytest

# Docker (containers must be running first)
docker-compose up -d
docker-compose exec web python -m pytest
```

**Note**: For local testing, you don't need Docker containers running. For Docker testing, start containers first with `docker-compose up -d`.

### Adding New Document Types

1. Add training data to `docs-sm/new_type/`
2. Update `ENTITY_MAPPING` in `documents/extractor.py`
3. Retrain the classifier model

## Troubleshooting

### Common Issues

- **Permission errors**: Ensure Docker has proper file permissions
- **Model loading slow**: First startup takes time to download ML models
- **Empty entities**: Check OCR text quality and entity extraction patterns

### Logs

```bash
# View application logs
docker logs doc_processor_web

# View ChromaDB logs  
docker logs doc_processor_chromadb
```

## Architecture Overview

### Design Philosophy
The system follows a **modular, pipeline-based architecture** designed for scalability, maintainability, and extensibility. Each component has a single responsibility and can be independently tested and modified.

### Core Components

#### 1. **API Layer** (`api/`)
- **REST API** using Django REST Framework
- **Swagger/OpenAPI** documentation for interactive testing
- **File upload handling** with multipart form support
- **Error handling** with structured JSON responses

#### 2. **Document Processing Pipeline** (`documents/`)
```
Image Upload → OCR → Classification → Entity Extraction → Vector Storage
```

- **OCR Module** (`ocr.py`): Tesseract + OpenCV for text extraction
  - Image preprocessing for better OCR accuracy
  - Caching system to avoid reprocessing
  - Error handling for invalid images

- **Classifier** (`classifier.py`): ML-based document type detection
  - TF-IDF vectorization + Logistic Regression
  - Supports 15+ document types (invoice, letter, form, etc.)
  - Auto-training from folder structure

- **Entity Extractor** (`extractor.py`): Multi-layered entity extraction
  - **Regex patterns** for document-specific entities
  - **HuggingFace NER** (BERT-based) for general entities
  - **NLTK processing** with spell correction for noisy OCR
  - **Domain mapping** to convert generic entities to document-specific fields

#### 3. **Vector Database** (`chroma_client.py`)
- **ChromaDB integration** for semantic search
- **Sentence embeddings** for document similarity
- **Metadata storage** with extracted entities
- **Scalable retrieval** for large document collections

### Design Choices

#### **Why Django + DRF?**
- **Rapid development** with built-in admin, ORM, and middleware
- **REST API** with automatic serialization and validation
- **Extensible** for future features (user auth, permissions, etc.)

#### **Why Multi-layered Entity Extraction?**
- **Regex**: Fast, domain-specific patterns (names, dates, codes)
- **BERT NER**: General entity recognition with high accuracy
- **NLTK**: Spell correction for noisy OCR text
- **Fallback system**: Ensures entities are always extracted

#### **Why ChromaDB?**
- **Vector similarity search** for document retrieval
- **Embedded database** - no separate server required
- **Automatic embeddings** with sentence-transformers
- **Metadata filtering** combined with semantic search

#### **Why Modular Architecture?**
- **Single Responsibility**: Each module has one clear purpose
- **Testability**: 86%+ test coverage with isolated unit tests
- **Maintainability**: Easy to modify individual components
- **Extensibility**: Add new document types or extraction methods easily

### Data Flow

1. **Upload**: Client sends image via REST API
2. **OCR**: Extract text using Tesseract with preprocessing
3. **Classification**: Predict document type using trained ML model
4. **Extraction**: Extract entities using multi-layered approach
5. **Storage**: Store document + entities in ChromaDB with embeddings
6. **Response**: Return structured JSON with extracted information

### Scalability Considerations

- **Stateless API**: Easy horizontal scaling
- **Caching**: OCR results cached to avoid reprocessing
- **Async-ready**: Django structure supports async processing
- **Database**: ChromaDB handles large-scale vector operations
- **Containerized**: Docker deployment for consistent environments

## Technology Stack

- **Backend**: Django, Django REST Framework
- **OCR**: Tesseract, OpenCV
- **ML**: scikit-learn, Transformers, NLTK
- **Vector DB**: ChromaDB
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Containerization**: Docker, Docker Compose

## License

MIT License