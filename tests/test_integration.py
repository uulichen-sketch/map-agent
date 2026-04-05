"""Integration tests for complete workflows."""

import pytest

from map_agent.providers.factory import create_provider, list_providers, get_default_provider
from map_agent.providers.base import MapProvider


def test_list_all_providers():
    """Test that all providers are listed."""
    providers = list_providers()

    assert "hms" in providers
    assert "gaode" in providers
    assert "google" in providers
    assert providers["hms"] == "Huawei Map Kit"
    assert providers["gaode"] == "Amap (高德地图)"
    assert providers["google"] == "Google Maps Platform"


def test_get_default_provider():
    """Test getting default provider."""
    provider_id = get_default_provider()
    assert provider_id in ["hms", "gaode", "google"]


def test_create_hms_provider():
    """Test creating HMS provider."""
    provider = create_provider("hms", api_key="test-key")
    assert isinstance(provider, MapProvider)
    assert provider.provider_id == "hms"


def test_create_gaode_provider():
    """Test creating Gaode provider."""
    provider = create_provider("gaode", api_key="test-key")
    assert isinstance(provider, MapProvider)
    assert provider.provider_id == "gaode"


def test_create_google_provider():
    """Test creating Google provider."""
    provider = create_provider("google", api_key="test-key")
    assert isinstance(provider, MapProvider)
    assert provider.provider_id == "google"


def test_create_invalid_provider():
    """Test creating invalid provider raises error."""
    with pytest.raises(ValueError) as exc_info:
        create_provider("invalid", api_key="test-key")

    assert "Unknown provider 'invalid'" in str(exc_info.value)


def test_create_hms_provider_missing_api_key():
    """Test creating HMS provider without API key."""
    # HMS provider can be created without API key (will fail at runtime)
    provider = create_provider("hms")
    assert provider.provider_id == "hms"
