"""Factory for creating provider instances."""

import os
from typing import Optional

from .base import MapProvider
from .registry import ProviderRegistry


def create_provider(
    provider_id: str,
    **config,
) -> MapProvider:
    """Factory method to create provider instances.

    Args:
        provider_id: Unique identifier of the provider (e.g., "hms", "gaode")
        **config: Provider-specific configuration options

    Returns:
        Instantiated provider object

    Raises:
        ValueError: If provider_id is not registered
    """
    provider_class = ProviderRegistry.get(provider_id)
    return provider_class(**config)


def get_default_provider() -> str:
    """Get the default provider ID.

    The default provider can be configured via environment variable.
    Falls back to "hms" if not configured.

    Returns:
        Provider ID string
    """
    return os.getenv("MAP_AGENT_DEFAULT_PROVIDER", "hms")


def get_provider_config(provider_id: str) -> dict:
    """Get configuration for a specific provider.

    Configuration is loaded from environment variables.
    Each provider has its own environment variable pattern.

    Examples:
        HMS: HUAWEI_MAP_API_KEY
        Gaode: AMAP_API_KEY
        Google: GOOGLE_MAPS_API_KEY

    Args:
        provider_id: Provider identifier

    Returns:
        Dictionary of configuration options

    Raises:
        ValueError: If required config is missing
    """
    config = {}

    if provider_id == "hms":
        api_key = os.getenv("HUAWEI_MAP_API_KEY")
        if not api_key:
            raise ValueError(
                "HUAWEI_MAP_API_KEY environment variable is not set. "
                "Get your API key from AppGallery Connect."
            )
        config["api_key"] = api_key

    elif provider_id == "gaode":
        api_key = os.getenv("AMAP_API_KEY")
        if not api_key:
            raise ValueError(
                "AMAP_API_KEY environment variable is not set. "
                "Get your API key from Amap (Gaode) developer console."
            )
        config["api_key"] = api_key

    elif provider_id == "google":
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_MAPS_API_KEY environment variable is not set. "
                "Get your API key from Google Cloud Console."
            )
        config["api_key"] = api_key

    else:
        raise ValueError(f"No configuration defined for provider: {provider_id}")

    return config


def list_providers() -> dict:
    """List all registered providers.

    Returns:
        Dictionary mapping provider_id to provider_name
    """
    from .registry import ProviderRegistry
    return ProviderRegistry.list_providers()
