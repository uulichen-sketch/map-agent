"""Huawei Map Kit provider implementation."""

from typing import Optional, List, Tuple

from ..client import HMSMapClient
from ..models import (
    BicyclingRouteParams,
    DrivingRouteParams,
    GeocodeParams,
    GeocodeResult as HMSGeocodeResult,
    KeywordSearchParams,
    NearbySearchParams,
    PlaceDetailParams,
    PlaceDetailResult,
    QuerySuggestionParams,
    ReverseGeocodeParams,
    RouteResult as HMSRouteResult,
    SiteSearchResult,
    SuggestionResult,
)
from ..exceptions import HuaweiAPIError as HMSAPIError, NetworkError as HMSNetworkError
from .base import (
    MapProvider,
    POI,
    Route,
    RouteStep,
    GeocodeResult,
    APIError,
    NetworkError,
    NotFoundError,
    InvalidRouteError,
)


class HMSProvider(MapProvider):
    """Huawei Map Kit provider.

    Uses the HMS Map Kit REST API for all map operations.

    Attributes:
        provider_id: "hms"
        provider_name: "Huawei Map Kit"
    """

    provider_id = "hms"
    provider_name = "Huawei Map Kit"

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize HMS provider.

        Args:
            api_key: Huawei Map Kit API key
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._timeout = timeout
        self._client: Optional[HMSMapClient] = None

    def _get_client(self) -> HMSMapClient:
        """Get or create HMS client instance."""
        if self._client is None:
            self._client = HMSMapClient(self._api_key, timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        """Close the HMS client."""
        if self._client:
            await self._client.close()
            self._client = None

    async def __aenter__(self) -> "HMSProvider":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    def _convert_hms_error(self, exc: Exception) -> Exception:
        """Convert HMS exception to provider exception.

        Args:
            exc: HMS-specific exception

        Returns:
            Provider-specific exception
        """
        if isinstance(exc, HMSAPIError):
            return APIError(exc.message, code=exc.code)
        if isinstance(exc, HMSNetworkError):
            return NetworkError(str(exc))
        return exc

    def _hms_site_to_poi(self, site: dict) -> POI:
        """Convert HMS site result to POI.

        Args:
            site: HMS site dict

        Returns:
            POI object
        """
        location = site.get("location", {})
        poi_info = site.get("poi", {})
        address_info = site.get("address", {})

        return POI(
            name=site.get("name", ""),
            address=site.get("formatAddress", ""),
            lat=location.get("lat", 0.0),
            lon=location.get("lng", 0.0),
            distance=site.get("distance"),
            category=poi_info.get("type"),
            poi_id=site.get("siteId"),
            phone=poi_info.get("phone"),
            website=poi_info.get("websiteUrl"),
            rating=poi_info.get("rating"),
        )

    def _hms_route_to_route(self, route: dict) -> Route:
        """Convert HMS route result to Route.

        Args:
            route: HMS route dict

        Returns:
            Route object
        """
        steps_data = route.get("steps", [])
        steps = []

        for step in steps_data:
            steps.append(
                RouteStep(
                    instruction=step.get("instruction", ""),
                    distance=step.get("distance", 0),
                    duration=step.get("duration", 0),
                    maneuver=step.get("action"),
                )
            )

        return Route(
            distance=route.get("distance", 0),
            duration=route.get("duration", 0),
            steps=steps,
            polyline=route.get("polyline"),
            bounds=route.get("bounds"),
        )

    async def search_nearby(
        self,
        lat: float,
        lon: float,
        radius: int,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        page_size: int = 20,
        page_index: int = 1,
    ) -> List[POI]:
        """Search for POIs near a given location."""
        try:
            client = self._get_client()

            from ..models import Coordinate
            params = NearbySearchParams(
                location=Coordinate(lng=lon, lat=lat),
                query=keyword,
                radius=radius,
                hwPoiType=category,
                language=language,
                pageSize=page_size,
                pageIndex=page_index,
            )

            result = await client.search_nearby(params)
            return [self._hms_site_to_poi(s) for s in result.sites]

        except Exception as e:
            raise self._convert_hms_error(e) from e

    async def search_keyword(
        self,
        keyword: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[int] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        page_size: int = 20,
        page_index: int = 1,
    ) -> List[POI]:
        """Search for POIs by keyword across a region."""
        try:
            client = self._get_client()

            location = None
            if lat is not None and lon is not None:
                from ..models import Coordinate
                location = Coordinate(lng=lon, lat=lat)

            params = KeywordSearchParams(
                query=keyword,
                location=location,
                radius=radius,
                hwPoiType=category,
                language=language,
                pageSize=page_size,
                pageIndex=page_index,
            )

            result = await client.search_by_keyword(params)
            return [self._hms_site_to_poi(s) for s in result.sites]

        except Exception as e:
            raise self._convert_hms_error(e) from e

    async def get_poi_detail(
        self,
        poi_id: str,
        language: Optional[str] = None,
    ) -> POI:
        """Get detailed information about a POI."""
        try:
            client = self._get_client()

            params = PlaceDetailParams(siteId=poi_id, language=language)
            result = await client.search_by_id(params)

            if result.returnCode != "0":
                raise NotFoundError(f"POI not found: {poi_id}")

            return self._hms_site_to_poi(result.site.model_dump() if result.site else {})

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise self._convert_hms_error(e) from e

    async def search_suggestion(
        self,
        keyword: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[int] = None,
        language: Optional[str] = None,
    ) -> List[str]:
        """Get search query suggestions / autocomplete."""
        try:
            client = self._get_client()

            location = None
            if lat is not None and lon is not None:
                from ..models import Coordinate
                location = Coordinate(lng=lon, lat=lat)

            params = QuerySuggestionParams(
                query=keyword,
                location=location,
                radius=radius,
                language=language,
            )

            result = await client.query_suggestion(params)

            # Extract suggestion texts
            return [
                s.get("title", s.get("text", ""))
                for s in result.suggestions
            ]

        except Exception as e:
            raise self._convert_hms_error(e) from e

    async def geocode(
        self,
        address: str,
        language: Optional[str] = None,
    ) -> List[GeocodeResult]:
        """Convert an address to geographic coordinates (forward geocoding)."""
        try:
            client = self._get_client()

            params = GeocodeParams(address=address, language=language)
            result = await client.geocode(params)

            return [
                GeocodeResult(
                    lat=site.get("location", {}).get("lat", 0.0),
                    lon=site.get("location", {}).get("lng", 0.0),
                    formatted_address=site.get("formatAddress"),
                    address_components=site.get("address"),
                )
                for site in result.sites
            ]

        except Exception as e:
            raise self._convert_hms_error(e) from e

    async def reverse_geocode(
        self,
        lat: float,
        lon: float,
        language: Optional[str] = None,
        radius: Optional[int] = None,
    ) -> dict:
        """Convert geographic coordinates to an address (reverse geocoding)."""
        try:
            client = self._get_client()

            from ..models import Coordinate
            params = ReverseGeocodeParams(
                location=Coordinate(lng=lon, lat=lat),
                language=language,
                radius=radius,
            )

            result = await client.reverse_geocode(params)

            if not result.sites:
                raise NotFoundError(f"No address found for coordinates: {lat}, {lon}")

            # Return the first result as dict
            first_site = result.sites[0]
            return {
                "lat": lat,
                "lon": lon,
                "formatted_address": first_site.get("formatAddress"),
                "address_components": first_site.get("address"),
                "returnCode": result.returnCode,
            }

        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise self._convert_hms_error(e) from e

    async def route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        mode: str = "driving",
        waypoints: Optional[List[Tuple[float, float]]] = None,
        avoid: Optional[List[str]] = None,
        alternatives: bool = False,
        language: Optional[str] = None,
    ) -> Route:
        """Plan a route between two points."""
        try:
            client = self._get_client()

            from ..models import Coordinate

            # Build origin and destination
            origin = Coordinate(lng=origin_lon, lat=origin_lat)
            destination = Coordinate(lng=dest_lon, lat=dest_lat)

            # Convert waypoints
            wp_coords = None
            if waypoints:
                wp_coords = [Coordinate(lng=w[1], lat=w[0]) for w in waypoints]

            # Convert avoid list (HMS uses integers: 1=toll, 2=highway, 8=ferry)
            avoid_ints = None
            if avoid:
                avoid_mapping = {"toll": 1, "highway": 2, "ferry": 8}
                avoid_ints = [
                    avoid_mapping.get(a.lower()) for a in avoid if a.lower() in avoid_mapping
                ]

            # Call appropriate route method based on mode
            if mode == "driving":
                params = DrivingRouteParams(
                    origin=origin,
                    destination=destination,
                    waypoints=wp_coords,
                    avoid=avoid_ints,
                    alternatives=alternatives,
                    language=language,
                )
                result = await client.driving_directions(params)

            elif mode == "walking":
                from ..models import WalkingRouteParams
                params = WalkingRouteParams(
                    origin=origin,
                    destination=destination,
                    language=language,
                )
                result = await client.walking_directions(params)

            elif mode == "cycling":
                from ..models import BicyclingRouteParams
                params = BicyclingRouteParams(
                    origin=origin,
                    destination=destination,
                    avoid=avoid_ints,
                    language=language,
                )
                result = await client.bicycling_directions(params)

            else:
                raise InvalidRouteError(f"Unsupported route mode: {mode}")

            if not result.routes:
                raise InvalidRouteError(f"No route found for mode: {mode}")

            # Return the first (best) route
            return self._hms_route_to_route(result.routes[0])

        except Exception as e:
            if isinstance(e, InvalidRouteError):
                raise
            raise self._convert_hms_error(e) from e
