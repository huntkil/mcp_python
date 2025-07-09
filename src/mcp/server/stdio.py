"""
STDIO server implementation for MCP.
"""

import asyncio
import json
import logging
import sys

from .server import Server


async def stdio_server(server: Server):
    """
    Run the MCP server using STDIO protocol.

    Args:
        server: MCP server instance
    """
    logger = logging.getLogger("mcp.stdio")

    try:
        while True:
            # Read request from stdin
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            if not line:
                break

            try:
                request = json.loads(line.strip())
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")

                logger.info(f"Received request: {method}")

                # Handle different methods
                if method == "tools/list":
                    tools = await server.handle_list_tools()
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "inputSchema": tool.inputSchema,
                                }
                                for tool in tools
                            ]
                        },
                    }

                elif method == "tools/call":
                    name = params.get("name")
                    arguments = params.get("arguments", {})

                    result = await server.handle_call_tool(name, arguments)

                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {"type": content.type, "text": content.text}
                                for content in result
                            ]
                        },
                    }

                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}",
                        },
                    }

                # Send response to stdout
                response_json = json.dumps(response, ensure_ascii=False)
                print(response_json, flush=True)

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                print(json.dumps(error_response), flush=True)

            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32603, "message": "Internal error"},
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
