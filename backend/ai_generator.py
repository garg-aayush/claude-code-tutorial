import anthropic
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Anthropic's Claude API for generating responses"""
    
    # Static system prompt to avoid rebuilding on each call
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to tools for searching course content and retrieving course outlines.

Tool Usage:
- You can make multiple tool calls across up to 2 rounds to gather information
- After seeing tool results, you may make additional tool calls if needed to answer the question completely
- Use the search tool for questions about specific course content or detailed educational materials
- Use the outline tool for questions about course structure, lesson lists, or course overviews
- Synthesize all tool results into accurate, fact-based responses
- If tools yield no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without tools
- **Course-specific content questions**: Use the search tool, then answer
- **Course structure/outline questions**: Use the outline tool to get lessons and course information
- **Complex queries**: May require multiple searches across different courses or lessons
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, explanations, or question-type analysis
 - Do not mention "based on the search results" or "according to the tool"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        # Pre-build base API parameters
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None,
                         max_rounds: int = 2) -> str:
        """
        Generate AI response with iterative tool usage support (up to max_rounds).

        Args:
            query: The user's question or request
            conversation_history: Previous messages for context
            tools: Available tools the AI can use
            tool_manager: Manager to execute tools
            max_rounds: Maximum number of tool execution rounds (default: 2)

        Returns:
            Generated response as string
        """

        # Build system content efficiently
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        # Initialize messages array with user's query
        messages = [{"role": "user", "content": query}]

        # Iterative tool execution loop
        rounds_completed = 0

        while rounds_completed < max_rounds:
            # Prepare API call parameters (copy messages to preserve call history)
            api_params = {
                **self.base_params,
                "messages": messages.copy(),
                "system": system_content
            }

            # Add tools if available (KEEP tools available in all rounds)
            if tools:
                api_params["tools"] = tools
                api_params["tool_choice"] = {"type": "auto"}

            # Make API call to Claude
            response = self.client.messages.create(**api_params)

            # Check stop reason
            if response.stop_reason != "tool_use":
                # Claude is done - no more tool calls needed
                return self._extract_text_response(response)

            # Tool use requested - execute tools and continue loop
            if not tool_manager:
                # No tool manager available - cannot execute tools
                return self._extract_text_response(response)

            # Execute tools and update messages
            success = self._execute_tools_and_update_messages(
                response,
                messages,
                tool_manager
            )

            if not success:
                # Tool execution failed - return error message
                return "Error executing tools. Please try again."

            # Increment round counter
            rounds_completed += 1

        # Max rounds reached - make final API call to get synthesis
        # This ensures we always get a text response even if Claude wants more rounds
        final_params = {
            **self.base_params,
            "messages": messages.copy(),
            "system": system_content
            # No tools in final call to force synthesis
        }

        final_response = self.client.messages.create(**final_params)
        return self._extract_text_response(final_response)
    
    def _execute_tools_and_update_messages(self,
                                           response,
                                           messages: List,
                                           tool_manager) -> bool:
        """
        Execute tools from response and update messages array.

        Args:
            response: Claude's response containing tool_use blocks
            messages: Messages array to update (modified in place)
            tool_manager: Manager to execute tools

        Returns:
            True if successful, False if error occurred
        """
        try:
            # Add assistant's tool use response to messages
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tool calls and collect results
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_result = tool_manager.execute_tool(
                        content_block.name,
                        **content_block.input
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": tool_result
                    })

            # Add tool results as user message
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
                return True

            # No tool results collected (shouldn't happen if stop_reason was tool_use)
            return False

        except Exception as e:
            # Log error and return failure
            print(f"Error executing tools: {e}")
            return False

    def _extract_text_response(self, response) -> str:
        """
        Extract text content from Claude's response.

        Args:
            response: Claude's API response

        Returns:
            Text content or empty string if no text found
        """
        for content_block in response.content:
            if hasattr(content_block, 'text'):
                return content_block.text

        # No text block found (edge case)
        return ""

    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager):
        """
        DEPRECATED: Legacy single-round tool execution.

        This method is maintained for backward compatibility but is not used by the new
        iterative loop in generate_response(). It may be removed in a future version.

        Handle execution of tool calls and get follow-up response.

        Args:
            initial_response: The response containing tool use requests
            base_params: Base API parameters
            tool_manager: Manager to execute tools

        Returns:
            Final response text after tool execution
        """
        # Start with existing messages
        messages = base_params["messages"].copy()
        
        # Add AI's tool use response
        messages.append({"role": "assistant", "content": initial_response.content})
        
        # Execute all tool calls and collect results
        tool_results = []
        for content_block in initial_response.content:
            if content_block.type == "tool_use":
                tool_result = tool_manager.execute_tool(
                    content_block.name, 
                    **content_block.input
                )
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": tool_result
                })
        
        # Add tool results as single message
        if tool_results:
            messages.append({"role": "user", "content": tool_results})
        
        # Prepare final API call without tools
        final_params = {
            **self.base_params,
            "messages": messages,
            "system": base_params["system"]
        }
        
        # Get final response
        final_response = self.client.messages.create(**final_params)
        return final_response.content[0].text