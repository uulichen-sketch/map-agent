"""Tests for HMS provider."""

import pytest

from map_agent.providers.hms import HMSProvider
from map_agent.providers.base import APIError, NetworkError


@pytest.mark.asyncio
async def test_hms_provider_creation(hms_api_key):
    """Test creating an HMS provider instance."""
    provider = HMSProvider(api_key=hms_api_key)
    assert provider.provider_id == "hms"
    assert provider.provider_name == "Huawei Map Kit"
    assert provider._api_key == hms_api_key


@pytest.mark.asyncio
async def test_hms_provider_creation_with_timeout(hms_api_key):
    """Test creating HMS provider with custom timeout."""
    provider = HMSProvider(api_key=hms_api_key, timeout=60.0)
    assert provider._timeout == 60.0


@pytest.mark.asyncio
async def test_hms_provider_close(hms_api_key):
    """Test closing HMS provider."""
    provider = HMSProvider(api_key=hms_api_key)

    # Provider should work before close
    client1 = provider._get_client()
    assert client1 is not None

    # Close provider
    await provider.close()

    # Client should be None after close
    assert provider._client is None


@pytest.mark.asyncio
async def test_hms_provider_context_manager(hms_api_key):
    """Test using HMS provider as context manager."""
    async with HMSProvider(api_key=hms_api_key) as provider:
        assert provider._client is not None
        assert provider.provider_id == "hms"

    # Client should be None after exit
    assert provider._client is None


def test_convert_hms_site_to_poi():
    """Test converting HMS site data to POI."""
    from map_agent.providers.hms import HMSProvider

    provider = HMSProvider(api_key="test-key")

    hms_site = {
        "siteId": "poi-001",
        "name": "Test Restaurant",
        "formatAddress": "123 Test Street",
        "location": {"lat": 22.5347, "lng": 114.0533},
        "distance": 100.5,
        "poi": {
            "type": "restaurant",
            "phone": "+86-1234567890",
            "websiteUrl": "https://test.com",
            "rating": 4.5,
        },
    }

    poi = provider._hms_site_to_poi(hms_site)

    assert poi.poi_id == "poi-001"
    assert poi.name == "Test Restaurant"
    assert poi.address == "123 Test Street"
    assert poi.lat == 22.5347
    assert poi.lon == 114.0533
    assert poi.distance == 100.5
    assert poi.category == "restaurant"
    assert poi.phone == "+86-1234567890"
    assert poi.website == "https://test.com"
    assert poi.rating == 4.5


def test_convert_hms_site_to_poi_minimal():
    """Test converting HMS site with minimal data."""
    from map_agent.providers.hms import HMSProvider

    provider = HMSProvider(api_key="test-key")

    hms_site = {
        "siteId": "poi-002",
        "name": "Simple Place",
        "formatAddress": "456 Simple Ave",
        "location": {"lat": 22.5357, "lng": 114.0543},
    }

    poi = provider._hms_site_to_poi(hms_site)

    assert poi.poi_id == "poi-002"
    assert poi.name == "Simple Place"
    assert poi.address == "456 Simple Ave"
    assert poi.lat == 22.5357
    assert poi.lon == 114.0543
    assert poi.distance is None
    assert poi.category is None


def test_convert_hms_route_to_route():
    """Test converting HMS route data to Route."""
    from map_agent.providers.hms import HMSProvider

    provider = HMSProvider(api_key="test-key")

    hms_route = {
        "distance": 5000,
        "duration": 900,
        "polyline": "encoded_polyline",
        "bounds": {
            "southwest": {"lat": 22.52, "lng": 114.04},
            "northeast": {"lat": 22.55, "lng": 114.07},
        },
        "steps": [
            {"instruction": "Go straight", "distance": 500, "duration": 90, "action": "straight"},
            {"instruction": "Turn right", "distance": 300, "duration": 60, "action": "turn-right"},
        ],
    }

    route = provider._hms_route_to_route(hms_route)

    assert route.distance == 5000
    assert route.duration == 900
    assert route.polyline == "encoded_polyline"
    assert route.bounds is not None
    assert len(route.steps) == 2
    assert route.steps[0].instruction == "Go straight"
    assert route.steps[1].instruction == "Turn right"


def test_convert_hms_error_to_api_error():
    """Test converting HMS APIError to provider APIError."""
    from map_agent.providers.hms import HMSProvider
    from map_agent.exceptions import HuaweiAPIError

    provider = HMSProvider(api_key="test-key")

    hms_error = HuaweiAPIError(code="1001", message="Invalid parameter")
    provider_error = provider._convert_hms_error(hms_error)

    assert isinstance(provider_error, APIError)
    assert "API error 1001: Invalid parameter" in str(provider_error)


def test_convert_hms_network_error():
    """Test converting HMS NetworkError to provider NetworkError."""
    from map_agent.providers.hms import HMSProvider
    from map_agent.exceptions import NetworkError as HMSNetworkError

    provider = HMSProvider(api_key="test-key")

    hms_error = HMSNetworkError("Connection timeout")
    provider_error = provider._convert_hms_error(hms_error)

    assert isinstance(provider_error, NetworkError)
    assert "Connection timeout" in str(provider_error)


@pytest.mark.asyncio
async def test_search_nearby_success(hms_api_key, sample_search_results, monkeypatch):
    """Test successful nearby search."""
    from unittest.mock import AsyncMock, patch
    from map_agent.models import SiteSearchResult

    provider = HMSProvider(api_key=hms_api_key)

    # Mock the HTTP client
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_search_results)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        pois = await provider.search_nearby(
            lat=22.5347,
            lon=114.0533,
            radius=1000,
            keyword="restaurant",
        )

        assert len(pois) == 2
        assert pois[0].name == "Test Place 1"
        assert pois[0].distance == 100.5


@pytest.mark.asyncio
async def test_search_nearby_with_category(hms_api_key, sample_search_results, monkeypatch):
    """Test nearby search with category filter."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_search_results)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        pois = await provider.search_nearby(
            lat=22.5347,
            lon=114.0533,
            radius=1000,
            category="restaurant",
        )

        assert len(pois) == 2


@pytest.mark.asyncio
async def test_search_nearby_error(hms_api_key, monkeypatch):
    """Test nearby search with API error."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    # Mock error response
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(
        return_value={"returnCode": "1001", "returnDesc": "Invalid parameter"}
    )
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        with pytest.raises(APIError) as exc_info:
            await provider.search_nearby(
                lat=22.5347,
                lon=114.0533,
                radius=1000,
            )

        assert "Invalid parameter" in str(exc_info.value)


@pytest.mark.asyncio
async def test_keyword_search_success(hms_api_key, sample_search_results, monkeypatch):
    """Test successful keyword search."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_search_results)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        pois = await provider.search_keyword(keyword="restaurant", lat=22.5347, lon=114.0533)

        assert len(pois) == 2


@pytest.mark.asyncio
async def test_poi_detail_success(hms_api_key, sample_search_results, monkeypatch):
    """Test getting POI detail."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    # Mock detail response
    detail_response = {
        "returnCode": "0",
        "returnDesc": "OK",
        "site": sample_search_results["sites"][0],
    }

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=detail_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        poi = await provider.get_poi_detail(poi_id="poi-001")

        assert poi.poi_id == "poi-001"
        assert poi.name == "Test Place 1"


@pytest.mark.asyncio
async def test_poi_detail_not_found(hms_api_key, monkeypatch):
    """Test getting POI detail with non-existent ID."""
    from unittest.mock import AsyncMock, patch
    from map_agent.providers.base import NotFoundError

    provider = HMSProvider(api_key=hms_api_key)

    # Mock error response
    detail_response = {
        "returnCode": "404",
        "returnDesc": "POI not found",
        "site": None,
    }

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=detail_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        with pytest.raises(NotFoundError):
            await provider.get_poi_detail(poi_id="nonexistent")


@pytest.mark.asyncio
async def test_geocode_success(hms_api_key, sample_geocode_response, monkeypatch):
    """Test successful geocoding."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_geocode_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        results = await provider.geocode(address="Shenzhen, China")

        assert len(results) == 1
        assert results[0].formatted_address == "Shenzhen, Guangdong, China"
        assert results[0].lat == 22.5431
        assert results[0].lon == 114.0579


@pytest.mark.asyncio
async def test_reverse_geocode_success(hms_api_key, monkeypatch):
    """Test successful reverse geocoding."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    # Mock reverse geocode response
    reverse_response = {
        "returnCode": "0",
        "returnDesc": "OK",
        "sites": [
            {
                "siteId": "geo-001",
                "name": "Shenzhen, China",
                "formatAddress": "Nanshan District, Shenzhen, China",
                "location": {"lat": 22.5431, "lng": 114.0579},
            }
        ],
    }

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=reverse_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        result = await provider.reverse_geocode(lat=22.5431, lon=114.0579)

        assert result["returnCode"] == "0"
        assert "Nanshan District" in result["formatted_address"]


@pytest.mark.asyncio
async def test_route_driving_success(hms_api_key, sample_route_response, monkeypatch):
    """Test successful driving route planning."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_route_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        route = await provider.route(
            origin_lat=22.52,
            origin_lon=114.04,
            dest_lat=22.55,
            dest_lon=114.07,
            mode="driving",
        )

        assert route.distance == 5000
        assert route.duration == 900
        assert len(route.steps) == 2


@pytest.mark.asyncio
async def test_route_walking_success(hms_api_key, sample_route_response, monkeypatch):
    """Test successful walking route planning."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_route_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        route = await provider.route(
            origin_lat=22.52,
            origin_lon=114.04,
            dest_lat=22.55,
            dest_lon=114.07,
            mode="walking",
        )

        assert route.distance == 5000
        assert route.duration == 900


@pytest.mark.asyncio
async def test_route_cycling_success(hms_api_key, sample_route_response, monkeypatch):
    """Test successful bicycling route planning."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_route_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        route = await provider.route(
            origin_lat=22.52,
            origin_lon=114.04,
            dest_lat=22.55,
            dest_lon=114.07,
            mode="cycling",
        )

        assert route.distance == 5000
        assert route.duration == 900


@pytest.mark.asyncio
async def test_route_with_waypoints(hms_api_key, sample_route_response, monkeypatch):
    """Test route planning with waypoints."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_route_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        route = await provider.route(
            origin_lat=22.52,
            origin_lon=114.04,
            dest_lat=22.55,
            dest_lon=114.07,
            mode="driving",
            waypoints=[(22.53, 114.05), (22.54, 114.06)],
        )

        assert route.distance == 5000


@pytest.mark.asyncio
async def test_search_suggestion_success(hms_api_key, sample_suggestion_response, monkeypatch):
    """Test successful query suggestion."""
    from unittest.mock import AsyncMock, patch

    provider = HMSProvider(api_key=hms_api_key)

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value=sample_suggestion_response)
    mock_response.raise_for_status = AsyncMock()

    async def mock_post(url, body):
        return mock_response

    with patch.object(provider._get_client(), '_post', side_effect=mock_post):
        suggestions = await provider.search_suggestion(keyword="Shen", lat=22.5347, lon=114.0533)

        assert len(suggestions) == 3
        assert "Shenzhen Bay Park" in suggestions
