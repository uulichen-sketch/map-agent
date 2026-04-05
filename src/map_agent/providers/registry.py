"""Provider registry for managing multiple map providers."""

from typing import Dict, Type, Optional

from .base import MapProvider


class ProviderRegistry:
    """Registry for map providers.

    Singleton class that manages all registered map providers.
    Providers are registered at module import time.

    Usage:
        from map_agent.providers import ProviderRegistry, MyProvider

        # Register a provider
        ProviderRegistry.register("my_provider", MyProvider)

        # Get a provider class
        provider_class = ProviderRegistry.get("my_provider")

        # List all providers
        all_providers = ProviderRegistry.list_providers()
    """

    _providers: Dict[str, Type[MapProvider]] = {}

    @classmethod
    def register(cls, provider_id: str, provider_class: Type[MapProvider]) -> None:
        """Register a map provider.

        Args:
            provider_id: Unique identifier for the provider
            provider_class: Provider class that inherits from MapProvider

        Raises:
            ValueError: If provider_id already registered
        """
        if provider_id in cls._providers:
            raise ValueError(f"Provider '{provider_id}' is already registered")
        cls._providers[provider_id] = provider_class

    @classmethod
    def get(cls, provider_id: str) -> Type[MapProvider]:
        """Get a provider class by ID.

        Args:
            provider_id: Unique identifier of the provider

        Returns:
            Provider class

        Raises:
            ValueError: If provider_id is not registered
        """
        if provider_id not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider '{provider_id}'. "
                f"Available providers: {available}"
            )
        return cls._providers[provider_id]

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """List all registered providers.

        Returns:
            Dictionary mapping provider_id to provider_name
        """
        return {
            pid: cls._providers[pid].provider_name
            for pid in cls._providers
        }

    @classmethod
    def is_registered(cls, provider_id: str) -> bool:
        """Check if a provider is registered.

        Args:
            provider_id: Provider identifier to check

        Returns:
            True if provider is registered, False otherwise
        """
        return provider_id in cls._providers

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers.

        Warning: This removes all providers from the registry.
        Mostly useful for testing.
        """
        cls._providers.clear()
