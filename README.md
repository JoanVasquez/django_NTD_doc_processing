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
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests

```bash
# Fast tests (lightweight only) - Recommended for development
python run_tests_fast.py

# Or using pytest directly
python -m pytest tests/test_*_lightweight.py -v --tb=short

# Full test suite (slower - includes integration tests)
python -m pytest tests/ --tb=short

# Install test dependencies first
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### Type Checking

This project enforces strict typing with mypy:

```bash
# Run type checking
python run_type_check.py

# Or directly with mypy
python -m mypy api documents doc_processor

# Install type checking dependencies
pip install -r requirements.dev.txt
```

### Code Quality

Code linting and import sorting:

```bash
# Run all code quality checks
python run_lint.py

# Fix import sorting
python -m isort api documents doc_processor

# Run linting only
python -m flake8 api documents doc_processor
```

### Pre-commit Hooks

Setup automatic code quality checks on commit:

```bash
# Install pre-commit hooks
python setup_precommit.py

# Or manually
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

### Adding New Document Types

1. Add training data to `docs-sm/new_type/`
2. Update `ENTITY_MAPPING` in `documents/extractor.py`
3. Retrain the classifier model

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

## Technology Stack

- **Backend**: Django, Django REST Framework
- **OCR**: Tesseract, OpenCV
- **Vector DB**: ChromaDB
- **Documentation**: Swagger/OpenAPI (drf-yasg)

## License

MIT License