"""Gemini AI Agent with function calling for tool execution."""

import json
import logging

from google import genai
from google.genai import types

from controller.agent.prompts import SYSTEM_PROMPT
from controller.security.permissions import PermissionManager
from controller.tools.base import ToolRegistry

logger = logging.getLogger(__name__)


class Agent:
    """AI Agent that uses Gemini for reasoning and local tools for execution.

    Maintains per-channel conversation history and handles the function-calling
    loop: user message -> Gemini -> tool calls -> Gemini -> response.
    """

    MAX_TOOL_ROUNDS = 10  # Prevent infinite tool-calling loops

    def __init__(
        self,
        config,
        tool_registry: ToolRegistry,
        permission_manager: PermissionManager,
    ):
        self.client = genai.Client(api_key=config.gemini_api_key)
        self.model = config.gemini_model
        self.tool_registry = tool_registry
        self.permissions = permission_manager
        self._conversations: dict[str, list[types.Content]] = {}

    def _get_tools_config(self) -> list[types.Tool]:
        """Build Gemini tools configuration from registered tools."""
        declarations = []
        for tool in self.tool_registry.get_all():
            declarations.append(types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
            ))
        return [types.Tool(function_declarations=declarations)]

    def _get_history(self, channel_id: str) -> list[types.Content]:
        """Get or create conversation history for a channel."""
        if channel_id not in self._conversations:
            self._conversations[channel_id] = []
        return self._conversations[channel_id]

    def clear_history(self, channel_id: str) -> None:
        """Clear conversation history for a channel."""
        self._conversations.pop(channel_id, None)

    async def process_message(
        self,
        channel_id: str,
        user_message: str,
        confirmation_callback=None,
    ) -> str:
        """Process a user message through the AI agent.

        Args:
            channel_id: Discord channel ID for conversation context.
            user_message: The user's message text.
            confirmation_callback: Async callback for dangerous operations.
                Signature: async (tool_name, description) -> bool

        Returns:
            The agent's text response.
        """
        history = self._get_history(channel_id)

        # Add user message to history
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
        history.append(user_content)

        # Keep history manageable (last 20 turns)
        if len(history) > 40:
            history[:] = history[-40:]

        try:
            return await self._run_agent_loop(channel_id, history, confirmation_callback)
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return f"An error occurred while processing your request: {e}"

    async def _run_agent_loop(
        self,
        channel_id: str,
        history: list[types.Content],
        confirmation_callback,
    ) -> str:
        """Run the agent loop: send to Gemini, execute tools, repeat."""
        for round_num in range(self.MAX_TOOL_ROUNDS):
            response = self.client.models.generate_content(
                model=self.model,
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=self._get_tools_config(),
                    temperature=0.3,
                ),
            )

            candidate = response.candidates[0]
            content = candidate.content

            # Add model response to history
            history.append(content)

            # Check if model wants to call functions
            function_calls = [
                part for part in content.parts
                if part.function_call is not None
            ]

            if not function_calls:
                # Model returned text, we're done
                text_parts = [
                    part.text for part in content.parts
                    if part.text is not None
                ]
                return "\n".join(text_parts) if text_parts else "Done."

            # Execute function calls
            function_responses = []
            for part in function_calls:
                fc = part.function_call
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}

                result = await self._execute_tool(
                    tool_name, tool_args, confirmation_callback
                )

                function_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": result},
                    )
                )

            # Add function responses to history
            response_content = types.Content(
                role="user",
                parts=function_responses,
            )
            history.append(response_content)

        return "Reached maximum number of tool calls. Please try a simpler request."

    async def _execute_tool(
        self,
        tool_name: str,
        kwargs: dict,
        confirmation_callback,
    ) -> str:
        """Execute a single tool with permission checks."""
        tool = self.tool_registry.get(tool_name)
        if not tool:
            return f"Error: Unknown tool '{tool_name}'"

        # Check path permissions
        path_error = self.permissions.check_tool_paths(tool_name, kwargs)
        if path_error:
            return path_error

        # Check if confirmation is needed
        if self.permissions.needs_confirmation(tool_name) and confirmation_callback:
            args_summary = json.dumps(kwargs, indent=2, ensure_ascii=False)
            description = f"**{tool_name}**\n```json\n{args_summary}\n```"
            confirmed = await confirmation_callback(tool_name, description)
            if not confirmed:
                return f"Operation '{tool_name}' was denied by user."

        # Execute the tool
        logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
        try:
            result = await tool.execute(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            return f"Error executing {tool_name}: {e}"
