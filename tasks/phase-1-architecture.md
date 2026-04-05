# Phase 1 Task: Multi-Provider Architecture Design

## Objective
Design and implement a multi-provider abstraction layer for map-agent project.

## Requirements

### 1. MapProvider Interface (Base Class)
Create `src/map_agent/providers/base.py` with:

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class POI:
    """Point of Interest"""
    name: str
    address: str
    lat: float
    lon: float
    distance: Optional[float] = None
    category: Optional[str] = None

@dataclass
class Route:
    """Route result"""
    distance: int  # in meters
    duration: int  # in seconds
    steps: List[dict]
    polyline: Optional[str] = None

class MapProvider(ABC):
    """Base class for all map providers"""

    provider_id: str
    provider_name: str

    @abstractmethod
    async def search_nearby(self, lat: float, lon: float, radius: int, keyword: str) -> List[POI]:
        """Search POIs nearby"""
        pass

    @abstractmethod
    async def search_keyword(self, keyword: str, city: Optional[str] = None) -> List[POI]:
        """Search POIs by keyword"""
        pass

    @abstractmethod
    async def get_poi_detail(self, poi_id: str) -> dict:
        """Get POI details"""
        pass

    @abstractmethod
    async def geocode(self, address: str) -> dict:
        """Convert address to coordinates"""
        pass

    @abstractmethod
    async def reverse_geocode(self, lat: float, lon: float) -> dict:
        """Convert coordinates to address"""
        pass

    @abstractmethod
    async def route(self, origin: tuple, dest: tuple, mode: str = "driving") -> Route:
        """Get route plan (driving/walking/cycling/transit)"""
        pass

    @abstractmethod
    async def search_suggestion(self, keyword: str) -> List[str]:
        """Get search suggestions"""
        pass
```

### 2. Provider Registry
Create `src/map_agent/providers/registry.py`:

```python
from typing import Dict, Type
from .base import MapProvider

class ProviderRegistry:
    """Registry for map providers"""

    _providers: Dict[str, Type[MapProvider]] = {}

    @classmethod
    def register(cls, provider_id: str, provider_class: Type[MapProvider]):
        cls._providers[provider_id] = provider_class

    @classmethod
    def get(cls, provider_id: str) -> Type[MapProvider]:
        if provider_id not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_id}")
        return cls._providers[provider_id]

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        return {pid: cls._providers[pid].provider_name for pid in cls._providers}
```

### 3. HMS Provider Implementation
Refactor existing HMS client to implement MapProvider interface:

```python
# src/map_agent/providers/hms.py
from .base import MapProvider, POI, Route

class HMSProvider(MapProvider):
    provider_id = "hms"
    provider_name = "Huawei Map Kit"

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Import and wrap existing HMS client code

    async def search_nearby(self, lat: float, lon: float, radius: int, keyword: str) -> List[POI]:
        # Implement using existing HMS client
        pass

    # ... implement all other abstract methods
```

### 4. Provider Factory
Create `src/map_agent/providers/factory.py`:

```python
from typing import Optional
from .registry import ProviderRegistry
from .hms import HMSProvider

# Import and register all providers
ProviderRegistry.register("hms", HMSProvider)

def create_provider(provider_id: str, **config) -> MapProvider:
    """Factory method to create provider instances"""
    provider_class = ProviderRegistry.get(provider_id)
    return provider_class(**config)

def get_default_provider() -> str:
    """Get default provider ID (configurable via env)"""
    import os
    return os.getenv("MAP_AGENT_DEFAULT_PROVIDER", "hms")
```

### 5. Update Server to Use Providers
Modify `src/map_agent/server.py` to:
- Support `provider_id` parameter in MCP tools
- Use ProviderFactory to create provider instances
- Default to HMS for backward compatibility

### 6. Configuration
Update `src/map_agent/config.py` to:
- Add provider selection options
- Support provider-specific API keys

## Acceptance Criteria
- [x] MapProvider interface defined with all abstract methods
- [ ] ProviderRegistry implementation with registration mechanism
- [ ] HMS provider refactored to implement MapProvider
- [ ] Provider factory with create_provider() function
- [ ] Server updated to use multi-provider architecture
- [ ] Configuration supports provider selection
- [ ] Backward compatibility maintained (default to HMS)
- [ ] Type hints added throughout
- [ ] Docstrings added to all public methods

## Next Steps
After this task is complete:
1. Implement GaodeProvider (高德地图)
2. Implement GoogleProvider
3. Add unit tests for base classes and HMS provider
4. Update documentation

## Notes
- Keep existing HMS client code, just wrap it in the new interface
- Use async/await throughout for consistency
- Consider using httpx for async HTTP requests
- Error handling should be consistent across providers
