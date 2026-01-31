"""Integration tests for RAG System"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from models import Source
from rag_system import RAGSystem


class TestRAGSystem:
    """Test RAG System integration"""

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_rag_system_initialization(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test RAGSystem component setup"""
        # Create RAG system
        rag = RAGSystem(test_config)

        # Verify all components initialized
        mock_doc_processor_cls.assert_called_once_with(
            test_config.CHUNK_SIZE, test_config.CHUNK_OVERLAP
        )
        mock_vector_store_cls.assert_called_once_with(
            test_config.CHROMA_PATH,
            test_config.EMBEDDING_MODEL,
            test_config.MAX_RESULTS,
        )
        mock_ai_generator_cls.assert_called_once_with(
            test_config.ANTHROPIC_API_KEY, test_config.ANTHROPIC_MODEL
        )
        mock_session_manager_cls.assert_called_once_with(test_config.MAX_HISTORY)

        # Verify tools registered
        assert len(rag.tool_manager.tools) == 2
        assert "search_course_content" in rag.tool_manager.tools
        assert "get_course_outline" in rag.tool_manager.tools

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_without_session(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test basic query without session"""
        rag = RAGSystem(test_config)

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "This is the answer"

        # Mock tool manager sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query
        response, sources = rag.query(query="What is testing?", session_id=None)

        # Verify response
        assert response == "This is the answer"
        assert sources == []

        # Verify AI called correctly
        mock_ai.generate_response.assert_called_once()
        call_kwargs = mock_ai.generate_response.call_args.kwargs
        assert "What is testing?" in call_kwargs["query"]
        assert call_kwargs["conversation_history"] is None
        assert call_kwargs["tools"] is not None
        assert call_kwargs["tool_manager"] is not None

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_with_new_session(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test query with new session"""
        rag = RAGSystem(test_config)

        # Mock session manager
        mock_session = mock_session_manager_cls.return_value
        mock_session.get_conversation_history.return_value = None

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Answer"

        # Mock sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query with session_id
        response, sources = rag.query(query="Test", session_id="session_123")

        # Verify history was requested (returns None for new session)
        mock_session.get_conversation_history.assert_called_once_with("session_123")

        # Verify exchange was added
        mock_session.add_exchange.assert_called_once_with(
            "session_123", "Test", "Answer"
        )

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_with_existing_session(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test query with existing conversation history"""
        rag = RAGSystem(test_config)

        # Mock session with history
        mock_session = mock_session_manager_cls.return_value
        history = "User: Previous question\nAssistant: Previous answer"
        mock_session.get_conversation_history.return_value = history

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Follow-up answer"

        # Mock sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query
        response, sources = rag.query(query="Follow-up", session_id="session_123")

        # Verify history was passed to AI
        call_kwargs = mock_ai.generate_response.call_args.kwargs
        assert call_kwargs["conversation_history"] == history

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_sources_retrieval(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
        sample_sources,
    ):
        """Test source tracking and retrieval"""
        rag = RAGSystem(test_config)

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Answer with sources"

        # Mock tool manager to return sources
        rag.tool_manager.get_last_sources = Mock(return_value=sample_sources)
        rag.tool_manager.reset_sources = Mock()

        # Execute query
        response, sources = rag.query(query="Test")

        # Verify sources retrieved
        assert len(sources) == 2
        assert all(isinstance(s, Source) for s in sources)
        assert sources[0].text == "Python Testing Course - Lesson 1"

        # Verify sources reset after retrieval
        rag.tool_manager.reset_sources.assert_called_once()

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_tool_integration(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test that tools are properly integrated"""
        rag = RAGSystem(test_config)

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Answer"

        # Mock sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query
        rag.query(query="Test")

        # Verify tools were passed
        call_kwargs = mock_ai.generate_response.call_args.kwargs
        tools = call_kwargs["tools"]
        assert len(tools) == 2

        # Verify tool_manager passed
        assert call_kwargs["tool_manager"] == rag.tool_manager

        # Verify tool definitions
        tool_names = [t["name"] for t in tools]
        assert "search_course_content" in tool_names
        assert "get_course_outline" in tool_names

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_prompt_construction(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test prompt format passed to AI"""
        rag = RAGSystem(test_config)

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Answer"

        # Mock sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query
        rag.query(query="What is unit testing?")

        # Verify prompt format
        call_kwargs = mock_ai.generate_response.call_args.kwargs
        prompt = call_kwargs["query"]
        assert "Answer this question about course materials:" in prompt
        assert "What is unit testing?" in prompt

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_history_updates(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test session history is updated after query"""
        rag = RAGSystem(test_config)

        # Mock session
        mock_session = mock_session_manager_cls.return_value
        mock_session.get_conversation_history.return_value = None

        # Mock AI response
        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "The answer is 42"

        # Mock sources
        rag.tool_manager.get_last_sources = Mock(return_value=[])

        # Execute query with session
        rag.query(query="What is the answer?", session_id="sess_1")

        # Verify session was updated with exchange
        mock_session.add_exchange.assert_called_once_with(
            "sess_1", "What is the answer?", "The answer is 42"
        )

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_query_orchestration_flow(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
        sample_sources,
    ):
        """Test end-to-end query orchestration"""
        rag = RAGSystem(test_config)

        # Setup mocks for full flow
        mock_session = mock_session_manager_cls.return_value
        history = "Previous conversation"
        mock_session.get_conversation_history.return_value = history

        mock_ai = mock_ai_generator_cls.return_value
        mock_ai.generate_response.return_value = "Final answer"

        rag.tool_manager.get_last_sources = Mock(return_value=sample_sources)
        rag.tool_manager.reset_sources = Mock()

        # Execute full flow
        response, sources = rag.query(
            query="Complex question", session_id="session_999"
        )

        # Verify orchestration steps in order:

        # 1. History retrieved
        mock_session.get_conversation_history.assert_called_with("session_999")

        # 2. AI called with all context
        mock_ai.generate_response.assert_called_once()
        ai_kwargs = mock_ai.generate_response.call_args.kwargs
        assert ai_kwargs["conversation_history"] == history
        assert ai_kwargs["tools"] is not None
        assert ai_kwargs["tool_manager"] is not None

        # 3. Sources retrieved and reset
        rag.tool_manager.get_last_sources.assert_called_once()
        rag.tool_manager.reset_sources.assert_called_once()

        # 4. History updated
        mock_session.add_exchange.assert_called_with(
            "session_999", "Complex question", "Final answer"
        )

        # 5. Response and sources returned
        assert response == "Final answer"
        assert sources == sample_sources

    @patch("rag_system.DocumentProcessor")
    @patch("rag_system.VectorStore")
    @patch("rag_system.AIGenerator")
    @patch("rag_system.SessionManager")
    def test_tool_manager_registration(
        self,
        mock_session_manager_cls,
        mock_ai_generator_cls,
        mock_vector_store_cls,
        mock_doc_processor_cls,
        test_config,
    ):
        """Test all tools are properly registered"""
        rag = RAGSystem(test_config)

        # Verify CourseSearchTool registered
        assert "search_course_content" in rag.tool_manager.tools

        # Verify CourseOutlineTool registered
        assert "get_course_outline" in rag.tool_manager.tools

        # Verify get_tool_definitions returns both tools
        definitions = rag.tool_manager.get_tool_definitions()
        assert len(definitions) == 2

        tool_names = [d["name"] for d in definitions]
        assert "search_course_content" in tool_names
        assert "get_course_outline" in tool_names
