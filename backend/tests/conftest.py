"""Central fixture definitions for test suite"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from config import Config

# Import fixtures from fixture modules
from tests.fixtures.course_data_fixtures import *
from tests.fixtures.vector_store_fixtures import *
from tests.fixtures.anthropic_fixtures import *


@pytest.fixture
def test_config():
    """Create a test configuration"""
    config = Config()
    config.ANTHROPIC_API_KEY = "test-api-key"
    config.ANTHROPIC_MODEL = "claude-haiku-4-5"
    config.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    config.CHUNK_SIZE = 800
    config.CHUNK_OVERLAP = 100
    config.MAX_RESULTS = 5
    config.MAX_HISTORY = 2
    config.CHROMA_PATH = "./test_chroma_db"
    return config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_embedding_function():
    """Create a mock embedding function for testing"""
    mock_func = Mock()
    mock_func.return_value = [[0.1, 0.2, 0.3, 0.4, 0.5]]  # Simple mock embedding
    return mock_func
