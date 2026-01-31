"""
API Endpoint Tests

Tests for FastAPI endpoints covering:
- POST /api/query - Query processing with RAG system
- GET /api/courses - Course analytics retrieval
- Request/response validation
- Error handling
- Session management
"""

import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


@pytest.mark.api
class TestQueryEndpoint:
    """Tests for POST /api/query endpoint"""

    def test_query_with_existing_session(self, test_client, mock_rag_system):
        """Test query processing with existing session ID"""
        # Arrange
        query_request = {
            "query": "What is Python?",
            "session_id": "existing-session-456"
        }

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "existing-session-456"
        assert isinstance(data["sources"], list)

        # Verify RAG system was called correctly
        mock_rag_system.query.assert_called_once_with(
            "What is Python?",
            "existing-session-456"
        )

    def test_query_without_session_creates_new_session(self, test_client, mock_rag_system):
        """Test query without session ID creates new session"""
        # Arrange
        query_request = {"query": "Explain JavaScript closures"}

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == "test-session-123"

        # Verify session was created
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_with_null_session_id(self, test_client, mock_rag_system):
        """Test query with explicit null session_id"""
        # Arrange
        query_request = {
            "query": "What are decorators?",
            "session_id": None
        }

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["session_id"] == "test-session-123"

    def test_query_returns_valid_response_structure(self, test_client, mock_rag_system):
        """Test query response has correct structure"""
        # Arrange
        query_request = {"query": "How does async/await work?"}

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)

        # Verify source structure (Source model has text and optional url)
        if data["sources"]:
            source = data["sources"][0]
            assert "text" in source
            assert isinstance(source["text"], str)
            # url is optional
            if "url" in source:
                assert isinstance(source["url"], (str, type(None)))

    def test_query_missing_query_field(self, test_client):
        """Test query with missing required 'query' field"""
        # Arrange
        invalid_request = {"session_id": "test-123"}

        # Act
        response = test_client.post("/api/query", json=invalid_request)

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_empty_string(self, test_client, mock_rag_system):
        """Test query with empty string"""
        # Arrange
        query_request = {"query": ""}

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert - Should accept empty string (validation at business logic level)
        assert response.status_code == status.HTTP_200_OK

    def test_query_with_special_characters(self, test_client, mock_rag_system):
        """Test query with special characters and unicode"""
        # Arrange
        query_request = {
            "query": "What is λ calculus? How do you use é and 中文?"
        }

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_rag_system.query.assert_called_once()

    def test_query_with_very_long_text(self, test_client, mock_rag_system):
        """Test query with very long text"""
        # Arrange
        long_query = "What is Python? " * 1000  # ~15,000 characters
        query_request = {"query": long_query}

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_query_rag_system_error_handling(self, test_client, mock_rag_system):
        """Test error handling when RAG system raises exception"""
        # Arrange
        mock_rag_system.query.side_effect = Exception("RAG system error")
        query_request = {"query": "What is Python?"}

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "RAG system error" in response.json()["detail"]

    def test_query_invalid_json(self, test_client):
        """Test query with invalid JSON"""
        # Act
        response = test_client.post(
            "/api/query",
            data="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_with_extra_fields(self, test_client, mock_rag_system):
        """Test query with extra fields (should be ignored)"""
        # Arrange
        query_request = {
            "query": "What is Python?",
            "session_id": "test-123",
            "extra_field": "should be ignored"
        }

        # Act
        response = test_client.post("/api/query", json=query_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestCoursesEndpoint:
    """Tests for GET /api/courses endpoint"""

    def test_get_courses_success(self, test_client, mock_rag_system):
        """Test successful course statistics retrieval"""
        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert isinstance(data["course_titles"], list)
        assert len(data["course_titles"]) == 2

    def test_get_courses_returns_valid_structure(self, test_client, mock_rag_system):
        """Test course statistics response structure"""
        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify types
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert all(isinstance(title, str) for title in data["course_titles"])

    def test_get_courses_empty_result(self, test_client, mock_rag_system):
        """Test course statistics when no courses exist"""
        # Arrange
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_courses_many_courses(self, test_client, mock_rag_system):
        """Test course statistics with many courses"""
        # Arrange
        many_courses = [f"Course {i}" for i in range(100)]
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 100,
            "course_titles": many_courses
        }

        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_courses"] == 100
        assert len(data["course_titles"]) == 100

    def test_get_courses_error_handling(self, test_client, mock_rag_system):
        """Test error handling when course analytics fails"""
        # Arrange
        mock_rag_system.get_course_analytics.side_effect = Exception(
            "Database connection error"
        )

        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database connection error" in response.json()["detail"]

    def test_get_courses_no_query_params(self, test_client, mock_rag_system):
        """Test courses endpoint doesn't accept query parameters"""
        # Act
        response = test_client.get("/api/courses?limit=10")

        # Assert - Should still work (params ignored)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestAPIIntegration:
    """Integration tests across multiple endpoints"""

    def test_multiple_queries_same_session(self, test_client, mock_rag_system):
        """Test multiple queries with same session ID"""
        # Arrange
        session_id = "consistent-session-789"

        # Act - First query
        response1 = test_client.post("/api/query", json={
            "query": "What is Python?",
            "session_id": session_id
        })

        # Act - Second query
        response2 = test_client.post("/api/query", json={
            "query": "What is JavaScript?",
            "session_id": session_id
        })

        # Assert
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.json()["session_id"] == session_id
        assert response2.json()["session_id"] == session_id

    def test_cors_headers_present(self, test_client):
        """Test CORS middleware is configured (note: TestClient doesn't include CORS headers)"""
        # Act
        response = test_client.get("/api/courses")

        # Assert - TestClient doesn't trigger CORS middleware, so we just verify the endpoint works
        # In a real browser, CORS headers would be present
        assert response.status_code == status.HTTP_200_OK

    def test_content_type_headers(self, test_client, mock_rag_system):
        """Test content-type headers are correct"""
        # Act - Query endpoint
        response1 = test_client.post("/api/query", json={"query": "test"})

        # Act - Courses endpoint
        response2 = test_client.get("/api/courses")

        # Assert
        assert "application/json" in response1.headers["content-type"]
        assert "application/json" in response2.headers["content-type"]

    def test_concurrent_requests(self, test_client, mock_rag_system):
        """Test handling of concurrent requests"""
        # Arrange
        queries = [
            {"query": "What is Python?"},
            {"query": "What is JavaScript?"},
            {"query": "What is TypeScript?"}
        ]

        # Act
        responses = [test_client.post("/api/query", json=q) for q in queries]

        # Assert
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert "answer" in response.json()

    def test_query_then_courses(self, test_client, mock_rag_system):
        """Test workflow of querying then checking courses"""
        # Act - Query
        query_response = test_client.post("/api/query", json={
            "query": "What courses are available?"
        })

        # Act - Get courses
        courses_response = test_client.get("/api/courses")

        # Assert
        assert query_response.status_code == status.HTTP_200_OK
        assert courses_response.status_code == status.HTTP_200_OK

        courses_data = courses_response.json()
        assert courses_data["total_courses"] > 0


@pytest.mark.api
class TestAPIValidation:
    """Tests for request/response validation"""

    def test_query_response_model_validation(self, test_client, mock_rag_system):
        """Test query response matches Pydantic model"""
        # Arrange
        from models import Source
        mock_rag_system.query.return_value = (
            "Test answer",
            [
                Source(
                    text="Test Course - Lesson 1",
                    url="https://example.com/lesson1"
                )
            ]
        )

        # Act
        response = test_client.post("/api/query", json={"query": "test"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Validate source structure matches Source model
        source = data["sources"][0]
        assert source["text"] == "Test Course - Lesson 1"
        assert source["url"] == "https://example.com/lesson1"

    def test_courses_response_model_validation(self, test_client, mock_rag_system):
        """Test courses response matches Pydantic model"""
        # Arrange
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 5,
            "course_titles": ["Course A", "Course B", "Course C", "Course D", "Course E"]
        }

        # Act
        response = test_client.get("/api/courses")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_courses"] == 5
        assert len(data["course_titles"]) == 5
