"""Tests for provider base classes."""

import pytest

from map_agent.providers.base import MapProvider, POI, Route, RouteStep, GeocodeResult


def test_poi_creation():
    """Test creating a POI object."""
    poi = POI(
        name="Test Restaurant",
        address="123 Test Street",
        lat=22.5347,
        lon=114.0533,
        distance=150.5,
        category="restaurant",
        poi_id="test-123",
        phone="+86-1234567890",
        website="https://test.com",
        rating=4.5,
    )

    assert poi.name == "Test Restaurant"
    assert poi.address == "123 Test Street"
    assert poi.lat == 22.5347
    assert poi.lon == 114.0533
    assert poi.distance == 150.5
    assert poi.category == "restaurant"
    assert poi.poi_id == "test-123"
    assert poi.phone == "+86-1234567890"
    assert poi.website == "https://test.com"
    assert poi.rating == 4.5


def test_poi_minimal():
    """Test creating a POI with minimal fields."""
    poi = POI(
        name="Minimal POI",
        address="Unknown",
        lat=0.0,
        lon=0.0,
    )

    assert poi.name == "Minimal POI"
    assert poi.distance is None
    assert poi.category is None
    assert poi.poi_id is None


def test_route_step_creation():
    """Test creating a route step."""
    step = RouteStep(
        instruction="Turn right",
        distance=100,
        duration=20,
        maneuver="turn-right",
    )

    assert step.instruction == "Turn right"
    assert step.distance == 100
    assert step.duration == 20
    assert step.maneuver == "turn-right"


def test_route_creation():
    """Test creating a route object."""
    route = Route(
        distance=5000,
        duration=900,
        steps=[
            RouteStep(instruction="Step 1", distance=100, duration=20),
            RouteStep(instruction="Step 2", distance=200, duration=40),
        ],
        polyline="encoded_polyline",
        bounds={"southwest": {"lat": 22.5, "lng": 114.0}},
    )

    assert route.distance == 5000
    assert route.duration == 900
    assert len(route.steps) == 2
    assert route.polyline == "encoded_polyline"
    assert route.bounds is not None


def test_geocode_result_creation():
    """Test creating a geocoding result."""
    result = GeocodeResult(
        lat=22.5431,
        lon=114.0579,
        formatted_address="Shenzhen, China",
        address_components={"country": "China", "city": "Shenzhen"},
    )

    assert result.lat == 22.5431
    assert result.lon == 114.0579
    assert result.formatted_address == "Shenzhen, China"
    assert result.address_components is not None


def test_map_provider_is_abstract():
    """Test that MapProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        MapProvider()
