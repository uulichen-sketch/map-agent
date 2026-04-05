"""Streamable-HTTP transport implementation."""

import asyncio
import logging
from typing import Optional

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logger = logging.getLogger(__name__)


async def run_streamable_http_server(
    server,
    host: str = "0.0.0.0",
    port: int = 8001,
):
    """Run MCP server with streamable-http transport.

    Args:
        server: MCP server instance
        host: Host to bind to
        port: Port to listen on

    Note:
        Streamable-http is optimized for long-running operations with progress updates.
        It uses a single endpoint for all communication, supporting streaming responses.

        This transport is better suited for:
        - Long-running API calls
        - Operations with progress updates
        - Operations that return large responses
    """
    try:
        # Import streamable-http transport from mcp package
        from mcp.server.streamable_http import StreamableHttpServerTransport

        # Create transport instance
        transport = StreamableHttpServerTransport("/mcp/stream")

        async def handle_request(request: Request):
            """Handle streamable-http request."""
            logger.debug(f"Streamable-HTTP request from {request.client}")

            # Let the transport handle the request
            response = await transport.handle_request(request)
            return response

        app = Starlette(
            debug=False,
            routes=[
                Route("/mcp/stream", endpoint=handle_request, methods=["POST"]),
            ],
        )

        logger.info(f"Starting streamable-http server on {host}:{port}")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

    except ImportError as e:
        logger.error(f"Streamable-HTTP transport not available: {e}")
        raise RuntimeError(
            "Streamable-HTTP transport requires mcp>=1.2.0 with streamable-http support. "
            "Install with: pip install 'mcp[streamable-http]'"
        ) from e
