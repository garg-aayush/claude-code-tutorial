# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Course Materials RAG System - A full-stack web application that enables users to query course materials using semantic search and AI-powered responses with Claude's tool-calling capabilities.

## Commands

### Run the Application
```bash
./run.sh
# Or manually:
cd backend && uv run uvicorn app:app --reload --port 8000
```

### Install Dependencies
```bash
uv sync
```

### Access Points
- Web Interface: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Architecture

### RAG Pipeline Flow
```
User Query → FastAPI → RAG System → Claude API (with tools)
                                         ↓
                              Tool: search_course_content
                                         ↓
                              Vector Store (ChromaDB)
                                         ↓
                              Return chunks → Claude synthesizes → Response
```

### Key Components

**Backend (`backend/`)**
- `app.py` - FastAPI entry point, REST endpoints (`/api/query`, `/api/courses`)
- `rag_system.py` - Main orchestrator coordinating all components
- `ai_generator.py` - Claude API integration with tool-use handling (two-step: tool decision → execution → synthesis)
- `vector_store.py` - ChromaDB wrapper with two collections: `course_catalog` (metadata) and `course_content` (chunks)
- `document_processor.py` - Parses course documents, extracts metadata, sentence-aware chunking with overlap
- `search_tools.py` - Tool definitions for Claude's tool-calling, `CourseSearchTool` implementation
- `session_manager.py` - Conversation history management
- `config.py` - Configuration (model, chunk size, embedding model)

**Frontend (`frontend/`)**
- Vanilla JavaScript with markdown rendering (marked.js)
- Chat interface with session management and collapsible sources

### Data Flow for a Query
1. Frontend POSTs to `/api/query` with query and optional session_id
2. RAG System builds prompt with conversation history
3. Claude evaluates if search tool is needed
4. If needed: `search_course_content` tool queries ChromaDB with semantic search
5. Course name resolution uses fuzzy vector matching in catalog collection
6. Results formatted with course/lesson context
7. Claude synthesizes final response from search results
8. Sources tracked and returned to frontend

### Document Processing
- Expected format: Course metadata header (title, link, instructor) followed by lessons
- Chunks: 800 chars with 100 char overlap, sentence-aware splitting
- Each chunk tagged with course title, lesson number, chunk index

### Configuration (`backend/config.py`)
- `ANTHROPIC_MODEL`: Claude model (default: claude-sonnet-4-20250514)
- `EMBEDDING_MODEL`: SentenceTransformer model (default: all-MiniLM-L6-v2)
- `CHUNK_SIZE`: 800, `CHUNK_OVERLAP`: 100
- `MAX_RESULTS`: 5, `MAX_HISTORY`: 2

## Environment Variables

Required:
- `ANTHROPIC_API_KEY` - Set in environment or `.env` file

## Development Guidelines

- Always use `uv` to run the server, manage all dependencies, and run Python files. Do not use `pip` or `python` directly (use `uv run` instead).

### Code Quality Tools

The project includes automated code quality tools:

**Formatting:**
- `./scripts/format.sh` - Auto-format code with black and isort
- Run before committing to ensure consistent formatting

**Linting:**
- `./scripts/lint.sh` - Check code quality (black, isort, flake8)
- `./scripts/type-check.sh` - Run type checking with mypy (optional)
- `./scripts/check.sh` - Complete checks (linting + tests)

**Configuration:**
- Black: 88 char lines, Python 3.13
- isort: Black-compatible profile
- flake8: PEP 8 compliance with black compatibility
- mypy: Optional type checking (lenient settings)

See `scripts/README.md` for detailed usage.

## Testing

### Test Suite Overview
Comprehensive test suite with 36 tests covering core RAG system components (100% pass rate):
- **Unit Tests**: CourseSearchTool (16 tests), AIGenerator (10 tests)
- **Integration Tests**: RAG System orchestration (10 tests)
- **Coverage**: AIGenerator (100%), Models (100%), Config (100%), CourseSearchTool (68%)

### Running Tests
```bash
# Run all tests
cd backend && uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=term-missing

# Run specific suite
uv run pytest tests/unit/test_search_tools.py -v      # CourseSearchTool tests
uv run pytest tests/unit/test_ai_generator.py -v      # AIGenerator tests
uv run pytest tests/integration/test_rag_system.py -v # RAG integration tests
```

### Test Structure
- `backend/tests/conftest.py` - Core fixtures (test_config, mock objects)
- `backend/tests/fixtures/` - Reusable test data (courses, mock VectorStore, mock Anthropic API)
- `backend/tests/unit/` - Unit tests for individual components
- `backend/tests/integration/` - Integration tests for system orchestration

### When Writing Tests
- Use existing fixtures from `tests/fixtures/` for consistent test data
- Mock external dependencies (ChromaDB, Anthropic API) - never test against real services
- Follow Arrange-Act-Assert pattern
- Test both happy paths and error cases

### Detailed Documentation
See `backend/tests/README.md` for comprehensive testing guide, fixture reference, and examples.
