# API Endpoint Tests

Comprehensive test suite for FastAPI endpoints in the Course Materials RAG System.

## Overview

This directory contains API-level tests that verify the HTTP endpoints work correctly with proper request/response handling, error management, and data validation.

## Test Coverage

**24 API tests** covering:
- **POST /api/query** - Query processing endpoint (11 tests)
- **GET /api/courses** - Course analytics endpoint (6 tests)
- **API Integration** - Cross-endpoint workflows (5 tests)
- **Request/Response Validation** - Pydantic model validation (2 tests)

## Running Tests

```bash
# Run all API tests
uv run pytest tests/api/ -v

# Run with marker
uv run pytest -m api -v

# Run specific test class
uv run pytest tests/api/test_endpoints.py::TestQueryEndpoint -v

# Run single test
uv run pytest tests/api/test_endpoints.py::TestQueryEndpoint::test_query_with_existing_session -v
```

## Test Structure

### TestQueryEndpoint
Tests for POST /api/query endpoint:
- Session management (with/without session ID)
- Request validation (missing fields, invalid JSON)
- Response structure validation
- Error handling (RAG system errors)
- Edge cases (empty strings, special characters, long text)

### TestCoursesEndpoint
Tests for GET /api/courses endpoint:
- Successful retrieval of course statistics
- Response structure validation
- Empty result handling
- Error handling
- Query parameter behavior

### TestAPIIntegration
Integration tests across multiple endpoints:
- Multiple queries with same session
- CORS configuration
- Content-type headers
- Concurrent request handling
- Cross-endpoint workflows

### TestAPIValidation
Pydantic model validation tests:
- QueryResponse model validation
- CourseStats model validation
- Source model validation

## Test Fixtures

Key fixtures defined in `tests/conftest.py`:

### `mock_rag_system`
Mock RAG system with pre-configured responses:
- Returns sample answers and Source objects
- Mocks session management
- Mocks course analytics

### `test_app`
Test FastAPI application without static file mounting:
- Includes all API endpoints
- Uses mock_rag_system for backend
- Configured with CORS middleware

### `test_client`
TestClient instance for making HTTP requests:
- Pre-configured with test_app
- Supports all HTTP methods
- Returns response objects for validation

## Response Models

### QueryResponse
```python
{
    "answer": str,          # AI-generated response
    "sources": List[Source], # List of source citations
    "session_id": str       # Session identifier
}
```

### Source
```python
{
    "text": str,            # Display text (e.g., "Course Title - Lesson 1")
    "url": Optional[str]    # Lesson link URL
}
```

### CourseStats
```python
{
    "total_courses": int,   # Number of courses
    "course_titles": List[str]  # List of course titles
}
```

## Error Handling

Tests verify proper error handling for:
- 422 Unprocessable Entity - Invalid request data
- 500 Internal Server Error - Backend/RAG system errors

## Notes

- All tests use mocked dependencies (no real API calls, database connections)
- TestClient doesn't trigger CORS middleware, so CORS tests verify endpoint functionality
- Tests follow Arrange-Act-Assert pattern
- Source objects use the simplified model (text + optional url) from `models.py`

## Adding New Tests

When adding new API tests:
1. Use existing fixtures from `conftest.py`
2. Follow the class-based organization (TestQueryEndpoint, TestCoursesEndpoint, etc.)
3. Add `@pytest.mark.api` decorator
4. Follow Arrange-Act-Assert pattern
5. Mock external dependencies
6. Test both success and error cases
