"""
MCP Server implementation for Markdown management.
"""

import logging
from typing import Any, Callable, Dict, List

from .. import types


class Server:
    """
    MCP Server implementation.
    """

    def __init__(self, name: str):
        """
        Initialize the MCP server.

        Args:
            name: Server name
        """
        self.name = name
        self.tools: Dict[str, Callable] = {}
        self.logger = logging.getLogger(f"mcp.server.{name}")

    def list_tools(self):
        """Decorator to register a list_tools handler."""

        def decorator(func: Callable):
            self._list_tools_handler = func
            return func

        return decorator

    def call_tool(self):
        """Decorator to register a call_tool handler."""

        def decorator(func: Callable):
            self._call_tool_handler = func
            return func

        return decorator

    async def handle_list_tools(self) -> List[types.Tool]:
        """Handle list_tools request."""
        if hasattr(self, "_list_tools_handler"):
            return await self._list_tools_handler()
        return []

    async def handle_call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle call_tool request."""
        if hasattr(self, "_call_tool_handler"):
            return await self._call_tool_handler(name, arguments)
        return [types.TextContent(text=f"Tool {name} not implemented")]
