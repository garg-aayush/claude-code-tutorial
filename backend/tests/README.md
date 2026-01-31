# Test Suite Documentation

## Overview

Comprehensive test suite for the Course Materials RAG System covering:
- **API Endpoints**: HTTP endpoint tests for FastAPI routes
- **CourseSearchTool**: Unit tests for search functionality
- **AIGenerator**: Unit tests for Claude API integration
- **RAG System**: Integration tests for system orchestration

## Quick Start

### Run All Tests
```bash
cd backend
uv run pytest tests/ -v
```

### Run Specific Test File
```bash
uv run pytest tests/api/test_endpoints.py -v
uv run pytest tests/unit/test_search_tools.py -v
uv run pytest tests/unit/test_ai_generator.py -v
uv run pytest tests/integration/test_rag_system.py -v
```

### Run by Marker
```bash
uv run pytest -m api -v           # API tests only
uv run pytest -m unit -v          # Unit tests only
uv run pytest -m integration -v   # Integration tests only
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=. --cov-report=term-missing
```

### Run Specific Test
```bash
uv run pytest tests/unit/test_search_tools.py::TestCourseSearchTool::test_execute_successful_search_no_filters -v
```

## Test Structure

```
tests/
├── conftest.py                          # Core fixtures (test_config, mock_rag_system, test_app, test_client)
├── fixtures/
│   ├── course_data_fixtures.py         # Sample courses and data
│   ├── vector_store_fixtures.py        # Mock VectorStore
│   └── anthropic_fixtures.py           # Mock Anthropic API
├── api/
│   ├── test_endpoints.py               # API endpoint tests (POST /api/query, GET /api/courses)
│   └── README.md                        # API testing documentation
├── unit/
│   ├── test_search_tools.py            # CourseSearchTool tests
│   └── test_ai_generator.py            # AIGenerator tests
└── integration/
    └── test_rag_system.py               # RAG System integration tests
```

## Available Fixtures

### Course Data Fixtures
- `sample_lesson()` - Single lesson
- `sample_lessons()` - List of lessons
- `sample_course()` - Complete course with lessons
- `course_without_lessons()` - Empty course
- `sample_course_chunks()` - Course chunks for vector operations
- `sample_sources()` - Source objects

### Vector Store Fixtures
- `mock_vector_store()` - Mocked VectorStore
- `sample_search_results()` - SearchResults with data
- `empty_search_results()` - Empty results
- `error_search_results()` - Results with error

### Anthropic Fixtures
- `mock_anthropic_client()` - Mock Anthropic client
- `anthropic_text_response()` - Direct text response
- `anthropic_tool_use_response()` - Tool use request
- `anthropic_final_response_after_tool()` - Synthesis after tool

### Core Fixtures
- `test_config()` - Test configuration
- `temp_dir()` - Temporary directory
- `mock_embedding_function()` - Mock embedding

### API Test Fixtures
- `mock_rag_system()` - Mock RAG system with pre-configured responses
- `test_app()` - Test FastAPI application without static file mounting
- `test_client()` - TestClient instance for HTTP requests

## Test Categories

### API Tests (24 tests)

Tests for FastAPI HTTP endpoints:
- POST /api/query endpoint (11 tests)
  - Session management
  - Request validation
  - Response structure
  - Error handling
  - Edge cases (special characters, long text)
- GET /api/courses endpoint (6 tests)
  - Course statistics retrieval
  - Empty results
  - Error handling
- API Integration (5 tests)
  - Multi-endpoint workflows
  - CORS configuration
  - Concurrent requests
- Request/Response Validation (2 tests)
  - Pydantic model validation

See `tests/api/README.md` for detailed API testing documentation.

### Unit Tests: CourseSearchTool (16 tests)

Tests for search tool functionality:
- Tool definition and schema
- Search with/without filters
- Empty result handling
- Error propagation
- Source tracking

### Unit Tests: AIGenerator (10 tests)

Tests for Claude API integration:
- Response generation
- Tool calling mechanism
- Message sequence
- Parameter passing
- History integration

### Integration Tests: RAG System (10 tests)

Tests for system orchestration:
- Component initialization
- Query execution
- Session management
- Source tracking
- End-to-end flow

## Writing New Tests

### Example Test
```python
def test_my_feature(mock_vector_store, sample_course):
    """Test description"""
    # Setup
    tool = CourseSearchTool(mock_vector_store)

    # Execute
    result = tool.execute(query="test")

    # Assert
    assert result is not None
    assert "expected content" in result
```

### Using Fixtures
```python
def test_with_fixtures(sample_course, mock_vector_store):
    # Fixtures are automatically injected
    assert sample_course.title == "Python Testing Course"
    mock_vector_store.search.return_value = SearchResults(...)
```

### Mocking
```python
from unittest.mock import Mock

def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = "result"
    assert mock_obj.method() == "result"
```

## Common Issues

### Issue: Import Errors
**Solution**: Ensure you're in the backend directory and using `uv run`
```bash
cd backend
uv run pytest tests/
```

### Issue: Fixture Not Found
**Solution**: Check if fixture is defined in conftest.py or imported properly

### Issue: Mock Not Working
**Solution**: Verify mock is configured before test execution
```python
mock_obj.method.return_value = expected_value
result = function_under_test(mock_obj)
```

## Coverage Goals

Target coverage for tested components:
- Critical components: >90%
- Core functionality: >80%
- Utility functions: >70%

Check coverage:
```bash
uv run pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Best Practices

1. **Test one thing**: Each test should verify one specific behavior
2. **Use descriptive names**: `test_execute_with_course_name_filter`
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock external dependencies**: Don't test ChromaDB or Anthropic API
5. **Use fixtures**: Reuse common test data
6. **Test edge cases**: Empty inputs, errors, boundary conditions

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    cd backend
    uv run pytest tests/ -v --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./backend/coverage.xml
```

## Debugging Tests

### Run with verbose output
```bash
uv run pytest tests/ -vv
```

### Show print statements
```bash
uv run pytest tests/ -s
```

### Run only failed tests
```bash
uv run pytest tests/ --lf
```

### Stop on first failure
```bash
uv run pytest tests/ -x
```

## Further Reading

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
