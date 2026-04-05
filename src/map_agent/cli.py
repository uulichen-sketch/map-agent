from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import click

from .client import HMSMapClient
from .config import get_api_key
from .exceptions import HMSMapError
from .formatters import format_json, format_text
from .models import (
    BicyclingRouteParams,
    Coordinate,
    DrivingRouteParams,
    GeocodeParams,
    KeywordSearchParams,
    NearbySearchParams,
    PlaceDetailParams,
    QuerySuggestionParams,
    ReverseGeocodeParams,
    WalkingRouteParams,
)


def _output(data: Any, fmt: str) -> None:
    if fmt == "text":
        click.echo(format_text(data))
    else:
        click.echo(format_json(data))


def _run(coro: Any, fmt: str) -> None:
    try:
        result = asyncio.run(coro)
        _output(result, fmt)
    except HMSMapError as e:
        _output({"error": True, "message": str(e)}, fmt)
        sys.exit(1)


@click.group()
@click.option("--api-key", envvar="HUAWEI_MAP_API_KEY", help="Huawei Map API Key")
@click.option("--format", "output_format", type=click.Choice(["json", "text"]), default="json", help="Output format")
@click.pass_context
def cli(ctx: click.Context, api_key: str | None, output_format: str) -> None:
    """Huawei Map Kit CLI - Place search, geocoding, and route planning."""
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["format"] = output_format


@cli.command()
@click.option("--lng", type=float, required=True, help="Longitude")
@click.option("--lat", type=float, required=True, help="Latitude")
@click.option("--query", default=None, help="Search keyword")
@click.option("--radius", type=int, default=1000, help="Search radius in meters")
@click.option("--language", default=None, help="Response language")
@click.option("--page-size", type=int, default=20, help="Results per page")
@click.option("--page-index", type=int, default=1, help="Page number")
@click.pass_context
def nearby(ctx: click.Context, lng: float, lat: float, query: str | None, radius: int,
           language: str | None, page_size: int, page_index: int) -> None:
    """Search for places near a location."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            result = await c.search_nearby(NearbySearchParams(
                location=Coordinate(lng=lng, lat=lat),
                query=query, radius=radius, language=language,
                pageSize=page_size, pageIndex=page_index,
            ))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.argument("query")
@click.option("--lng", type=float, default=None, help="Center longitude")
@click.option("--lat", type=float, default=None, help="Center latitude")
@click.option("--radius", type=int, default=None, help="Search radius in meters")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def keyword(ctx: click.Context, query: str, lng: float | None, lat: float | None,
            radius: int | None, language: str | None) -> None:
    """Search for places by keyword."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            location = Coordinate(lng=lng, lat=lat) if lng is not None and lat is not None else None
            result = await c.search_by_keyword(KeywordSearchParams(
                query=query, location=location, radius=radius, language=language,
            ))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.argument("site_id")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def detail(ctx: click.Context, site_id: str, language: str | None) -> None:
    """Get detailed info about a place by its ID."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            result = await c.search_by_id(PlaceDetailParams(siteId=site_id, language=language))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.argument("query")
@click.option("--lng", type=float, default=None, help="Bias longitude")
@click.option("--lat", type=float, default=None, help="Bias latitude")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def suggest(ctx: click.Context, query: str, lng: float | None, lat: float | None,
            language: str | None) -> None:
    """Get search query suggestions / autocomplete."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            location = Coordinate(lng=lng, lat=lat) if lng is not None and lat is not None else None
            result = await c.query_suggestion(QuerySuggestionParams(
                query=query, location=location, language=language,
            ))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.argument("address")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def geocode(ctx: click.Context, address: str, language: str | None) -> None:
    """Convert address to coordinates."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            result = await c.geocode(GeocodeParams(address=address, language=language))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.option("--lng", type=float, required=True, help="Longitude")
@click.option("--lat", type=float, required=True, help="Latitude")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def reverse_geocode(ctx: click.Context, lng: float, lat: float, language: str | None) -> None:
    """Convert coordinates to address."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            result = await c.reverse_geocode(ReverseGeocodeParams(
                location=Coordinate(lng=lng, lat=lat), language=language,
            ))
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.option("--origin", type=str, required=True, help="Origin as 'lng,lat'")
@click.option("--dest", type=str, required=True, help="Destination as 'lng,lat'")
@click.option("--mode", type=click.Choice(["driving", "walking", "bicycling"]), default="driving")
@click.option("--language", default=None, help="Response language")
@click.pass_context
def route(ctx: click.Context, origin: str, dest: str, mode: str, language: str | None) -> None:
    """Plan a route between two points."""
    api_key = ctx.obj["api_key"] or get_api_key()
    fmt = ctx.obj["format"]

    try:
        o_lng, o_lat = (float(x) for x in origin.split(","))
        d_lng, d_lat = (float(x) for x in dest.split(","))
    except ValueError:
        click.echo({"error": True, "message": "Origin and dest must be 'lng,lat' format"}, fmt)
        sys.exit(1)

    async def _cmd() -> dict:
        async with HMSMapClient(api_key) as c:
            if mode == "driving":
                params = DrivingRouteParams(
                    origin=Coordinate(lng=o_lng, lat=o_lat),
                    destination=Coordinate(lng=d_lng, lat=d_lat),
                    language=language,
                )
                result = await c.driving_directions(params)
            elif mode == "walking":
                params = WalkingRouteParams(
                    origin=Coordinate(lng=o_lng, lat=o_lat),
                    destination=Coordinate(lng=d_lng, lat=d_lat),
                    language=language,
                )
                result = await c.walking_directions(params)
            else:
                params = BicyclingRouteParams(
                    origin=Coordinate(lng=o_lng, lat=o_lat),
                    destination=Coordinate(lng=d_lng, lat=d_lat),
                    language=language,
                )
                result = await c.bicycling_directions(params)
            return result.model_dump(mode="json", exclude_none=True)

    _run(_cmd(), fmt)


@cli.command()
@click.option("--transport", type=click.Choice(["stdio", "sse", "streamable-http"]), default="stdio", help="Transport protocol (stdio/sse/streamable-http)")
@click.option("--host", default="0.0.0.0", help="Host for SSE/streamable-http transports")
@click.option("--port", default=8000, type=int, help="Port for SSE/streamable-http transports")
@click.option("--provider", default="hms", help="Map provider (hms/gaode/google)")
def serve(transport: str, host: str, port: int, provider: str) -> None:
    """Start MCP server.

    Supports three transport modes:
    - stdio: Standard input/output (default, best for local tools)
    - sse: Server-Sent Events over HTTP (better for web clients)
    - streamable-http: Streamable HTTP for long-running operations

    Examples:
        # Default stdio transport with HMS provider
        map-agent serve

        # SSE transport for web clients
        map-agent serve --transport sse --host 0.0.0.0 --port 8000

        # Streamable-http for long-running ops
        map-agent serve --transport streamable-http --host 0.0.0.0 --port 8001
    """
    from .server import create_server, set_provider
    from .providers import create_provider, get_provider_config

    # Load provider configuration
    try:
        config = get_provider_config(provider)
        provider_instance = create_provider(provider, **config)
    except Exception as e:
        click.echo(f"Error loading provider '{provider}': {e}", err=True)
        sys.exit(1)

    # Create MCP server and set provider
    server = create_server(provider_id=provider)
    set_provider(provider_instance)

    async def run_server():
        if transport == "stdio":
            # Stdio is the default and requires no additional setup
            click.echo("Starting MCP server with stdio transport...")
            await server.run_stdin_stdout()
        elif transport == "sse":
            from .transports.sse import run_sse_server
            click.echo(f"Starting MCP server with SSE transport on {host}:{port}...")
            await run_sse_server(server, host, port)
        elif transport == "streamable-http":
            from .transports.streamable_http import run_streamable_http_server
            click.echo(f"Starting MCP server with streamable-http transport on {host}:{port}...")
            await run_streamable_http_server(server, host, port)

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")
    except Exception as e:
        click.echo(f"Server error: {e}", err=True)
        sys.exit(1)
