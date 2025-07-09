"""
MCP server for Markdown document management.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import os
import sys

from mcp.server import Server
from mcp import types
from mcp.server.stdio import stdio_server
from .markdown_manager import MarkdownManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarkdownMCPServer:
    """
    MCP server for managing Markdown documents.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the MCP server.
        
        Args:
            base_path: Base directory for file operations
        """
        self.server = Server("markdown-manager")
        self.markdown_manager = MarkdownManager(base_path)
        self.setup_tools()
        logger.info("Markdown MCP Server initialized")
    
    def setup_tools(self):
        """Register all tools with the MCP server."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools."""
            return [
                types.Tool(
                    name="read_markdown",
                    description="Read a Markdown file and return its content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Markdown file to read"
                            },
                            "encoding": {
                                "type": "string",
                                "description": "File encoding (default: utf-8)",
                                "default": "utf-8"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="create_markdown",
                    description="Create a new Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to create"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "description": "Whether to overwrite existing file",
                                "default": False
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                types.Tool(
                    name="update_markdown",
                    description="Update an existing Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to update"
                            },
                            "content": {
                                "type": "string",
                                "description": "New content"
                            },
                            "append": {
                                "type": "boolean",
                                "description": "Whether to append content instead of replacing",
                                "default": False
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                types.Tool(
                    name="delete_markdown",
                    description="Delete a Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to delete"
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Whether to confirm deletion",
                                "default": False
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="list_markdown_files",
                    description="List Markdown files in a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in",
                                "default": "."
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search recursively",
                                "default": False
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern to match",
                                "default": "*.md"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="search_markdown",
                    description="Search for content in Markdown files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in"
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Whether search should be case sensitive",
                                "default": False
                            }
                        },
                        "required": ["directory", "query"]
                    }
                ),
                types.Tool(
                    name="manage_frontmatter",
                    description="Manage YAML frontmatter in Markdown files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file"
                            },
                            "action": {
                                "type": "string",
                                "description": "Action to perform: get, set, update, remove",
                                "enum": ["get", "set", "update", "remove"]
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Metadata for set/update actions"
                            }
                        },
                        "required": ["file_path", "action"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                logger.info(f"Tool call: {name} with arguments: {arguments}")
                
                if name == "read_markdown":
                    result = self.markdown_manager.read_file(
                        file_path=arguments["file_path"],
                        encoding=arguments.get("encoding", "utf-8")
                    )
                
                elif name == "create_markdown":
                    result = self.markdown_manager.create_file(
                        file_path=arguments["file_path"],
                        content=arguments["content"],
                        overwrite=arguments.get("overwrite", False)
                    )
                
                elif name == "update_markdown":
                    result = self.markdown_manager.update_file(
                        file_path=arguments["file_path"],
                        content=arguments["content"],
                        append=arguments.get("append", False)
                    )
                
                elif name == "delete_markdown":
                    result = self.markdown_manager.delete_file(
                        file_path=arguments["file_path"],
                        confirm=arguments.get("confirm", False)
                    )
                
                elif name == "list_markdown_files":
                    result = self.markdown_manager.list_files(
                        directory=arguments.get("directory", "."),
                        recursive=arguments.get("recursive", False),
                        pattern=arguments.get("pattern", "*.md")
                    )
                
                elif name == "search_markdown":
                    result = self.markdown_manager.search_content(
                        directory=arguments["directory"],
                        query=arguments["query"],
                        case_sensitive=arguments.get("case_sensitive", False)
                    )
                
                elif name == "manage_frontmatter":
                    result = self.markdown_manager.manage_frontmatter(
                        file_path=arguments["file_path"],
                        action=arguments["action"],
                        metadata=arguments.get("metadata")
                    )
                
                else:
                    result = {"error": f"Unknown tool: {name}"}
                
                # Convert result to JSON string
                result_text = json.dumps(result, indent=2, ensure_ascii=False)
                
                logger.info(f"Tool {name} completed successfully")
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                error_result = {"error": f"Tool execution failed: {str(e)}"}
                return [types.TextContent(type="text", text=json.dumps(error_result, indent=2))]


def main():
    """Main entry point."""
    # Get base path from environment or use current directory
    base_path = os.getenv("MARKDOWN_MCP_BASE_PATH", ".")
    
    server = MarkdownMCPServer(base_path)
    logger.info("Starting Markdown MCP Server...")
    stdio_server(server.server)


if __name__ == "__main__":
    main() 