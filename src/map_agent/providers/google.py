"""Google Maps provider implementation.

Google Maps is widely used internationally for global coverage.
API docs: https://developers.google.com/maps/documentation
"""

from typing import Optional, List, Tuple
import httpx

from ..providers.base import MapProvider, POI, Route, RouteStep, GeocodeResult
from ..providers.base import APIError, NetworkError, NotFoundError, InvalidRouteError


class GoogleMapsProvider(MapProvider):
    """Google Maps provider.

    Uses Google Maps Platform REST API for all map operations.

    Attributes:
        provider_id: "google"
        provider_name: "Google Maps Platform"
    """

    provider_id = "google"
    provider_name = "Google Maps Platform"

    # Google Maps API endpoints
    GEOCODE_BASE = "https://maps.googleapis.com/maps/api/geocode/json"
    REVERSE_GEO_BASE = "https://maps.googleapis.com/maps/api/geocode/json"
    PLACES_NEARBY_BASE = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    PLACES_TEXT_BASE = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    PLACES_DETAIL_BASE = "https://maps.googleapis.com/maps/api/place/details/json"
    DIRECTIONS_BASE = "https://maps.googleapis.com/maps/api/directions/json"
    PLACE_AUTOCOMPLETE_BASE = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize Google Maps provider.

        Args:
            api_key: Google Maps API key (GOOGLE_MAPS_API_KEY)
            timeout: Request timeout in seconds
        """
        self._api_key = api_key
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "GoogleMapsProvider":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    def _check_api_status(self, data: dict) -> None:
        """Check Google Maps API response status."""
        if data.get("status") != "OK":
            error_message = data.get("error_message", "Unknown error")
            status = data.get("status", "UNKNOWN")
            if status == "ZERO_RESULTS":
                raise NotFoundError(error_message)
            elif status == "OVER_QUERY_LIMIT":
                raise APIError(f"Quota exceeded: {error_message}", code=status)
            elif status == "REQUEST_DENIED":
                raise APIError(f"Request denied: {error_message}", code=status)
            elif status == "INVALID_REQUEST":
                raise APIError(f"Invalid request: {error_message}", code=status)
            else:
                raise APIError(f"API error {status}: {error_message}", code=status)

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

            params = {
                "key": self._api_key,
                "location": f"{lat},{lon}",
                "radius": str(radius),
            }

            if keyword:
                params["keyword"] = keyword
            if category:
                # Google Maps uses type codes
                params["type"] = category
            if language:
                params["language"] = language

            resp = await client.get(self.PLACES_NEARBY_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            pois = []
            for result in data.get("results", []):
                location = result.get("geometry", {}).get("location", {})
                pois.append(
                    POI(
                        name=result.get("name", ""),
                        address=result.get("formatted_address", ""),
                        lat=location.get("lat", 0.0),
                        lon=location.get("lng", 0.0),
                        poi_id=result.get("place_id"),
                        category=result.get("types", [""])[0] if result.get("types") else None,
                    )
                )

            return pois

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

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

            params = {
                "key": self._api_key,
                "query": keyword,
            }

            if lat is not None and lon is not None:
                params["location"] = f"{lat},{lon}"
            if radius is not None:
                params["radius"] = str(radius)
            if language:
                params["language"] = language

            resp = await client.get(self.PLACES_TEXT_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            pois = []
            for result in data.get("results", []):
                location = result.get("geometry", {}).get("location", {})
                pois.append(
                    POI(
                        name=result.get("name", ""),
                        address=result.get("formatted_address", ""),
                        lat=location.get("lat", 0.0),
                        lon=location.get("lng", 0.0),
                        poi_id=result.get("place_id"),
                        category=result.get("types", [""])[0] if result.get("types") else None,
                    )
                )

            return pois

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

    async def get_poi_detail(
        self,
        poi_id: str,
        language: Optional[str] = None,
    ) -> POI:
        """Get detailed information about a POI."""
        try:
            client = self._get_client()

            params = {
                "key": self._api_key,
                "place_id": poi_id,
                "fields": "name,formatted_address,geometry,types,formatted_phone_number,website,rating",
            }

            if language:
                params["language"] = language

            resp = await client.get(self.PLACES_DETAIL_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            result = data.get("result", {})
            location = result.get("geometry", {}).get("location", {})

            return POI(
                name=result.get("name", ""),
                address=result.get("formatted_address", ""),
                lat=location.get("lat", 0.0),
                lon=location.get("lng", 0.0),
                poi_id=poi_id,
                phone=result.get("formatted_phone_number"),
                website=result.get("website"),
                rating=result.get("rating"),
            )

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

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

            params = {
                "key": self._api_key,
                "input": keyword,
            }

            if lat is not None and lon is not None:
                params["location"] = f"{lat},{lon}"
            if radius is not None:
                params["radius"] = str(radius)
            if language:
                params["language"] = language

            resp = await client.get(self.PLACE_AUTOCOMPLETE_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            # Extract descriptions as suggestions
            return [pred.get("description", "") for pred in data.get("predictions", [])]

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

    async def geocode(
        self,
        address: str,
        language: Optional[str] = None,
    ) -> List[GeocodeResult]:
        """Convert an address to geographic coordinates (forward geocoding)."""
        try:
            client = self._get_client()

            params = {
                "key": self._api_key,
                "address": address,
            }

            if language:
                params["language"] = language

            resp = await client.get(self.GEOCODE_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            geocodes = []
            for result in data.get("results", []):
                location = result.get("geometry", {}).get("location", {})
                geocodes.append(
                    GeocodeResult(
                        lat=location.get("lat", 0.0),
                        lon=location.get("lng", 0.0),
                        formatted_address=result.get("formatted_address", ""),
                        address_components=result.get("address_components", {}),
                    )
                )

            return geocodes

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

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

            params = {
                "key": self._api_key,
                "latlng": f"{lat},{lon}",
            }

            if language:
                params["language"] = language

            resp = await client.get(self.REVERSE_GEO_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            results = data.get("results", [])
            if not results:
                raise NotFoundError(f"No address found for coordinates: {lat}, {lon}")

            result = results[0]
            return {
                "lat": lat,
                "lon": lon,
                "formatted_address": result.get("formatted_address", ""),
                "address_components": result.get("address_components", {}),
                "returnCode": "0",
            }

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e

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

            # Google Maps mode mapping
            mode_map = {
                "driving": "driving",
                "walking": "walking",
                "cycling": "bicycling",
                "transit": "transit",
            }
            google_mode = mode_map.get(mode, "driving")

            params = {
                "key": self._api_key,
                "origin": f"{origin_lat},{origin_lon}",
                "destination": f"{dest_lat},{dest_lon}",
                "mode": google_mode,
            }

            # Add waypoints
            if waypoints:
                wp_str = "|".join([f"{w[0]},{w[1]}" for w in waypoints])
                params["waypoints"] = wp_str

            # Map avoid options
            avoid_options = []
            if avoid:
                if "toll" in avoid:
                    avoid_options.append("tolls")
                if "highway" in avoid:
                    avoid_options.append("highways")
                if "ferry" in avoid:
                    avoid_options.append("ferries")
            if avoid_options:
                params["avoid"] = "|".join(avoid_options)

            if alternatives:
                params["alternatives"] = "true"

            if language:
                params["language"] = language

            resp = await client.get(self.DIRECTIONS_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            self._check_api_status(data)

            routes = data.get("routes", [])
            if not routes:
                raise InvalidRouteError(f"No route found for mode: {mode}")

            # Use the first (best) route
            route_data = routes[0]
            legs = route_data.get("legs", [])

            steps = []
            total_distance = 0
            total_duration = 0

            for leg in legs:
                total_distance += leg.get("distance", {}).get("value", 0)
                total_duration += leg.get("duration", {}).get("value", 0)

                for step in leg.get("steps", []):
                    instruction = step.get("html_instructions", "").replace("<b>", "").replace("</b>", "")
                    steps.append(
                        RouteStep(
                            instruction=instruction,
                            distance=step.get("distance", {}).get("value", 0),
                            duration=step.get("duration", {}).get("value", 0),
                            maneuver=step.get("maneuver", ""),
                        )
                    )

            return Route(
                distance=total_distance,  # Google uses meters
                duration=total_duration,  # Google uses seconds
                steps=steps,
                polyline=route_data.get("overview_polyline", {}).get("points", ""),
                bounds=route_data.get("bounds", {}),
            )

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e
