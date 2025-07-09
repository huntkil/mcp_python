"""
MCP types for the Markdown manager server.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class TextContent:
    """Text content for MCP responses."""

    type: str = "text"
    text: str = ""


@dataclass
class Tool:
    """Tool definition for MCP server."""

    name: str
    description: str
    inputSchema: Dict[str, Any]  # noqa: N815


class types:  # noqa: N801
    """MCP types namespace."""

    TextContent = TextContent
    Tool = Tool
