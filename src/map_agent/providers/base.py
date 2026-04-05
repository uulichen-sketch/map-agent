"""Base classes and interfaces for map providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class POI:
    """Point of Interest.

    Represents a place/location with coordinates and metadata.
    """
    name: str
    address: str
    lat: float
    lon: float
    distance: Optional[float] = None  # Distance in meters
    category: Optional[str] = None
    poi_id: Optional[str] = None  # Provider-specific ID
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None


@dataclass
class RouteStep:
    """Single step in a route.

    Represents one instruction/turn in a route.
    """
    instruction: str
    distance: int  # in meters
    duration: int  # in seconds
    maneuver: Optional[str] = None  # e.g., "turn-left", "uturn"


@dataclass
class Route:
    """Route result.

    Represents a complete route between two points.
    """
    distance: int  # Total distance in meters
    duration: int  # Total duration in seconds
    steps: List[RouteStep]
    polyline: Optional[str] = None  # Encoded polyline
    bounds: Optional[dict] = None  # Bounding box


@dataclass
class GeocodeResult:
    """Geocoding result.

    Result of converting address to coordinates.
    """
    lat: float
    lon: float
    formatted_address: Optional[str] = None
    address_components: Optional[dict] = None


class MapProvider(ABC):
    """Base class for all map providers.

    All map provider implementations must inherit from this class
    and implement all abstract methods.

    Attributes:
        provider_id: Unique identifier for the provider (e.g., "hms", "gaode", "google")
        provider_name: Human-readable name of the provider
    """

    provider_id: str
    provider_name: str

    @abstractmethod
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
        """Search for POIs near a given location.

        Args:
            lat: Latitude of the center point
            lon: Longitude of the center point
            radius: Search radius in meters (typically 1-50000)
            keyword: Optional search keyword to filter results
            category: Optional category filter (provider-specific)
            language: Optional response language code
            page_size: Number of results per page (typically 1-20)
            page_index: Page number (typically 1-60)

        Returns:
            List of POI objects sorted by distance

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
        """
        pass

    @abstractmethod
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
        """Search for POIs by keyword across a region.

        Args:
            keyword: Search query string
            lat: Optional center latitude for biasing results
            lon: Optional center longitude for biasing results
            radius: Optional search radius in meters
            category: Optional category filter (provider-specific)
            language: Optional response language code
            page_size: Number of results per page (typically 1-20)
            page_index: Page number (typically 1-60)

        Returns:
            List of POI objects matching the keyword

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
        """
        pass

    @abstractmethod
    async def get_poi_detail(
        self,
        poi_id: str,
        language: Optional[str] = None,
    ) -> POI:
        """Get detailed information about a POI.

        Args:
            poi_id: Provider-specific POI identifier
            language: Optional response language code

        Returns:
            POI object with complete details

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
            NotFoundError: If POI ID doesn't exist
        """
        pass

    @abstractmethod
    async def search_suggestion(
        self,
        keyword: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[int] = None,
        language: Optional[str] = None,
    ) -> List[str]:
        """Get search query suggestions / autocomplete.

        Args:
            keyword: Partial query string for autocomplete
            lat: Optional center latitude for biasing results
            lon: Optional center longitude for biasing results
            radius: Optional bias radius in meters
            language: Optional response language code

        Returns:
            List of suggested search terms

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
        """
        pass

    @abstractmethod
    async def geocode(
        self,
        address: str,
        language: Optional[str] = None,
    ) -> List[GeocodeResult]:
        """Convert an address to geographic coordinates (forward geocoding).

        Args:
            address: Structured address string
            language: Optional response language code

        Returns:
            List of geocoding results with coordinates

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
        """
        pass

    @abstractmethod
    async def reverse_geocode(
        self,
        lat: float,
        lon: float,
        language: Optional[str] = None,
        radius: Optional[int] = None,
    ) -> dict:
        """Convert geographic coordinates to an address (reverse geocoding).

        Args:
            lat: Latitude
            lon: Longitude
            language: Optional response language code
            radius: Optional search radius in meters

        Returns:
            Address information (format varies by provider)

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
        """
        pass

    @abstractmethod
    async def route(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        mode: str = "driving",
        waypoints: Optional[List[tuple[float, float]]] = None,
        avoid: Optional[List[str]] = None,
        alternatives: bool = False,
        language: Optional[str] = None,
    ) -> Route:
        """Plan a route between two points.

        Args:
            origin_lat: Latitude of origin
            origin_lon: Longitude of origin
            dest_lat: Latitude of destination
            dest_lon: Longitude of destination
            mode: Route mode ("driving", "walking", "cycling", "transit")
            waypoints: Optional list of (lat, lon) waypoints (typically max 5)
            avoid: Optional list of features to avoid (provider-specific)
            alternatives: Whether to return multiple route options
            language: Optional response language code

        Returns:
            Route object with distance, duration, and steps

        Raises:
            NetworkError: On network connectivity issues
            APIError: On provider API errors
            InvalidRouteError: If route cannot be calculated
        """
        pass


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class APIError(ProviderError):
    """Provider API returned an error."""
    def __init__(self, message: str, code: Optional[str] = None):
        self.code = code
        super().__init__(message)


class NetworkError(ProviderError):
    """Network connectivity or timeout issue."""
    pass


class NotFoundError(ProviderError):
    """Requested resource not found."""
    pass


class InvalidRouteError(ProviderError):
    """Route cannot be calculated."""
    pass
