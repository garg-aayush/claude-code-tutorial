"""Central fixture definitions for test suite"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from config import Config
from tests.fixtures.anthropic_fixtures import *

# Import fixtures from fixture modules
from tests.fixtures.course_data_fixtures import *
from tests.fixtures.vector_store_fixtures import *


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


# API Test Fixtures


@pytest.fixture
def mock_rag_system():
    """Create a mock RAG system for API testing"""
    from models import Source

    mock_system = MagicMock()

    # Mock session manager
    mock_system.session_manager = MagicMock()
    mock_system.session_manager.create_session.return_value = "test-session-123"

    # Mock query method - returns tuple of (answer, list of Source objects)
    mock_system.query.return_value = (
        "This is a test answer about Python programming.",
        [
            Source(
                text="Introduction to Python - Lesson 1",
                url="https://example.com/python/lesson1"
            )
        ]
    )

    # Mock course analytics method
    mock_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Introduction to Python", "Advanced JavaScript"]
    }

    # Mock add_course_folder method
    mock_system.add_course_folder.return_value = (2, 10)

    return mock_system


@pytest.fixture
def test_app(mock_rag_system):
    """Create a test FastAPI app without static file mounting"""
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional
    from models import Source

    # Create test app
    app = FastAPI(title="Course Materials RAG System - Test", root_path="")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Pydantic models
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[Source]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # API endpoints
    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()

            answer, sources = mock_rag_system.query(request.query, session_id)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client for making API requests"""
    from fastapi.testclient import TestClient
    return TestClient(test_app)
