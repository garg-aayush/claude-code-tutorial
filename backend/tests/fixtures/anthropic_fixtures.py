"""Fixtures for Anthropic API mocking"""

from unittest.mock import MagicMock, Mock

import pytest
from anthropic.types import ContentBlock, Message, TextBlock, ToolUseBlock


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client"""
    client = Mock()
    client.messages = Mock()
    client.messages.create = Mock()
    return client


@pytest.fixture
def anthropic_text_response():
    """Create a direct text response from Claude (no tool use)"""
    mock_response = Mock(spec=Message)
    mock_response.stop_reason = "end_turn"

    text_block = Mock(spec=TextBlock)
    text_block.type = "text"
    text_block.text = "This is a direct answer without using any tools."

    mock_response.content = [text_block]
    return mock_response


@pytest.fixture
def anthropic_tool_use_response():
    """Create a response requesting tool use"""
    mock_response = Mock(spec=Message)
    mock_response.stop_reason = "tool_use"

    tool_use_block = Mock(spec=ToolUseBlock)
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool_use_123"
    tool_use_block.name = "search_course_content"
    tool_use_block.input = {
        "query": "unit testing",
        "course_name": "Python Testing Course",
    }

    mock_response.content = [tool_use_block]
    return mock_response


@pytest.fixture
def anthropic_final_response_after_tool():
    """Create final synthesis response after tool execution"""
    mock_response = Mock(spec=Message)
    mock_response.stop_reason = "end_turn"

    text_block = Mock(spec=TextBlock)
    text_block.type = "text"
    text_block.text = "Based on the course materials, unit testing focuses on testing individual components in isolation."

    mock_response.content = [text_block]
    return mock_response


@pytest.fixture
def anthropic_tool_use_response_round2():
    """Create a second round tool use response (different query)"""
    mock_response = Mock(spec=Message)
    mock_response.stop_reason = "tool_use"

    tool_use_block = Mock(spec=ToolUseBlock)
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool_use_456"
    tool_use_block.name = "search_course_content"
    tool_use_block.input = {
        "query": "Python testing frameworks",
        "course_name": "Advanced Python Course",
    }

    mock_response.content = [tool_use_block]
    return mock_response


@pytest.fixture
def mock_ai_generator_with_responses(
    mock_anthropic_client,
    anthropic_tool_use_response,
    anthropic_final_response_after_tool,
):
    """Create a mock AIGenerator simulating full tool use flow"""
    from ai_generator import AIGenerator

    generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
    generator.client = mock_anthropic_client

    # Simulate two-step flow: tool request, then final response
    mock_anthropic_client.messages.create.side_effect = [
        anthropic_tool_use_response,
        anthropic_final_response_after_tool,
    ]

    return generator


@pytest.fixture
def mock_ai_generator_no_tools(mock_anthropic_client, anthropic_text_response):
    """Create a mock AIGenerator for direct responses (no tools)"""
    from ai_generator import AIGenerator

    generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
    generator.client = mock_anthropic_client

    # Direct response without tools
    mock_anthropic_client.messages.create.return_value = anthropic_text_response

    return generator
