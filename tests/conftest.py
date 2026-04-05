"""Test fixtures for map-agent providers and tools."""

import pytest
from typing import AsyncMock, Dict, Any

from map_agent.providers.base import POI, Route, RouteStep, GeocodeResult


@pytest.fixture
def sample_poi() -> POI:
    """Sample POI data for testing."""
    return POI(
        name="Test Restaurant",
        address="123 Test Street, Shenzhen, China",
        lat=22.5347,
        lon=114.0533,
        distance=150.5,
        category="restaurant",
        poi_id="test-poi-123",
        phone="+86-1234567890",
        website="https://test.example.com",
        rating=4.5,
    )


@pytest.fixture
def sample_pois() -> list[POI]:
    """Sample list of POIs for testing."""
    return [
        POI(
            name="Restaurant A",
            address="123 Street A",
            lat=22.5347,
            lon=114.0533,
            distance=100,
            category="restaurant",
            poi_id="poi-001",
        ),
        POI(
            name="Coffee Shop B",
            address="456 Street B",
            lat=22.5357,
            lon=114.0543,
            distance=200,
            category="cafe",
            poi_id="poi-002",
        ),
        POI(
            name="Store C",
            address="789 Street C",
            lat=22.5367,
            lon=114.0553,
            distance=300,
            category="shopping",
            poi_id="poi-003",
        ),
    ]


@pytest.fixture
def sample_route() -> Route:
    """Sample route data for testing."""
    return Route(
        distance=5000,  # 5km
        duration=900,  # 15 minutes
        steps=[
            RouteStep(
                instruction="Head north on Main Street",
                distance=500,
                duration=90,
                maneuver="straight",
            ),
            RouteStep(
                instruction="Turn right onto Oak Avenue",
                distance=300,
                duration=60,
                maneuver="turn-right",
            ),
            RouteStep(
                instruction="Arrive at destination",
                distance=0,
                duration=0,
                maneuver="arrive",
            ),
        ],
        polyline="encoded_polyline_string",
        bounds={
            "southwest": {"lat": 22.5200, "lng": 114.0400},
            "northeast": {"lat": 22.5500, "lng": 114.0700},
        },
    )


@pytest.fixture
def sample_geocode_results() -> list[GeocodeResult]:
    """Sample geocoding results for testing."""
    return [
        GeocodeResult(
            lat=22.5431,
            lon=114.0579,
            formatted_address="Shenzhen, Guangdong, China",
            address_components={"country": "China", "province": "Guangdong", "city": "Shenzhen"},
        ),
        GeocodeResult(
            lat=22.5435,
            lon=114.0582,
            formatted_address="Nanshan District, Shenzhen, China",
            address_components={"district": "Nanshan", "city": "Shenzhen", "country": "China"},
        ),
    ]


@pytest.fixture
def mock_http_response():
    """Mock HTTP response helper."""
    async def _mock_response(json_data: Dict[str, Any], status_code: int = 200) -> AsyncMock:
        mock_resp = AsyncMock()
        mock_resp.status_code = status_code
        mock_resp.json = AsyncMock(return_value=json_data)
        mock_resp.raise_for_status = AsyncMock()
        return mock_resp

    return _mock_response


@pytest.fixture
def hms_api_key() -> str:
    """Mock HMS API key for testing."""
    return "test-hms-api-key-12345"


@pytest.fixture
def sample_search_results():
    """Sample HMS API search results."""
    return {
        "returnCode": "0",
        "returnDesc": "OK",
        "totalCount": 3,
        "sites": [
            {
                "siteId": "poi-001",
                "name": "Test Place 1",
                "formatAddress": "123 Test Street",
                "location": {"lat": 22.5347, "lng": 114.0533},
                "distance": 100.5,
                "poi": {"type": "restaurant", "phone": "+86-123", "websiteUrl": "https://test.com", "rating": 4.5},
                "address": {"city": "Shenzhen", "district": "Nanshan"},
            },
            {
                "siteId": "poi-002",
                "name": "Test Place 2",
                "formatAddress": "456 Test Avenue",
                "location": {"lat": 22.5357, "lng": 114.0543},
                "distance": 200.3,
                "poi": {"type": "cafe"},
                "address": {"city": "Shenzhen", "district": "Futian"},
            },
        ],
    }


@pytest.fixture
def sample_geocode_response():
    """Sample HMS geocoding API response."""
    return {
        "returnCode": "0",
        "returnDesc": "OK",
        "sites": [
            {
                "siteId": "geo-001",
                "name": "Shenzhen, China",
                "formatAddress": "Shenzhen, Guangdong, China",
                "location": {"lat": 22.5431, "lng": 114.0579},
                "address": {"country": "China", "province": "Guangdong", "city": "Shenzhen"},
            }
        ],
    }


@pytest.fixture
def sample_route_response():
    """Sample HMS route API response."""
    return {
        "returnCode": "0",
        "returnDesc": "OK",
        "routes": [
            {
                "distance": 5000,
                "duration": 900,
                "bounds": {
                    "southwest": {"lat": 22.5200, "lng": 114.0400},
                    "northeast": {"lat": 22.5500, "lng": 114.0700},
                },
                "polyline": "encoded_polyline",
                "steps": [
                    {
                        "instruction": "Head north on Main Street",
                        "distance": 500,
                        "duration": 90,
                        "action": "straight",
                    },
                    {
                        "instruction": "Turn right",
                        "distance": 300,
                        "duration": 60,
                        "action": "turn-right",
                    },
                ],
            }
        ],
    }


@pytest.fixture
def sample_suggestion_response():
    """Sample HMS query suggestion API response."""
    return {
        "returnCode": "0",
        "returnDesc": "OK",
        "suggestions": [
            {"title": "Shenzhen Bay Park", "text": "Shenzhen Bay Park"},
            {"title": "Shenzhen University", "text": "Shenzhen University"},
            {"title": "Shenzhen Library", "text": "Shenzhen Library"},
        ],
    }
