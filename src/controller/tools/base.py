"""Base tool class and registry for Gemini function calling."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Base class for all tools that can be called by the AI agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calling."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this tool does."""

    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON Schema for tool parameters."""

    @property
    def dangerous(self) -> bool:
        """Whether this tool requires user confirmation before execution."""
        return False

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters. Returns result string."""


class ToolRegistry:
    """Registry for managing available tools and converting to Gemini format."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_function_declarations(self) -> list[dict[str, Any]]:
        """Convert all tools to Gemini function declaration format."""
        declarations = []
        for tool in self._tools.values():
            declarations.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            })
        return declarations

    def is_dangerous(self, tool_name: str) -> bool:
        """Check if a tool requires confirmation."""
        tool = self._tools.get(tool_name)
        return tool.dangerous if tool else False
