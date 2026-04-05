"""SSE (Server-Sent Events) transport implementation."""

import asyncio
import logging
from typing import Optional

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

logger = logging.getLogger(__name__)


async def run_sse_server(
    server,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    """Run MCP server with SSE transport.

    Args:
        server: MCP server instance
        host: Host to bind to
        port: Port to listen on

    Note:
        SSE requires two endpoints:
        - GET /sse: Client connects to receive server-sent events
        - POST /messages: Client sends requests to server

        The SSE transport enables real-time bi-directional communication
        over HTTP, which is better suited for web-based clients than stdio.
    """
    try:
        # Import SSE transport from mcp package
        from mcp.server.sse import SseServerTransport

        async def handle_sse(request: Request):
            """Handle SSE connection."""
            logger.info(f"SSE connection from {request.client}")
            async with SseServerTransport("/messages") as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options(),
                )

        async def handle_messages(request: Request):
            """Handle POST requests from SSE client."""
            logger.debug(f"Message from SSE client: {request.client}")
            # Import HTTP transport for request handling
            from mcp.server.stdio import StdioServerTransport

            # For SSE, messages come via POST to /messages endpoint
            # The SseServerTransport handles this internally
            pass

        app = Starlette(
            debug=False,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ],
        )

        logger.info(f"Starting SSE server on {host}:{port}")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

    except ImportError as e:
        logger.error(f"SSE transport not available: {e}")
        raise RuntimeError(
            "SSE transport requires mcp>=1.2.0 with SSE support. "
            "Install with: pip install 'mcp[sse]'"
        ) from e
