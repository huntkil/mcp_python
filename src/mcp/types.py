"""
MCP types for the Markdown manager server.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


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
    inputSchema: Dict[str, Any]


class types:
    """MCP types namespace."""
    
    TextContent = TextContent
    Tool = Tool 