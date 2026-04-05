# Phase 1 Task: SSE/Streamable-HTTP Transport Support

## Objective
Add SSE (Server-Sent Events) and streamable-http transport support to map-agent MCP server.

## Current Status
- Only stdio transport is currently supported
- Competitors (百度/高德 MCP) support SSE and streamable-http
- SSE enables better integration with web-based clients
- Streamable-http supports long-running operations

## Requirements

### 1. SSE Transport Implementation
Create `src/map_agent/transports/sse.py`:

```python
import asyncio
import json
from typing import AsyncIterator
from mcp.server import Server
from mcp.server.sse import SseServerTransport

async def run_sse_server(
    server: Server,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    """Run MCP server with SSE transport"""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.requests import Request
    from mcp.server.sse import SseServerTransport

    # SSE endpoint for server-sent events
    async def handle_sse(request: Request):
        async with SseServerTransport("/messages") as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    app = Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ],
    )

    import uvicorn
    await uvicorn.run(app, host=host, port=port)
```

### 2. Update CLI to Support Multiple Transports
Modify `src/map_agent/cli.py`:

```python
@click.group()
def cli():
    """Map Agent - Multi-provider Map MCP Server"""
    pass

@cli.command()
@click.option("--transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help="Transport protocol")
@click.option("--host", default="0.0.0.0", help="Host for SSE/streamable-http")
@click.option("--port", default=8000, help="Port for SSE/streamable-http")
def serve(transport: str, host: str, port: int):
    """Start MCP server"""
    import asyncio
    from map_agent.server import create_server

    server = create_server()

    if transport == "stdio":
        asyncio.run(server.run_stdin_stdout())
    elif transport == "sse":
        from map_agent.transports.sse import run_sse_server
        asyncio.run(run_sse_server(server, host, port))
    elif transport == "streamable-http":
        from map_agent.transports.streamable_http import run_streamable_http_server
        asyncio.run(run_streamable_http_server(server, host, port))
```

### 3. Streamable-HTTP Transport
Create `src/map_agent/transports/streamable_http.py`:

```python
import asyncio
from typing import Optional
from mcp.server import Server

async def run_streamable_http_server(
    server: Server,
    host: str = "0.0.0.0",
    port: int = 8001,
):
    """Run MCP server with streamable-http transport"""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from mcp.server.streamable_http import StreamableHttpServerTransport

    transport = StreamableHttpServerTransport("/mcp/stream")

    app = Starlette(
        debug=False,
        routes=[
            Route("/mcp/stream", endpoint=transport.handle_request, methods=["POST"]),
        ],
    )

    import uvicorn
    await uvicorn.run(app, host=host, port=port)
```

### 4. Dependencies
Update `pyproject.toml`:

```toml
dependencies = [
    "httpx>=0.27",
    "click>=8.0",
    "mcp>=1.2.0",
    "pydantic>=2.0",
    "starlette>=0.27",  # for SSE and streamable-http
    "uvicorn[standard]>=0.23",  # ASGI server
    "sse-starlette>=1.6",  # SSE support
]

[project.optional-dependencies]
transport = [
    "starlette>=0.27",
    "uvicorn[standard]>=0.23",
    "sse-starlette>=1.6",
]
```

### 5. Configuration
Update `src/map_agent/config.py`:

```python
import os
from typing import Optional

class TransportConfig:
    """Transport configuration"""
    mode: str = os.getenv("MAP_AGENT_TRANSPORT", "stdio")  # stdio, sse, streamable-http
    host: str = os.getenv("MAP_AGENT_HOST", "0.0.0.0")
    port: int = int(os.getenv("MAP_AGENT_PORT", "8000"))
```

### 6. Documentation
Update README with transport examples:

```bash
# Stdio transport (default)
map-agent-mcp

# SSE transport
map-agent serve --transport sse --host 0.0.0.0 --port 8000

# Streamable-HTTP transport
map-agent serve --transport streamable-http --host 0.0.0.0 --port 8001
```

## Acceptance Criteria
- [ ] SSE transport implementation working with /sse endpoint
- [ ] Streamable-http transport implementation working with /mcp/stream endpoint
- [ ] CLI updated to support --transport option
- [ ] Dependencies added to pyproject.toml
- [ ] Server can run with all three transports (stdio, sse, streamable-http)
- [ ] Configuration via environment variables
- [ ] Documentation updated with transport examples
- [ ] Type hints added
- [ ] Error handling for transport failures
- [ ] Unit tests for transport initialization

## Testing Commands

```bash
# Test stdio
map-agent-mcp

# Test SSE
map-agent serve --transport sse --host 127.0.0.1 --port 8000 &
curl http://127.0.0.1:8000/sse

# Test streamable-http
map-agent serve --transport streamable-http --host 127.0.0.1 --port 8001 &
curl -X POST http://127.0.0.1:8001/mcp/stream -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize"}'
```

## Next Steps
- Integrate with multi-provider architecture
- Add CORS support for web clients
- Add authentication (optional)
- Performance testing with concurrent requests

## Notes
- SSE is better for real-time updates from server to client
- Streamable-http is better for long-running operations with progress
- Keep stdio as default for backward compatibility
- Consider using mcp.transport helpers if available
