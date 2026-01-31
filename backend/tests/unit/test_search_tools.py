"""Unit tests for CourseSearchTool"""

from unittest.mock import Mock

import pytest
from models import Source
from search_tools import CourseSearchTool, ToolManager
from vector_store import SearchResults


class TestCourseSearchTool:
    """Test CourseSearchTool functionality"""

    def test_get_tool_definition(self, mock_vector_store):
        """Verify tool schema is correct"""
        tool = CourseSearchTool(mock_vector_store)
        definition = tool.get_tool_definition()

        assert definition["name"] == "search_course_content"
        assert "query" in definition["input_schema"]["properties"]
        assert "course_name" in definition["input_schema"]["properties"]
        assert "lesson_number" in definition["input_schema"]["properties"]
        assert definition["input_schema"]["required"] == ["query"]

    def test_execute_successful_search_no_filters(
        self, mock_vector_store, sample_search_results
    ):
        """Test basic search without filters"""
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test query")

        # Verify search was called correctly
        mock_vector_store.search.assert_called_once_with(
            query="test query", course_name=None, lesson_number=None
        )

        # Verify formatted results contain course titles
        assert "Python Testing Course" in result
        assert "MCP Introduction" in result

        # Verify sources populated
        assert len(tool.last_sources) == 3
        assert isinstance(tool.last_sources[0], Source)

    def test_execute_with_course_name_filter(
        self, mock_vector_store, sample_search_results
    ):
        """Test search with course name filter"""
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test query", course_name="MCP")

        # Verify filter applied to search
        mock_vector_store.search.assert_called_once_with(
            query="test query", course_name="MCP", lesson_number=None
        )

        assert result is not None

    def test_execute_with_lesson_number_filter(
        self, mock_vector_store, sample_search_results
    ):
        """Test search with lesson number filter"""
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test query", lesson_number=2)

        # Verify filter applied
        mock_vector_store.search.assert_called_once_with(
            query="test query", course_name=None, lesson_number=2
        )

        # Verify lesson number appears in source text
        assert "Lesson 2" in result

    def test_execute_with_combined_filters(
        self, mock_vector_store, sample_search_results
    ):
        """Test search with both course name and lesson number filters"""
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(
            query="test query", course_name="Python Testing Course", lesson_number=1
        )

        # Verify both filters passed to search
        mock_vector_store.search.assert_called_once_with(
            query="test query", course_name="Python Testing Course", lesson_number=1
        )

        assert result is not None

    def test_execute_empty_results_no_filters(
        self, mock_vector_store, empty_search_results
    ):
        """Test handling of empty results without filters"""
        mock_vector_store.search.return_value = empty_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="nonexistent content")

        assert result == "No relevant content found."

    def test_execute_empty_results_with_filters(
        self, mock_vector_store, empty_search_results
    ):
        """Test handling of empty results with filters"""
        mock_vector_store.search.return_value = empty_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(
            query="test query", course_name="Nonexistent Course", lesson_number=5
        )

        assert "No relevant content found" in result
        assert "Nonexistent Course" in result
        assert "lesson 5" in result

    def test_execute_search_error(self, mock_vector_store, error_search_results):
        """Test error handling from search"""
        mock_vector_store.search.return_value = error_search_results
        tool = CourseSearchTool(mock_vector_store)

        result = tool.execute(query="test query")

        assert result == "Database connection failed"

    def test_format_results_creates_sources(
        self, mock_vector_store, sample_search_results
    ):
        """Test that _format_results creates proper Source objects"""
        tool = CourseSearchTool(mock_vector_store)

        _formatted = tool._format_results(sample_search_results)

        # Check sources were created
        assert len(tool.last_sources) == 3

        # Check first source
        assert tool.last_sources[0].text == "Python Testing Course - Lesson 1"
        assert tool.last_sources[0].url is not None

        # Check source without lesson number (should still work)
        assert isinstance(tool.last_sources[2], Source)

    def test_last_sources_tracking(self, mock_vector_store, sample_search_results):
        """Test source tracking across multiple searches"""
        mock_vector_store.search.return_value = sample_search_results
        tool = CourseSearchTool(mock_vector_store)

        # First search
        tool.execute(query="first query")
        first_sources = tool.last_sources.copy()
        assert len(first_sources) == 3

        # Second search should replace sources
        tool.execute(query="second query")
        assert len(tool.last_sources) == 3

        # Verify Source.text format is correct
        for source in tool.last_sources:
            assert " - Lesson " in source.text or "Lesson" not in source.text


class TestToolManager:
    """Test ToolManager functionality"""

    def test_register_tool(self, mock_vector_store):
        """Test tool registration"""
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)

        manager.register_tool(tool)

        assert "search_course_content" in manager.tools
        assert manager.tools["search_course_content"] == tool

    def test_get_tool_definitions(self, mock_vector_store):
        """Test retrieving tool definitions"""
        manager = ToolManager()
        search_tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(search_tool)

        definitions = manager.get_tool_definitions()

        assert len(definitions) == 1
        assert definitions[0]["name"] == "search_course_content"

    def test_execute_tool(self, mock_vector_store, sample_search_results):
        """Test tool execution via manager"""
        mock_vector_store.search.return_value = sample_search_results
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        result = manager.execute_tool("search_course_content", query="test")

        assert result is not None
        assert "Python Testing Course" in result

    def test_execute_nonexistent_tool(self, mock_vector_store):
        """Test executing a tool that doesn't exist"""
        manager = ToolManager()

        result = manager.execute_tool("nonexistent_tool", query="test")

        assert "not found" in result

    def test_get_last_sources(self, mock_vector_store, sample_search_results):
        """Test retrieving sources from last search"""
        mock_vector_store.search.return_value = sample_search_results
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        # Execute search
        manager.execute_tool("search_course_content", query="test")

        # Get sources
        sources = manager.get_last_sources()

        assert len(sources) == 3
        assert all(isinstance(s, Source) for s in sources)

    def test_reset_sources(self, mock_vector_store, sample_search_results):
        """Test resetting sources across all tools"""
        mock_vector_store.search.return_value = sample_search_results
        manager = ToolManager()
        tool = CourseSearchTool(mock_vector_store)
        manager.register_tool(tool)

        # Execute search
        manager.execute_tool("search_course_content", query="test")
        assert len(manager.get_last_sources()) == 3

        # Reset sources
        manager.reset_sources()
        assert len(manager.get_last_sources()) == 0
