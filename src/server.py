"""
MCP server for Markdown document management with Obsidian integration.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from .markdown_manager import MarkdownManager
from .mcp import types
from .mcp.server import Server
from .mcp.server.stdio import stdio_server
from .obsidian_manager import ObsidianManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarkdownMCPServer:
    """
    MCP server for managing Markdown documents and Obsidian vaults.
    """

    def __init__(self, base_path: str = ".", obsidian_vault_path: Optional[str] = None):
        """
        Initialize the MCP server.

        Args:
            base_path: Base directory for file operations
            obsidian_vault_path: Path to Obsidian vault (optional)
        """
        self.server = Server("markdown-manager")
        self.markdown_manager = MarkdownManager(base_path)

        # Initialize Obsidian manager if vault path is provided
        self.obsidian_manager = None
        if obsidian_vault_path:
            try:
                self.obsidian_manager = ObsidianManager(obsidian_vault_path)
                logger.info(
                    f"Obsidian manager initialized with vault: {obsidian_vault_path}"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Obsidian manager: {e}")

        self.setup_tools()
        logger.info("Markdown MCP Server initialized")

    def setup_tools(self):
        """Register all tools with the MCP server."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools."""
            tools = [
                types.Tool(
                    name="read_markdown",
                    description="Read a Markdown file and return its content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the Markdown file to read",
                            },
                            "encoding": {
                                "type": "string",
                                "description": "File encoding (default: utf-8)",
                                "default": "utf-8",
                            },
                        },
                        "required": ["file_path"],
                    },
                ),
                types.Tool(
                    name="create_markdown",
                    description="Create a new Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to create",
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file",
                            },
                            "overwrite": {
                                "type": "boolean",
                                "description": "Whether to overwrite existing file",
                                "default": False,
                            },
                        },
                        "required": ["file_path", "content"],
                    },
                ),
                types.Tool(
                    name="update_markdown",
                    description="Update an existing Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to update",
                            },
                            "content": {"type": "string", "description": "New content"},
                            "append": {
                                "type": "boolean",
                                "description": "Whether to append content instead of replacing",
                                "default": False,
                            },
                        },
                        "required": ["file_path", "content"],
                    },
                ),
                types.Tool(
                    name="delete_markdown",
                    description="Delete a Markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to delete",
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Whether to confirm deletion",
                                "default": False,
                            },
                        },
                        "required": ["file_path"],
                    },
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
                                "default": ".",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search recursively",
                                "default": False,
                            },
                            "pattern": {
                                "type": "string",
                                "description": "File pattern to match",
                                "default": "*.md",
                            },
                        },
                    },
                ),
                types.Tool(
                    name="search_markdown",
                    description="Search for content in Markdown files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in",
                            },
                            "query": {"type": "string", "description": "Search query"},
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Whether search should be case sensitive",
                                "default": False,
                            },
                        },
                        "required": ["directory", "query"],
                    },
                ),
                types.Tool(
                    name="manage_frontmatter",
                    description="Manage YAML frontmatter in Markdown files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file",
                            },
                            "action": {
                                "type": "string",
                                "description": "Action to perform: get, set, update, remove",
                                "enum": ["get", "set", "update", "remove"],
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Metadata for set/update actions",
                            },
                        },
                        "required": ["file_path", "action"],
                    },
                ),
            ]

            # Add Obsidian tools if Obsidian manager is available
            if self.obsidian_manager:
                obsidian_tools = [
                    types.Tool(
                        name="obsidian_vault_info",
                        description="Get information about the Obsidian vault",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    types.Tool(
                        name="obsidian_list_notes",
                        description="List all notes in the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "folder": {
                                    "type": "string",
                                    "description": "Subfolder path (relative to vault root)",
                                    "default": "",
                                },
                                "recursive": {
                                    "type": "boolean",
                                    "description": "Whether to search recursively",
                                    "default": True,
                                },
                            },
                        },
                    ),
                    types.Tool(
                        name="obsidian_read_note",
                        description="Read a note from the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "note_path": {
                                    "type": "string",
                                    "description": "Path to the note (relative to vault root)",
                                }
                            },
                            "required": ["note_path"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_create_note",
                        description="Create a new note in the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "note_path": {
                                    "type": "string",
                                    "description": "Path for the new note (relative to vault root)",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Note content",
                                    "default": "",
                                },
                                "frontmatter": {
                                    "type": "object",
                                    "description": "Optional frontmatter metadata",
                                },
                            },
                            "required": ["note_path"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_update_note",
                        description="Update an existing note in the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "note_path": {
                                    "type": "string",
                                    "description": "Path to the note",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "New content (if None, keeps existing)",
                                },
                                "frontmatter": {
                                    "type": "object",
                                    "description": "New frontmatter (if None, keeps existing)",
                                },
                                "append": {
                                    "type": "boolean",
                                    "description": "Whether to append content instead of replacing",
                                    "default": False,
                                },
                            },
                            "required": ["note_path"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_delete_note",
                        description="Delete a note from the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "note_path": {
                                    "type": "string",
                                    "description": "Path to the note to delete",
                                }
                            },
                            "required": ["note_path"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_search_notes",
                        description="Search for notes containing the query in the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query",
                                },
                                "folder": {
                                    "type": "string",
                                    "description": "Limit search to specific folder",
                                    "default": "",
                                },
                                "case_sensitive": {
                                    "type": "boolean",
                                    "description": "Whether search is case sensitive",
                                    "default": False,
                                },
                            },
                            "required": ["query"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_get_tags",
                        description="Extract all tags from the Obsidian vault",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    types.Tool(
                        name="obsidian_get_links",
                        description="Extract all internal links from the Obsidian vault",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    types.Tool(
                        name="obsidian_create_template",
                        description="Create a template in the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "template_name": {
                                    "type": "string",
                                    "description": "Name of the template",
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Template content",
                                },
                                "frontmatter": {
                                    "type": "object",
                                    "description": "Optional frontmatter for the template",
                                },
                            },
                            "required": ["template_name", "content"],
                        },
                    ),
                    types.Tool(
                        name="obsidian_list_templates",
                        description="List all available templates in the Obsidian vault",
                        inputSchema={"type": "object", "properties": {}},
                    ),
                    types.Tool(
                        name="obsidian_create_note_from_template",
                        description="Create a new note using a template from the Obsidian vault",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "template_name": {
                                    "type": "string",
                                    "description": "Name of the template to use",
                                },
                                "note_path": {
                                    "type": "string",
                                    "description": "Path for the new note",
                                },
                                "variables": {
                                    "type": "object",
                                    "description": "Variables to substitute in the template",
                                },
                            },
                            "required": ["template_name", "note_path"],
                        },
                    ),
                ]
                tools.extend(obsidian_tools)

            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls."""
            try:
                logger.info(f"Tool call: {name} with arguments: {arguments}")

                if name == "read_markdown":
                    result = self.markdown_manager.read_file(
                        file_path=arguments["file_path"],
                        encoding=arguments.get("encoding", "utf-8"),
                    )

                elif name == "create_markdown":
                    result = self.markdown_manager.create_file(
                        file_path=arguments["file_path"],
                        content=arguments["content"],
                        overwrite=arguments.get("overwrite", False),
                    )

                elif name == "update_markdown":
                    result = self.markdown_manager.update_file(
                        file_path=arguments["file_path"],
                        content=arguments["content"],
                        append=arguments.get("append", False),
                    )

                elif name == "delete_markdown":
                    result = self.markdown_manager.delete_file(
                        file_path=arguments["file_path"],
                        confirm=arguments.get("confirm", False),
                    )

                elif name == "list_markdown_files":
                    result = self.markdown_manager.list_files(
                        directory=arguments.get("directory", "."),
                        recursive=arguments.get("recursive", False),
                        pattern=arguments.get("pattern", "*.md"),
                    )

                elif name == "search_markdown":
                    result = self.markdown_manager.search_content(
                        directory=arguments["directory"],
                        query=arguments["query"],
                        case_sensitive=arguments.get("case_sensitive", False),
                    )

                elif name == "manage_frontmatter":
                    result = self.markdown_manager.manage_frontmatter(
                        file_path=arguments["file_path"],
                        action=arguments["action"],
                        metadata=arguments.get("metadata"),
                    )

                # Obsidian tools
                elif name == "obsidian_vault_info":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.get_vault_info()

                elif name == "obsidian_list_notes":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.list_notes(
                            folder=arguments.get("folder", ""),
                            recursive=arguments.get("recursive", True),
                        )

                elif name == "obsidian_read_note":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.read_note(
                            note_path=arguments["note_path"]
                        )

                elif name == "obsidian_create_note":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.create_note(
                            note_path=arguments["note_path"],
                            content=arguments.get("content", ""),
                            frontmatter=arguments.get("frontmatter"),
                        )

                elif name == "obsidian_update_note":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.update_note(
                            note_path=arguments["note_path"],
                            content=arguments.get("content"),
                            frontmatter=arguments.get("frontmatter"),
                            append=arguments.get("append", False),
                        )

                elif name == "obsidian_delete_note":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.delete_note(
                            note_path=arguments["note_path"]
                        )

                elif name == "obsidian_search_notes":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.search_notes(
                            query=arguments["query"],
                            folder=arguments.get("folder", ""),
                            case_sensitive=arguments.get("case_sensitive", False),
                        )

                elif name == "obsidian_get_tags":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.get_tags()

                elif name == "obsidian_get_links":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.get_links()

                elif name == "obsidian_create_template":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.create_template(
                            template_name=arguments["template_name"],
                            content=arguments["content"],
                            frontmatter=arguments.get("frontmatter"),
                        )

                elif name == "obsidian_list_templates":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.list_templates()

                elif name == "obsidian_create_note_from_template":
                    if not self.obsidian_manager:
                        result = {"error": "Obsidian manager not initialized"}
                    else:
                        result = self.obsidian_manager.create_note_from_template(
                            template_name=arguments["template_name"],
                            note_path=arguments["note_path"],
                            variables=arguments.get("variables"),
                        )

                else:
                    result = {"error": f"Unknown tool: {name}"}

                # Convert result to JSON string
                result_text = json.dumps(result, indent=2, ensure_ascii=False)

                logger.info(f"Tool {name} completed successfully")
                return [types.TextContent(type="text", text=result_text)]

            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                error_result = {"error": f"Tool execution failed: {e!s}"}
                return [
                    types.TextContent(
                        type="text", text=json.dumps(error_result, indent=2)
                    )
                ]


def main():
    """Main entry point."""
    # Get base path from environment or use current directory
    base_path = os.getenv("MARKDOWN_MCP_BASE_PATH", ".")

    # Get Obsidian vault path from environment
    obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH")

    server = MarkdownMCPServer(base_path, obsidian_vault_path)
    logger.info("Starting Markdown MCP Server...")
    asyncio.run(stdio_server(server.server))


if __name__ == "__main__":
    main()
