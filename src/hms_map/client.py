from __future__ import annotations

import urllib.parse
from typing import Any

import httpx

from .exceptions import HuaweiAPIError, NetworkError
from .models import (
    BicyclingRouteParams,
    DrivingRouteParams,
    GeocodeParams,
    GeocodeResult,
    KeywordSearchParams,
    NearbySearchParams,
    PlaceDetailParams,
    PlaceDetailResult,
    QuerySuggestionParams,
    ReverseGeocodeParams,
    RouteResult,
    SiteSearchResult,
    SuggestionResult,
    WalkingRouteParams,
)

SITE_BASE = "https://siteapi.cloud.huawei.com/mapApi/v1/siteService"
ROUTE_BASE = "https://mapapi.cloud.huawei.com/mapApi/v1/routeService"


class HMSMapClient:
    """Async HTTP client for Huawei Map Kit REST APIs."""

    def __init__(self, api_key: str, timeout: float = 30.0):
        self._api_key = api_key
        self._encoded_key = urllib.parse.quote(api_key, safe="")
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> HMSMapClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # ---- internal ----

    def _site_url(self, action: str) -> str:
        return f"{SITE_BASE}/{action}?key={self._encoded_key}"

    def _route_url(self, action: str) -> str:
        return f"{ROUTE_BASE}/{action}?key={self._encoded_key}"

    async def _post(self, url: str, body: dict) -> dict:
        try:
            resp = await self._client.post(url, json=body)
            resp.raise_for_status()
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {url}") from e
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP {e.response.status_code}: {url}") from e

        data = resp.json()
        code = data.get("returnCode", "")
        if code and code != "0":
            raise HuaweiAPIError(
                code=code,
                message=data.get("returnDesc", "Unknown error"),
            )
        return data

    # ---- site service ----

    async def search_nearby(self, params: NearbySearchParams) -> SiteSearchResult:
        data = await self._post(self._site_url("nearbySearch"), params.model_dump(exclude_none=True))
        return SiteSearchResult(**data)

    async def search_by_keyword(self, params: KeywordSearchParams) -> SiteSearchResult:
        data = await self._post(self._site_url("textSearch"), params.model_dump(exclude_none=True))
        return SiteSearchResult(**data)

    async def search_by_id(self, params: PlaceDetailParams) -> PlaceDetailResult:
        data = await self._post(self._site_url("searchById"), params.model_dump(exclude_none=True))
        return PlaceDetailResult(**data)

    async def query_suggestion(self, params: QuerySuggestionParams) -> SuggestionResult:
        data = await self._post(self._site_url("querySuggestion"), params.model_dump(exclude_none=True))
        return SuggestionResult(**data)

    async def geocode(self, params: GeocodeParams) -> GeocodeResult:
        data = await self._post(self._site_url("geocode"), params.model_dump(exclude_none=True))
        return GeocodeResult(**data)

    async def reverse_geocode(self, params: ReverseGeocodeParams) -> GeocodeResult:
        data = await self._post(self._site_url("reverseGeocode"), params.model_dump(exclude_none=True))
        return GeocodeResult(**data)

    # ---- route service ----

    async def driving_directions(self, params: DrivingRouteParams) -> RouteResult:
        data = await self._post(self._route_url("driving"), params.model_dump(exclude_none=True))
        return RouteResult(**data)

    async def walking_directions(self, params: WalkingRouteParams) -> RouteResult:
        data = await self._post(self._route_url("walking"), params.model_dump(exclude_none=True))
        return RouteResult(**data)

    async def bicycling_directions(self, params: BicyclingRouteParams) -> RouteResult:
        data = await self._post(self._route_url("bicycling"), params.model_dump(exclude_none=True))
        return RouteResult(**data)
