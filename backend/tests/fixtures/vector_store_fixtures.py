"""Fixtures for vector store mocking"""
import pytest
from unittest.mock import Mock, MagicMock
from vector_store import SearchResults


@pytest.fixture
def mock_chroma_client():
    """Create a mock ChromaDB client"""
    client = Mock()
    client.get_or_create_collection = Mock(return_value=Mock())
    return client


@pytest.fixture
def sample_search_results():
    """Create sample SearchResults with data"""
    return SearchResults(
        documents=[
            "This is content from Python Testing Course about unit testing.",
            "This covers integration testing fundamentals.",
            "Advanced testing patterns and best practices."
        ],
        metadata=[
            {"course_title": "Python Testing Course", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "Python Testing Course", "lesson_number": 2, "chunk_index": 0},
            {"course_title": "MCP Introduction", "lesson_number": 1, "chunk_index": 0}
        ],
        distances=[0.2, 0.3, 0.4],
        error=None
    )


@pytest.fixture
def empty_search_results():
    """Create empty SearchResults"""
    return SearchResults(
        documents=[],
        metadata=[],
        distances=[],
        error=None
    )


@pytest.fixture
def error_search_results():
    """Create SearchResults with error"""
    return SearchResults(
        documents=[],
        metadata=[],
        distances=[],
        error="Database connection failed"
    )


@pytest.fixture
def mock_vector_store():
    """Create a fully mocked VectorStore"""
    mock_store = Mock()
    mock_store.search = Mock()
    mock_store.get_lesson_link = Mock(return_value="https://example.com/lesson")
    mock_store._resolve_course_name = Mock(return_value="Python Testing Course")
    mock_store.add_course_metadata = Mock()
    mock_store.add_course_content = Mock()
    mock_store.get_course_count = Mock(return_value=2)
    mock_store.get_existing_course_titles = Mock(return_value=["Python Testing Course", "MCP Introduction"])
    mock_store.clear_all_data = Mock()

    # Mock the collections
    mock_store.course_catalog = Mock()
    mock_store.course_content = Mock()

    return mock_store


@pytest.fixture
def configured_mock_vector_store(mock_vector_store, sample_search_results):
    """Create a pre-configured mock VectorStore with search results"""
    mock_vector_store.search.return_value = sample_search_results
    return mock_vector_store
