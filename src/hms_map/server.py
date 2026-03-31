"""MCP Server for Huawei HMS Core Map Kit."""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import HMSMapClient
from .config import get_api_key
from .exceptions import HuaweiAPIError, NetworkError
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

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="hms-map-kit",
    instructions=(
        "Provides access to Huawei Map Kit capabilities including: "
        "nearby search, keyword search, place details, query suggestions, "
        "geocoding, reverse geocoding, and driving/walking/bicycling route planning. "
        "Coordinates use (lng, lat) format."
    ),
)

_client: HMSMapClient | None = None


def _get_client() -> HMSMapClient:
    global _client
    if _client is None:
        _client = HMSMapClient(get_api_key())
    return _client


def _safe_json(data: Any) -> dict:
    if isinstance(data, dict):
        return data
    return data.model_dump(mode="json", exclude_none=True)


# ---------- Search tools ----------


@mcp.tool()
async def search_nearby(
    lng: float,
    lat: float,
    query: str | None = None,
    radius: int | None = 1000,
    hwPoiType: str | None = None,
    language: str | None = None,
    pageSize: int | None = 20,
    pageIndex: int | None = 1,
) -> str:
    """Search for places near a given location.

    Returns a list of nearby places (POIs) sorted by distance.
    Use query to filter by keyword, hwPoiType to filter by category.
    """
    client = _get_client()
    params = NearbySearchParams(
        location=Coordinate(lng=lng, lat=lat),
        query=query,
        radius=radius,
        hwPoiType=hwPoiType,
        language=language,
        pageSize=pageSize,
        pageIndex=pageIndex,
    )
    try:
        result = await client.search_nearby(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def search_keyword(
    query: str,
    lng: float | None = None,
    lat: float | None = None,
    radius: int | None = None,
    hwPoiType: str | None = None,
    language: str | None = None,
    pageSize: int | None = 20,
    pageIndex: int | None = 1,
) -> str:
    """Search for places by keyword across a region.

    Optionally narrow results by center location and radius.
    """
    client = _get_client()
    location = Coordinate(lng=lng, lat=lat) if lng is not None and lat is not None else None
    params = KeywordSearchParams(
        query=query,
        location=location,
        radius=radius,
        hwPoiType=hwPoiType,
        language=language,
        pageSize=pageSize,
        pageIndex=pageIndex,
    )
    try:
        result = await client.search_by_keyword(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def place_detail(
    siteId: str,
    language: str | None = None,
) -> str:
    """Get detailed information about a place by its site ID.

    Use this after a search to get full details including address,
    phone, website, rating, and opening hours.
    """
    client = _get_client()
    params = PlaceDetailParams(siteId=siteId, language=language)
    try:
        result = await client.search_by_id(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def query_suggestion(
    query: str,
    lng: float | None = None,
    lat: float | None = None,
    radius: int | None = None,
    language: str | None = None,
) -> str:
    """Get search query suggestions / autocomplete.

    Returns suggested search terms as the user types.
    Bias results toward a location if provided.
    """
    client = _get_client()
    location = Coordinate(lng=lng, lat=lat) if lng is not None and lat is not None else None
    params = QuerySuggestionParams(
        query=query,
        location=location,
        radius=radius,
        language=language,
    )
    try:
        result = await client.query_suggestion(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


# ---------- Geocoding tools ----------


@mcp.tool()
async def geocode(
    address: str,
    language: str | None = None,
) -> str:
    """Convert a structured address to geographic coordinates (forward geocoding).

    Returns matching locations with coordinates.
    """
    client = _get_client()
    params = GeocodeParams(address=address, language=language)
    try:
        result = await client.geocode(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def reverse_geocode(
    lng: float,
    lat: float,
    language: str | None = None,
    radius: int | None = None,
) -> str:
    """Convert geographic coordinates to an address (reverse geocoding).

    Returns matching addresses for the given coordinates.
    """
    client = _get_client()
    params = ReverseGeocodeParams(
        location=Coordinate(lng=lng, lat=lat),
        language=language,
        radius=radius,
    )
    try:
        result = await client.reverse_geocode(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


# ---------- Route planning tools ----------


@mcp.tool()
async def driving_route(
    origin_lng: float,
    origin_lat: float,
    dest_lng: float,
    dest_lat: float,
    waypoints: list[dict] | None = None,
    avoid: list[int] | None = None,
    alternatives: bool | None = None,
    language: str | None = None,
) -> str:
    """Plan a driving route between two points.

    Returns route with distance, duration, and turn-by-turn steps.
    Use avoid=[1] to avoid tolls, avoid=[2] to avoid highways.
    Set alternatives=true to get multiple route options.
    """
    client = _get_client()
    wp = [Coordinate(**w) for w in waypoints] if waypoints else None
    params = DrivingRouteParams(
        origin=Coordinate(lng=origin_lng, lat=origin_lat),
        destination=Coordinate(lng=dest_lng, lat=dest_lat),
        waypoints=wp,
        avoid=avoid,
        alternatives=alternatives,
        language=language,
    )
    try:
        result = await client.driving_directions(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def walking_route(
    origin_lng: float,
    origin_lat: float,
    dest_lng: float,
    dest_lat: float,
    language: str | None = None,
) -> str:
    """Plan a walking route between two points.

    Returns route with distance, duration, and step-by-step directions.
    """
    client = _get_client()
    params = WalkingRouteParams(
        origin=Coordinate(lng=origin_lng, lat=origin_lat),
        destination=Coordinate(lng=dest_lng, lat=dest_lat),
        language=language,
    )
    try:
        result = await client.walking_directions(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


@mcp.tool()
async def bicycling_route(
    origin_lng: float,
    origin_lat: float,
    dest_lng: float,
    dest_lat: float,
    avoid: list[int] | None = None,
    language: str | None = None,
) -> str:
    """Plan a bicycling route between two points.

    Returns route with distance, duration, and step-by-step directions.
    Use avoid=[8] to avoid ferries.
    """
    client = _get_client()
    params = BicyclingRouteParams(
        origin=Coordinate(lng=origin_lng, lat=origin_lat),
        destination=Coordinate(lng=dest_lng, lat=dest_lat),
        avoid=avoid,
        language=language,
    )
    try:
        result = await client.bicycling_directions(params)
    except (HuaweiAPIError, NetworkError) as e:
        return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)
    return json.dumps(_safe_json(result), ensure_ascii=False)


def main() -> None:
    """Entry point for MCP server (stdio transport)."""
    mcp.run()
