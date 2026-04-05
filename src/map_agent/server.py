"""MCP Server for Map Agent with multi-provider support."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .providers.base import MapProvider, POI, Route
from .config import get_api_key, TransportConfig

logger = logging.getLogger(__name__)

# Global MCP server instance
mcp: Optional[FastMCP] = None

# Global provider instance
_provider: Optional[MapProvider] = None


def _get_provider() -> MapProvider:
    """Get or create the default provider instance."""
    global _provider
    if _provider is None:
        # Default to HMS provider for backward compatibility
        from .providers import create_provider, get_provider_config, get_default_provider
        provider_id = get_default_provider()
        config = get_provider_config(provider_id)
        _provider = create_provider(provider_id, **config)
        logger.info(f"Using provider: {provider_id}")
    return _provider


def set_provider(provider: MapProvider) -> None:
    """Set the provider instance for the MCP server.

    Args:
        provider: Provider instance to use
    """
    global _provider
    _provider = provider
    logger.info(f"Set provider to: {provider.provider_id}")


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


def create_server(provider_id: Optional[str] = None) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        provider_id: Optional provider ID to use (default: from env or 'hms')

    Returns:
        Configured FastMCP instance
    """
    global mcp

    if provider_id is None:
        from .providers import get_default_provider
        provider_id = get_default_provider()

    # Set up provider
    _get_provider()

    # Create MCP server with provider-specific instructions
    provider_name = _provider.provider_name if _provider else provider_id
    mcp = FastMCP(
        name=f"map-agent-{provider_id}",
        instructions=(
            f"Multi-provider Map Agent using {provider_name}. "
            f"Capabilities: nearby search, keyword search, place details, "
            f"query suggestions, geocoding, reverse geocoding, and "
            f"driving/walking/bicycling/cycling route planning. "
            f"Coordinates use (lng, lat) format. "
            f"Provider: {provider_id}"
        ),
    )

    # Register tools dynamically based on provider
    _register_provider_tools(mcp)

    return mcp


def _register_provider_tools(mcp_server: FastMCP) -> None:
    """Register MCP tools for the current provider.

    This dynamically creates tools that delegate to the provider instance.
    """
    provider = _get_provider()

    @mcp_server.tool()
    async def search_nearby(
        lng: float,
        lat: float,
        query: str | None = None,
        radius: int | None = 1000,
        category: str | None = None,
        language: str | None = None,
        page_size: int = 20,
        page_index: int = 1,
    ) -> str:
        """Search for places near a given location."""
        try:
            pois = await provider.search_nearby(
                lat=lat, lon=lng, radius=radius, keyword=query,
                category=category, language=language,
                page_size=page_size, page_index=page_index,
            )
            return json.dumps({
                "returnCode": "0",
                "sites": [_poi_to_dict(p) for p in pois],
                "totalCount": len(pois),
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def search_keyword(
        query: str,
        lng: float | None = None,
        lat: float | None = None,
        radius: int | None = None,
        category: str | None = None,
        language: str | None = None,
        page_size: int = 20,
        page_index: int = 1,
    ) -> str:
        """Search for places by keyword."""
        try:
            pois = await provider.search_keyword(
                keyword=query, lat=lat, lon=lng, radius=radius,
                category=category, language=language,
                page_size=page_size, page_index=page_index,
            )
            return json.dumps({
                "returnCode": "0",
                "sites": [_poi_to_dict(p) for p in pois],
                "totalCount": len(pois),
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def place_detail(
        poi_id: str,
        language: str | None = None,
    ) -> str:
        """Get detailed information about a place."""
        try:
            poi = await provider.get_poi_detail(poi_id, language=language)
            return json.dumps({
                "returnCode": "0",
                "site": _poi_to_dict(poi),
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def query_suggestion(
        query: str,
        lng: float | None = None,
        lat: float | None = None,
        radius: int | None = None,
        language: str | None = None,
    ) -> str:
        """Get search query suggestions."""
        try:
            suggestions = await provider.search_suggestion(
                keyword=query, lat=lat, lon=lng, radius=radius, language=language,
            )
            return json.dumps({
                "returnCode": "0",
                "suggestions": suggestions,
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def geocode(
        address: str,
        language: str | None = None,
    ) -> str:
        """Convert address to coordinates."""
        try:
            results = await provider.geocode(address, language=language)
            return json.dumps({
                "returnCode": "0",
                "sites": [{
                    "name": r.formatted_address or "",
                    "location": {"lat": r.lat, "lng": r.lon},
                } for r in results],
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def reverse_geocode(
        lng: float,
        lat: float,
        language: str | None = None,
        radius: int | None = None,
    ) -> str:
        """Convert coordinates to address."""
        try:
            result = await provider.reverse_geocode(lat, lng, language=language, radius=radius)
            return json.dumps({
                "returnCode": "0",
                "sites": [result] if isinstance(result, dict) else [],
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def driving_route(
        origin_lng: float,
        origin_lat: float,
        dest_lng: float,
        dest_lat: float,
        waypoints: list[dict] | None = None,
        avoid: list[str] | None = None,
        alternatives: bool = False,
        language: str | None = None,
    ) -> str:
        """Plan a driving route."""
        try:
            wp = [(w["lat"], w["lng"]) for w in waypoints] if waypoints else None
            route = await provider.route(
                origin_lat=origin_lat, origin_lon=origin_lng,
                dest_lat=dest_lat, dest_lon=dest_lng,
                mode="driving", waypoints=wp,
                avoid=avoid, alternatives=alternatives, language=language,
            )
            return json.dumps({
                "returnCode": "0",
                "routes": [_route_to_dict(r) for r in [route]],
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def walking_route(
        origin_lng: float,
        origin_lat: float,
        dest_lng: float,
        dest_lat: float,
        language: str | None = None,
    ) -> str:
        """Plan a walking route."""
        try:
            route = await provider.route(
                origin_lat=origin_lat, origin_lon=origin_lng,
                dest_lat=dest_lat, dest_lon=dest_lng,
                mode="walking", language=language,
            )
            return json.dumps({
                "returnCode": "0",
                "routes": [_route_to_dict(r) for r in [route]],
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)

    @mcp_server.tool()
    async def bicycling_route(
        origin_lng: float,
        origin_lat: float,
        dest_lng: float,
        dest_lat: float,
        avoid: list[str] | None = None,
        language: str | None = None,
    ) -> str:
        """Plan a bicycling route."""
        try:
            route = await provider.route(
                origin_lat=origin_lat, origin_lon=origin_lng,
                dest_lat=dest_lat, dest_lon=dest_lng,
                mode="cycling", avoid=avoid, language=language,
            )
            return json.dumps({
                "returnCode": "0",
                "routes": [_route_to_dict(r) for r in [route]],
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": True, "message": str(e)}, ensure_ascii=False)


def _poi_to_dict(poi: POI) -> dict:
    """Convert POI object to dict."""
    return {
        "siteId": poi.poi_id,
        "name": poi.name,
        "formatAddress": poi.address,
        "location": {"lat": poi.lat, "lng": poi.lon},
        "distance": poi.distance,
        "poi": {
            "type": poi.category,
            "phone": poi.phone,
            "websiteUrl": poi.website,
        } if any([poi.category, poi.phone, poi.website]) else None,
    }


def _route_to_dict(route: Route) -> dict:
    """Convert Route object to dict."""
    return {
        "distance": route.distance,
        "duration": route.duration,
        "bounds": route.bounds,
        "polyline": route.polyline,
        "steps": [
            {
                "instruction": s.instruction,
                "distance": s.distance,
                "duration": s.duration,
                "action": s.maneuver,
            }
            for s in route.steps
        ],
    }


def main() -> None:
    """Entry point for MCP server (stdio transport).

    For backward compatibility, defaults to HMS provider.
    """
    create_server().run()
