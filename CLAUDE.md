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
