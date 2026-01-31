"""Unit tests for AIGenerator"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from ai_generator import AIGenerator
from anthropic.types import Message, TextBlock, ToolUseBlock


class TestAIGenerator:
    """Test AIGenerator functionality"""

    def test_initialization(self):
        """Verify AIGenerator setup"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")

        assert generator.model == "claude-haiku-4-5"
        assert generator.base_params["model"] == "claude-haiku-4-5"
        assert generator.base_params["temperature"] == 0
        assert generator.base_params["max_tokens"] == 800

    def test_generate_response_without_tools(self, mock_anthropic_client, anthropic_text_response):
        """Test direct response without tools"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client
        mock_anthropic_client.messages.create.return_value = anthropic_text_response

        response = generator.generate_response(query="What is testing?", tools=None)

        # Verify response
        assert response == "This is a direct answer without using any tools."

        # Verify API call parameters
        call_args = mock_anthropic_client.messages.create.call_args
        assert call_args.kwargs["messages"][0]["content"] == "What is testing?"
        assert "tools" not in call_args.kwargs

    def test_generate_response_no_tool_use_needed(self, mock_anthropic_client, anthropic_text_response):
        """Test when tools are available but not used"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client
        mock_anthropic_client.messages.create.return_value = anthropic_text_response

        tools = [{"name": "search_course_content", "description": "Search tool"}]
        response = generator.generate_response(query="What is 2+2?", tools=tools)

        # Should return direct text since stop_reason is "end_turn"
        assert response == "This is a direct answer without using any tools."

        # Verify tools were provided to API
        call_args = mock_anthropic_client.messages.create.call_args
        assert "tools" in call_args.kwargs

    def test_generate_response_triggers_tool_use(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_final_response_after_tool):
        """Test tool execution flow"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        # Mock two API calls: initial with tool_use, then final response
        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_final_response_after_tool
        ]

        # Create mock tool manager
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Search results about unit testing"

        tools = [{"name": "search_course_content", "description": "Search tool"}]
        response = generator.generate_response(
            query="Tell me about unit testing",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify two API calls were made
        assert mock_anthropic_client.messages.create.call_count == 2

        # Verify tool was executed
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="unit testing",
            course_name="Python Testing Course"
        )

        # Verify final response
        assert "unit testing focuses on testing individual components" in response

    def test_handle_tool_execution_message_sequence(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_final_response_after_tool):
        """Verify message structure in tool execution"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_final_response_after_tool
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Tool results"

        tools = [{"name": "search_course_content", "description": "Search"}]
        generator.generate_response(
            query="Test query",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Check second API call's messages
        second_call_kwargs = mock_anthropic_client.messages.create.call_args_list[1].kwargs
        messages = second_call_kwargs["messages"]

        # Should have: user message, assistant message with tool_use, user message with tool_result
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"

        # Verify tool_result structure
        tool_results = messages[2]["content"]
        assert isinstance(tool_results, list)
        assert tool_results[0]["type"] == "tool_result"
        assert tool_results[0]["content"] == "Tool results"

    def test_handle_tool_execution_tool_parameters(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_final_response_after_tool):
        """Test that tool parameters are passed correctly"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        # Set specific parameters in tool_use response
        anthropic_tool_use_response.content[0].input = {
            "query": "integration testing",
            "course_name": "Advanced Course",
            "lesson_number": 3
        }

        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_final_response_after_tool
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Results"

        tools = [{"name": "search_course_content"}]
        generator.generate_response(
            query="Test",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify all parameters passed to tool
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="integration testing",
            course_name="Advanced Course",
            lesson_number=3
        )

    def test_generate_response_with_conversation_history(self, mock_anthropic_client, anthropic_text_response):
        """Test that conversation history is included in system prompt"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client
        mock_anthropic_client.messages.create.return_value = anthropic_text_response

        history = "User: What is testing?\nAssistant: Testing verifies code quality."
        response = generator.generate_response(
            query="Tell me more",
            conversation_history=history
        )

        # Verify system prompt includes history
        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert "Previous conversation:" in call_kwargs["system"]
        assert history in call_kwargs["system"]

    def test_tool_execution_error_handling(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_final_response_after_tool):
        """Test error propagation from tool execution"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_final_response_after_tool
        ]

        # Tool returns error
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Error: Database not found"

        tools = [{"name": "search_course_content"}]
        response = generator.generate_response(
            query="Test",
            tools=tools,
            tool_manager=mock_tool_manager
        )

        # Verify error was passed to Claude in tool_result
        second_call_kwargs = mock_anthropic_client.messages.create.call_args_list[1].kwargs
        tool_result_content = second_call_kwargs["messages"][2]["content"][0]["content"]
        assert tool_result_content == "Error: Database not found"

    def test_api_parameters_correct(self, mock_anthropic_client, anthropic_text_response):
        """Verify API call parameters are correct"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client
        mock_anthropic_client.messages.create.return_value = anthropic_text_response

        tools = [{"name": "test_tool"}]
        generator.generate_response(
            query="Test query",
            tools=tools
        )

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs

        # Verify parameters
        assert call_kwargs["model"] == "claude-haiku-4-5"
        assert call_kwargs["temperature"] == 0
        assert call_kwargs["max_tokens"] == 800
        assert call_kwargs["tools"] == tools
        assert call_kwargs["tool_choice"] == {"type": "auto"}

    def test_system_prompt_construction(self, mock_anthropic_client, anthropic_text_response):
        """Test system prompt construction with and without history"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client
        mock_anthropic_client.messages.create.return_value = anthropic_text_response

        # Without history
        generator.generate_response(query="Test")
        call1_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert "Previous conversation:" not in call1_kwargs["system"]
        assert "AI assistant specialized in course materials" in call1_kwargs["system"]

        # With history
        generator.generate_response(query="Test", conversation_history="Previous chat")
        call2_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert "Previous conversation:" in call2_kwargs["system"]
        assert "Previous chat" in call2_kwargs["system"]

    def test_generate_response_two_tool_rounds(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_tool_use_response_round2, anthropic_final_response_after_tool):
        """Test two rounds of tool execution"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        # Mock three API calls: tool round 1, tool round 2, final text
        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,        # Round 1: search "unit testing"
            anthropic_tool_use_response_round2, # Round 2: search "Python testing frameworks"
            anthropic_final_response_after_tool # Final: text response
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = [
            "Results for unit testing",
            "Results for Python testing frameworks"
        ]

        tools = [{"name": "search_course_content"}]
        response = generator.generate_response(
            query="Tell me about Python testing",
            tools=tools,
            tool_manager=mock_tool_manager,
            max_rounds=2
        )

        # Verify three API calls
        assert mock_anthropic_client.messages.create.call_count == 3

        # Verify two tool executions
        assert mock_tool_manager.execute_tool.call_count == 2

        # Verify final response
        assert "unit testing focuses on testing individual components" in response

    def test_max_rounds_limit_enforced(self, mock_anthropic_client, anthropic_tool_use_response):
        """Test that max_rounds limit is enforced"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        # Create a final text response for the synthesis call
        final_response = Mock(spec=Message)
        final_response.stop_reason = "end_turn"
        text_block = Mock(spec=TextBlock)
        text_block.type = "text"
        text_block.text = "Final synthesis after max rounds"
        final_response.content = [text_block]

        # Mock responses that always request tools (would loop forever without limit)
        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_tool_use_response,
            final_response  # Final synthesis call
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Results"

        tools = [{"name": "search_course_content"}]
        response = generator.generate_response(
            query="Test",
            tools=tools,
            tool_manager=mock_tool_manager,
            max_rounds=2
        )

        # Should make: 2 tool rounds + 1 final synthesis call = 3 total
        assert mock_anthropic_client.messages.create.call_count == 3

        # Should execute tools twice
        assert mock_tool_manager.execute_tool.call_count == 2

        # Verify final response
        assert response == "Final synthesis after max rounds"

    def test_early_termination_on_text_response(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_final_response_after_tool):
        """Test that loop terminates early when Claude returns text"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        # Mock: tool round 1, then text (natural termination)
        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_final_response_after_tool
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.return_value = "Results"

        tools = [{"name": "search_course_content"}]
        response = generator.generate_response(
            query="Test",
            tools=tools,
            tool_manager=mock_tool_manager,
            max_rounds=2
        )

        # Should only make 2 API calls (not 3) since Claude terminated early
        assert mock_anthropic_client.messages.create.call_count == 2

        # Should only execute tools once
        assert mock_tool_manager.execute_tool.call_count == 1

        # Verify response
        assert "unit testing focuses on testing individual components" in response

    def test_message_accumulation_across_rounds(self, mock_anthropic_client, anthropic_tool_use_response, anthropic_tool_use_response_round2, anthropic_final_response_after_tool):
        """Test that messages accumulate correctly across rounds"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        mock_anthropic_client.messages.create.side_effect = [
            anthropic_tool_use_response,
            anthropic_tool_use_response_round2,
            anthropic_final_response_after_tool
        ]

        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = ["Result 1", "Result 2"]

        tools = [{"name": "search_course_content"}]
        generator.generate_response(
            query="Test query",
            tools=tools,
            tool_manager=mock_tool_manager,
            max_rounds=2
        )

        # Check second API call's messages
        call2_messages = mock_anthropic_client.messages.create.call_args_list[1].kwargs["messages"]

        # Should have: user query, assistant tool_use, user tool_result
        assert len(call2_messages) == 3
        assert call2_messages[0]["role"] == "user"
        assert call2_messages[1]["role"] == "assistant"
        assert call2_messages[2]["role"] == "user"

        # Check third API call's messages
        call3_messages = mock_anthropic_client.messages.create.call_args_list[2].kwargs["messages"]

        # Should have: user query, asst tool_use, user tool_result, asst tool_use, user tool_result
        assert len(call3_messages) == 5

    def test_tool_execution_error_handling_in_loop(self, mock_anthropic_client, anthropic_tool_use_response):
        """Test error handling when tool execution fails"""
        generator = AIGenerator(api_key="test-key", model="claude-haiku-4-5")
        generator.client = mock_anthropic_client

        mock_anthropic_client.messages.create.return_value = anthropic_tool_use_response

        # Tool execution raises exception
        mock_tool_manager = Mock()
        mock_tool_manager.execute_tool.side_effect = Exception("Database error")

        tools = [{"name": "search_course_content"}]
        response = generator.generate_response(
            query="Test",
            tools=tools,
            tool_manager=mock_tool_manager,
            max_rounds=2
        )

        # Should return error message
        assert "Error executing tools" in response

        # Should only make one API call (error stops loop)
        assert mock_anthropic_client.messages.create.call_count == 1
