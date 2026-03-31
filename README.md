# hms-map

A [Model Context Protocol](https://modelcontextprotocol.io) server and CLI tool for [Huawei Map Kit](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/map-introduction-V5). Provides place search, geocoding, reverse geocoding, and route planning (driving, walking, bicycling) through Huawei HMS Core Map Kit REST APIs.

## Features

- **9 MCP Tools** — nearby search, keyword search, place details, query suggestions, geocode, reverse geocode, driving/walking/bicycling route planning
- **Dual Interface** — works as both an MCP server (for AI assistants) and a standalone CLI tool
- **Async** — built on `httpx` + `asyncio` for non-blocking I/O
- **Type Safe** — full Pydantic v2 models for all request/response data

## Prerequisites

A Huawei Map Kit API key is required. Obtain one from [AppGallery Connect](https://developer.huawei.com/consumer/cn/service/josp/agc/index.html).

Set it via environment variable:

```bash
export HUAWEI_MAP_API_KEY="your-api-key-here"
```

## MCP Server Setup

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hms-map": {
      "command": "hms-map-mcp",
      "env": {
        "HUAWEI_MAP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Or use `uvx` (no local install needed):

```json
{
  "mcpServers": {
    "hms-map": {
      "command": "uvx",
      "args": ["hms-map-mcp"],
      "env": {
        "HUAWEI_MAP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### VS Code / Cursor

Add to your `.vscode/mcp.json` (or project `.mcp.json`):

```json
{
  "servers": {
    "hms-map": {
      "command": "hms-map-mcp",
      "env": {
        "HUAWEI_MAP_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_nearby` | Search for places near a location |
| `search_keyword` | Search for places by keyword across a region |
| `place_detail` | Get detailed information about a place by site ID |
| `query_suggestion` | Get search query suggestions / autocomplete |
| `geocode` | Convert an address to geographic coordinates |
| `reverse_geocode` | Convert coordinates to an address |
| `driving_route` | Plan a driving route between two points |
| `walking_route` | Plan a walking route between two points |
| `bicycling_route` | Plan a bicycling route between two points |

### Tool Parameters

**search_nearby** — `lng`, `lat`, `query?`, `radius?` (default 1000), `hwPoiType?`, `language?`, `pageSize?`, `pageIndex?`

**search_keyword** — `query`, `lng?`, `lat?`, `radius?`, `hwPoiType?`, `language?`, `pageSize?`, `pageIndex?`

**place_detail** — `siteId`, `language?`

**query_suggestion** — `query`, `lng?`, `lat?`, `radius?`, `language?`

**geocode** — `address`, `language?`

**reverse_geocode** — `lng`, `lat`, `language?`, `radius?`

**driving_route** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `waypoints?`, `avoid?` (1=tolls, 2=highways), `alternatives?`, `language?`

**walking_route** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `language?`

**bicycling_route** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `avoid?` (8=ferries), `language?`

## CLI Usage

Install:

```bash
pip install hms-map
```

Global options: `--api-key KEY` (or `HUAWEI_MAP_API_KEY` env), `--format json|text`

```bash
# Nearby search
hms-map nearby --lng 116.397 --lat 39.908 --query "coffee" --radius 2000

# Keyword search
hms-map keyword "restaurants" --lng 121.473 --lat 31.230

# Place detail
hms-map detail SITE_ID

# Query suggestions
hms-map suggest "starbucks" --lng 121.473 --lat 31.230

# Geocode
hms-map geocode "北京市天安门广场"

# Reverse geocode
hms-map reverse-geocode --lng 116.397 --lat 39.909

# Route planning
hms-map route --origin "116.397,39.908" --dest "121.473,31.230" --mode driving
hms-map route --origin "116.397,39.908" --dest "121.473,31.230" --mode walking
hms-map route --origin "116.397,39.908" --dest "121.473,31.230" --mode bicycling
```

## Development

```bash
git clone https://github.com/uulichen-sketch/hms-map.git
cd hms-map
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## License

[MIT](LICENSE)
