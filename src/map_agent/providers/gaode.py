"""Amap (Gaode) provider implementation.

Amap is one of the most popular map providers in China.
API docs: https://lbs.amap.com/api/
"""

from typing import Optional, List, Tuple
import httpx

from ..providers.base import MapProvider, POI, Route, RouteStep, GeocodeResult
from ..providers.base import APIError, NetworkError, NotFoundError, InvalidRouteError


class AmapProvider(MapProvider):
    """Amap (Gaode) map provider.

    Uses Amap (高德地图) REST API for all map operations.

    Attributes:
        provider_id: "gaode"
        provider_name: "Amap (高德地图)"
    """

    provider_id = "gaode"
    provider_name = "Amap (高德地图)"

    # Amap API endpoints
    GEO_BASE = "https://restapi.amap.com/v3/geocode/geo"
    RE_GEO_BASE = "https://restapi.amap.com/v3/geocode/regeo"
    POI_SEARCH_BASE = "https://restapi.amap.com/v5/place/around"
    POI_TEXT_BASE = "https://restapi.amap.com/v5/place/text"
    POI_DETAIL_BASE = "https://restapi.amap.com/v5/place/detail"
    ROUTE_BASE = "https://restapi.amap.com/v5/direction/driving"
    WALKING_BASE = "https://restapi.amap.com/v5/direction/walking"
    BICYCLING_BASE = "https://restapi.amap.com/v5/direction/bicycling"
    SUGGESTION_BASE = "https://restapi.amap.com/v3/assistant/inputtips"

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize Amap provider.

        Args:
            api_key: Amap API key (AMAP_API_KEY)
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

    async def __aenter__(self) -> "AmapProvider":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

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
                "location": f"{lon},{lat}",
                "radius": str(radius),
                "offset": str((page_index - 1) * page_size),
                "limit": str(page_size),
            }

            if keyword:
                params["keywords"] = keyword
            if category:
                params["types"] = category

            resp = await client.get(self.POI_SEARCH_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise APIError(f"Amap error: {data.get('info', 'Unknown error')}", code=data.get("status"))

            pois = []
            for item in data.get("pois", []):
                location = item.get("location", {})
                pois.append(
                    POI(
                        name=item.get("name", ""),
                        address=item.get("address", "") or item.get("pname", "") + item.get("pname", ""),
                        lat=float(location.get("lat", 0.0)),
                        lon=float(location.get("lon", 0.0)),
                        distance=item.get("distance"),
                        category=item.get("type"),
                        poi_id=item.get("id"),
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
                "keywords": keyword,
                "offset": str((page_index - 1) * page_size),
                "limit": str(page_size),
            }

            if lat is not None and lon is not None:
                params["location"] = f"{lon},{lat}"
            if radius is not None:
                params["radius"] = str(radius)
            if category:
                params["types"] = category

            resp = await client.get(self.POI_TEXT_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise APIError(f"Amap error: {data.get('info', 'Unknown error')}", code=data.get("status"))

            pois = []
            for item in data.get("pois", []):
                location = item.get("location", {})
                pois.append(
                    POI(
                        name=item.get("name", ""),
                        address=item.get("address", "") or item.get("pname", "") + item.get("pname", ""),
                        lat=float(location.get("lat", 0.0)),
                        lon=float(location.get("lon", 0.0)),
                        distance=item.get("distance"),
                        category=item.get("type"),
                        poi_id=item.get("id"),
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
                "id": poi_id,
            }

            resp = await client.get(self.POI_DETAIL_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise NotFoundError(f"POI not found: {poi_id}")

            pois = data.get("pois", [])
            if not pois:
                raise NotFoundError(f"POI not found: {poi_id}")

            item = pois[0]
            location = item.get("location", {})

            return POI(
                name=item.get("name", ""),
                address=item.get("address", ""),
                lat=float(location.get("lat", 0.0)),
                lon=float(location.get("lon", 0.0)),
                category=item.get("type"),
                poi_id=item.get("id"),
                phone=item.get("tel"),
                website=item.get("website"),
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
                "keywords": keyword,
            }

            if lat is not None and lon is not None:
                params["location"] = f"{lon},{lat}"
            if radius is not None:
                params["radius"] = str(radius)

            resp = await client.get(self.SUGGESTION_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise APIError(f"Amap error: {data.get('info', 'Unknown error')}", code=data.get("status"))

            # Extract suggestions
            return [tip.get("name", "") for tip in data.get("tips", [])]

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

            resp = await client.get(self.GEO_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise APIError(f"Amap error: {data.get('info', 'Unknown error')}", code=data.get("status"))

            geocodes = []
            for item in data.get("geocodes", []):
                location = item.get("location", {})
                geocodes.append(
                    GeocodeResult(
                        lat=float(location.get("lat", 0.0)),
                        lon=float(location.get("lon", 0.0)),
                        formatted_address=item.get("formatted_address", ""),
                        address_components={"country": item.get("country", "")},
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
                "location": f"{lon},{lat}",
            }

            if radius is not None:
                params["radius"] = str(radius)

            resp = await client.get(self.RE_GEO_BASE, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise NotFoundError(f"No address found for coordinates: {lat}, {lon}")

            regeocode = data.get("regeocode", {})
            address_component = regeocode.get("addressComponent", {})

            return {
                "lat": lat,
                "lon": lon,
                "formatted_address": regeocode.get("formatted_address", ""),
                "address_components": {
                    "country": address_component.get("country", ""),
                    "province": address_component.get("province", ""),
                    "city": address_component.get("city", ""),
                    "district": address_component.get("district", ""),
                    "township": address_component.get("township", ""),
                },
                "returnCode": "1",
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

            # Choose base URL based on mode
            if mode == "driving":
                base_url = self.ROUTE_BASE
            elif mode == "walking":
                base_url = self.WALKING_BASE
            elif mode == "cycling":
                base_url = self.BICYCLING_BASE
            else:
                raise InvalidRouteError(f"Unsupported route mode: {mode}")

            params = {
                "key": self._api_key,
                "origin": f"{origin_lon},{origin_lat}",
                "destination": f"{dest_lon},{dest_lat}",
            }

            # Add waypoints if provided
            if waypoints:
                wp_str = ";".join([f"{w[1]},{w[0]}" for w in waypoints])
                params["waypoints"] = wp_str

            # Map avoid options (Amap uses different codes)
            # 0=none, 1=avoid tolls
            if avoid and "toll" in avoid:
                params["avoid"] = "1"

            resp = await client.get(base_url, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data.get("status") != "1":
                raise InvalidRouteError(f"No route found for mode: {mode}")

            routes = data.get("route", {})
            if not routes:
                raise InvalidRouteError(f"No route found for mode: {mode}")

            # Parse route
            path = routes.get("paths", [])
            if not path:
                raise InvalidRouteError(f"No route found for mode: {mode}")

            path = path[0]
            steps_data = path.get("steps", [])

            steps = []
            for step in steps_data:
                steps.append(
                    RouteStep(
                        instruction=step.get("instruction", ""),
                        distance=int(step.get("distance", 0)),
                        duration=int(step.get("duration", 0)),
                        maneuver=step.get("action", ""),
                    )
                )

            return Route(
                distance=int(path.get("distance", 0)),
                duration=int(path.get("duration", 0)),
                steps=steps,
                polyline=path.get("polyline", ""),
                bounds={
                    "southwest": {
                        "lat": float(path.get("bounds", {}).get("southwest", {}).get("lat", 0.0)),
                        "lon": float(path.get("bounds", {}).get("southwest", {}).get("lng", 0.0)),
                    },
                    "northeast": {
                        "lat": float(path.get("bounds", {}).get("northeast", {}).get("lat", 0.0)),
                        "lon": float(path.get("bounds", {}).get("northeast", {}).get("lng", 0.0)),
                    },
                },
            )

        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}") from e
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise NetworkError(str(e)) from e
