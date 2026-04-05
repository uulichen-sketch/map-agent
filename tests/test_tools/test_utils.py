"""Tests for tool functions."""

import pytest
from map_agent.server import _safe_json, _poi_to_dict, _route_to_dict


def test_safe_json_with_dict():
    """Test _safe_json with dict input."""
    class TestModel:
        def model_dump(self, mode, exclude_none):
            return {"key": "value", "number": 123}

    result = _safe_json(TestModel())
    assert result == {"key": "value", "number": 123}


def test_safe_json_with_dict_direct():
    """Test _safe_json with direct dict."""
    result = _safe_json({"direct": "dict"})
    assert result == {"direct": "dict"}


def test_poi_to_dict():
    """Test _poi_to_dict conversion."""
    from map_agent.providers.base import POI

    poi = POI(
        name="Test Place",
        address="123 Test St",
        lat=22.5347,
        lon=114.0533,
        distance=150.5,
        category="restaurant",
        poi_id="poi-123",
        phone="+86-1234567890",
        website="https://test.com",
        rating=4.5,
    )

    result = _poi_to_dict(poi)

    assert result["siteId"] == "poi-123"
    assert result["name"] == "Test Place"
    assert result["formatAddress"] == "123 Test St"
    assert result["location"]["lat"] == 22.5347
    assert result["location"]["lng"] == 114.0533
    assert result["distance"] == 150.5


def test_poi_to_dict_minimal():
    """Test _poi_to_dict with minimal POI."""
    from map_agent.providers.base import POI

    poi = POI(
        name="Minimal Place",
        address="Unknown",
        lat=0.0,
        lon=0.0,
    )

    result = _poi_to_dict(poi)

    assert result["siteId"] is None
    assert result["name"] == "Minimal Place"
    assert result["formatAddress"] == "Unknown"
    assert result["distance"] is None


def test_route_to_dict():
    """Test _route_to_dict conversion."""
    from map_agent.providers.base import Route, RouteStep

    route = Route(
        distance=5000,
        duration=900,
        steps=[
            RouteStep(
                instruction="Step 1",
                distance=500,
                duration=90,
                maneuver="straight",
            ),
            RouteStep(
                instruction="Step 2",
                duration=60,
                maneuver="turn-right",
            ),
        ],
        polyline="encoded_polyline",
        bounds={
            "southwest": {"lat": 22.52, "lng": 114.04},
            "northeast": {"lat": 22.55, "lng": 114.07},
        },
    )

    result = _route_to_dict(route)

    assert result["distance"] == 5000
    assert result["duration"] == 900
    assert result["polyline"] == "encoded_polyline"
    assert result["bounds"] is not None
    assert len(result["steps"]) == 2


def test_route_to_dict_minimal():
    """Test _route_to_dict with minimal route."""
    from map_agent.providers.base import Route

    route = Route(
        distance=100,
        duration=30,
        steps=[],
    )

    result = _route_to_dict(route)

    assert result["distance"] == 100
    assert result["duration"] == 30
    assert len(result["steps"]) == 0
