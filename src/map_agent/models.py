from __future__ import annotations

from pydantic import BaseModel, Field


# --- Shared ---

class Coordinate(BaseModel):
    lng: float = Field(description="Longitude")
    lat: float = Field(description="Latitude")


# --- Site Service request models ---

class NearbySearchParams(BaseModel):
    location: Coordinate = Field(description="Center location")
    radius: int | None = Field(default=1000, ge=1, le=50000, description="Search radius in meters")
    query: str | None = Field(default=None, max_length=512, description="Search keyword")
    hwPoiType: str | None = Field(default=None, description="Huawei POI type filter")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    pageSize: int | None = Field(default=20, ge=1, le=20, description="Results per page")
    pageIndex: int | None = Field(default=1, ge=1, le=60, description="Page number")


class KeywordSearchParams(BaseModel):
    query: str = Field(description="Search keyword")
    location: Coordinate | None = Field(default=None, description="Search center point")
    radius: int | None = Field(default=None, ge=1, le=50000, description="Search radius in meters")
    hwPoiType: str | None = Field(default=None, description="Huawei POI type filter")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    pageSize: int | None = Field(default=20, ge=1, le=20, description="Results per page")
    pageIndex: int | None = Field(default=1, ge=1, le=60, description="Page number")


class PlaceDetailParams(BaseModel):
    siteId: str = Field(description="Place ID")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    children: bool | None = Field(default=False, description="Return child nodes")


class QuerySuggestionParams(BaseModel):
    query: str = Field(description="Partial query string for autocomplete")
    location: Coordinate | None = Field(default=None, description="Bias location")
    radius: int | None = Field(default=None, description="Bias radius in meters")
    language: str | None = Field(default=None, max_length=16, description="Response language")


class GeocodeParams(BaseModel):
    address: str = Field(description="Address to geocode")
    language: str | None = Field(default=None, max_length=16, description="Response language")


class ReverseGeocodeParams(BaseModel):
    location: Coordinate = Field(description="Coordinates to reverse geocode")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    radius: int | None = Field(default=None, description="Search radius in meters")


# --- Route Service request models ---

class DrivingRouteParams(BaseModel):
    origin: Coordinate = Field(description="Route origin")
    destination: Coordinate = Field(description="Route destination")
    waypoints: list[Coordinate] | None = Field(default=None, description="Up to 5 waypoints")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    alternatives: bool | None = Field(default=False, description="Return multiple routes")
    avoid: list[int] | None = Field(default=None, description="Avoid: 1=toll, 2=highway")
    departAt: int | None = Field(default=None, description="Departure timestamp (UTC seconds)")


class WalkingRouteParams(BaseModel):
    origin: Coordinate = Field(description="Route origin")
    destination: Coordinate = Field(description="Route destination")
    language: str | None = Field(default=None, max_length=16, description="Response language")


class BicyclingRouteParams(BaseModel):
    origin: Coordinate = Field(description="Route origin")
    destination: Coordinate = Field(description="Route destination")
    language: str | None = Field(default=None, max_length=16, description="Response language")
    avoid: list[int] | None = Field(default=None, description="Avoid: 8=ferry")


# --- Response models ---

class Site(BaseModel):
    siteId: str | None = None
    name: str | None = None
    formatAddress: str | None = None
    location: Coordinate | None = None
    distance: float | None = None
    poi: dict | None = None
    address: dict | None = None
    viewport: dict | None = None


class SiteSearchResult(BaseModel):
    returnCode: str
    returnDesc: str | None = None
    totalCount: int | None = None
    sites: list[Site] = Field(default_factory=list)


class PlaceDetailResult(BaseModel):
    returnCode: str
    returnDesc: str | None = None
    site: Site | None = None


class GeocodeResult(BaseModel):
    returnCode: str
    returnDesc: str | None = None
    sites: list[Site] = Field(default_factory=list)


class SuggestionResult(BaseModel):
    returnCode: str
    returnDesc: str | None = None
    suggestions: list[dict] = Field(default_factory=list)


class RouteResult(BaseModel):
    returnCode: str
    returnDesc: str | None = None
    routes: list[dict] = Field(default_factory=list)
