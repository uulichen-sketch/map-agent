# Phase 1 Task: Test Suite for Existing Functionality

## Objective
Write comprehensive test suite for existing HMS map functionality before major refactoring.

## Scope
Test all 9 existing MCP tools:
1. search_nearby - Search POIs nearby
2. search_keyword - Search POIs by keyword
3. get_poi_detail - Get POI details
4. search_suggestion - Get search suggestions
5. geocode - Address to coordinates
6. reverse_geocode - Coordinates to address
7. route_driving - Driving route planning
8. route_walking - Walking route planning
9. route_cycling - Cycling route planning

## Requirements

### 1. Test Structure
Create test files:

```
tests/
├── conftest.py (fixtures and setup)
├── test_providers/
│   ├── __init__.py
│   ├── test_base.py (test base interface)
│   └── test_hms.py (test HMS provider)
├── test_tools/
│   ├── __init__.py
│   ├── test_search.py
│   ├── test_geocode.py
│   └── test_route.py
└── test_transports/
    ├── __init__.py
    ├── test_stdio.py
    └── test_sse.py
```

### 2. Fixtures (conftest.py)

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from map_agent.providers.factory import create_provider
from map_agent.config import Config

@pytest.fixture
def mock_hms_api_key():
    """Mock HMS API key for testing"""
    return "test-api-key-123"

@pytest.fixture
def hms_provider(mock_hms_api_key):
    """HMS provider instance for testing"""
    return create_provider("hms", api_key=mock_hms_api_key)

@pytest.fixture
def mock_http_response():
    """Mock HTTP response helper"""
    async def _mock_response(json_data, status_code=200):
        mock_resp = AsyncMock()
        mock_resp.status_code = status_code
        mock_resp.json = AsyncMock(return_value=json_data)
        return mock_resp
    return _mock_response

@pytest.fixture
def sample_poi_data():
    """Sample POI data for testing"""
    return {
        "name": "Test Restaurant",
        "address": "123 Test St",
        "location": {"lat": 22.5347, "lng": 114.0533},
        "distance": 100,
        "poiId": "test-123"
    }

@pytest.fixture
def sample_route_data():
    """Sample route data for testing"""
    return {
        "distance": 5000,
        "duration": 600,
        "steps": [],
        "polyline": "encoded_string"
    }
```

### 3. Test Coverage Goals

#### Provider Tests (test_providers/test_hms.py)
- [x] Test provider initialization
- [ ] Test search_nearby with valid parameters
- [ ] Test search_nearby with invalid coordinates
- [ ] Test search_keyword with and without city
- [ ] Test get_poi_detail with valid POI ID
- [ ] Test get_poi_detail with invalid POI ID
- [ ] Test geocode with valid address
- [ ] Test geocode with invalid address
- [ ] Test reverse_geocode with valid coordinates
- [ ] Test reverse_geocode with invalid coordinates
- [ ] Test route_driving with valid origin/destination
- [ ] Test route_walking with valid origin/destination
- [ ] Test route_cycling with valid origin/destination
- [ ] Test route with invalid mode
- [ ] Test search_suggestion with valid keyword
- [ ] Test error handling (network errors, API errors)

#### Tool Tests (test_tools/)
- [ ] Test MCP tool registration
- [ ] Test tool parameter validation
- [ ] Test tool response formatting
- [ ] Test tool error handling

#### Transport Tests (test_transports/)
- [ ] Test stdio transport initialization
- [ ] Test SSE transport initialization
- [ ] Test streamable-http transport initialization

### 4. Mocking Strategy

```python
# Mock HTTP client to avoid real API calls
@pytest.mark.asyncio
async def test_search_nearby_success(hms_provider, sample_poi_data):
    """Test successful POI search"""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = await mock_http_response({
            "pois": [sample_poi_data]
        })

        pois = await hms_provider.search_nearby(22.5347, 114.0533, 1000, "restaurant")

        assert len(pois) == 1
        assert pois[0].name == "Test Restaurant"
        assert pois[0].address == "123 Test St"
```

### 5. Integration Tests

```python
# Test end-to-end workflow
@pytest.mark.asyncio
async def test_full_search_workflow(hms_provider, sample_poi_data):
    """Test complete search flow: keyword -> detail -> geocode"""
    # 1. Search by keyword
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = await mock_http_response({
            "pois": [sample_poi_data]
        })
        pois = await hms_provider.search_keyword("restaurant", "Shenzhen")

    assert len(pois) > 0

    # 2. Get POI detail
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = await mock_http_response({
            "poi": sample_poi_data
        })
        detail = await hms_provider.get_poi_detail(pois[0].poi_id)

    assert detail["name"] == "Test Restaurant"

    # 3. Geocode the address
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = await mock_http_response({
            "location": {"lat": 22.5347, "lng": 114.0533}
        })
        coords = await hms_provider.geocode("123 Test St")

    assert coords["lat"] == 22.5347
    assert coords["lon"] == 114.0533
```

### 6. Update pyproject.toml

```toml
[project.optional-dependencies]
test = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.0",
    "respx>=0.22",  # HTTP mocking
    "httpx-mock>=0.1.5",  # Alternative HTTP mocking
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --cov=map_agent --cov-report=html --cov-report=term-missing"

[tool.coverage.run]
source = ["src/map_agent"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Acceptance Criteria
- [ ] All 9 existing tools have test coverage
- [ ] Provider base class tests implemented
- [ ] HMS provider tests with 80%+ coverage
- [ ] Mocking strategy defined and working
- [ ] Integration tests for common workflows
- [ ] Transport tests for stdio (SSE tests come after implementation)
- [ ] CI/CD ready (pytest configuration)
- [ ] Test documentation (README in tests/)
- [ ] Fixtures properly configured
- [ ] Error cases tested
- [ ] Type checking with mypy (optional)

## Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=map_agent --cov-report=html

# Run specific test file
pytest tests/test_providers/test_hms.py

# Run async tests
pytest tests/test_providers/test_hms.py -v

# Show coverage report
open htmlcov/index.html
```

## Next Steps
- Run tests and ensure all pass
- Review coverage and add missing tests
- Document test strategy in README
- Prepare for multi-provider refactoring

## Notes
- Use httpx mocking to avoid real API calls
- Keep tests fast (< 5 seconds total)
- Use pytest-asyncio for async test support
- Add property-based testing if time permits (hypothesis)
- Document any limitations or untestable scenarios
