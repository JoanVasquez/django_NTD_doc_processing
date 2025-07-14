import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_heavy_operations():
    """Auto-mock heavy operations for all tests"""
    # Mock modules that might not be installed
    mock_modules = {
        'transformers': MagicMock(),
        'sentence_transformers': MagicMock(),
        'chromadb': MagicMock(),
        'pytesseract': MagicMock()
    }
    
    for module_name, mock_module in mock_modules.items():
        sys.modules[module_name] = mock_module
    
    yield
    
    # Clean up
    for module_name in mock_modules:
        if module_name in sys.modules:
            del sys.modules[module_name]

@pytest.fixture
def mock_file_operations():
    """Mock file I/O operations"""
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open'):
            yield

@pytest.fixture
def disable_logging():
    """Disable logging during tests"""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)