# Map Agent

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-compatible-orange.svg)](https://modelcontextprotocol.io)

A **multi-provider Map MCP Server** (Huawei/Gaode/Google) with SSE/streamable-http transport support.

**多 Provider 地图 MCP 服务器**，支持华为/高德/谷歌地图，提供 SSE/streamable-http 传输。

## English Features / 中文特性

- **Multi-Provider Support** — HMS (Huawei), Gaode (高德), Google Maps Platform
  - **多 Provider 支持** — 华为、高德、谷歌地图
- **12 MCP Tools** — POI search, geocoding, route planning (driving/walking/cycling/transit)
  - **12 个 MCP 工具** — POI 搜索、地理编码、路径规划（驾驶/步行/骑行/公交）
- **3 Transport Modes** — stdio (default), SSE, streamable-http
  - **3 种传输模式** — stdio (默认), SSE, streamable-http
- **Async & Type-Safe** — Built on `httpx` + `asyncio`, full Pydantic v2 models
  - **异步 & 类型安全** — 基于 `httpx` + `asyncio`，完整的 Pydantic v2 模型
- **Additional Tools** — Distance measurement (straight/route), IP geolocation
  - **扩展工具** — 距离测量（直线/路线）、IP 地理定位

## Quick Start / 快速开始

### Installation / 安装

```bash
pip install map-agent
```

### Prerequisites / 前置要求

You need an API key from one of the providers: / 需要以下任一地图服务的 API Key:

| Provider / 服务商 | Environment Variable / 环境变量 | Get API Key / 获取方式 |
|------------------|-------------------------------------|------------------------|
| HMS (Huawei) / 华为 | `HUAWEI_MAP_API_KEY` | [AppGallery Connect](https://developer.huawei.com/consumer/cn/service/josp/agc/index.html) |
| Gaode (高德) / 高德 | `AMAP_API_KEY` | [Amap Console](https://console.amap.com/dev/key/app) |
| Google Maps / 谷歌 | `GOOGLE_MAPS_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/apis/library) |

Set the API key: / 设置 API Key：

```bash
# For HMS / 华为地图
export HUAWEI_MAP_API_KEY="your-hms-key"

# For Gaode / 高德地图
export AMAP_API_KEY="your-gaode-key"

# For Google Maps / 谷歌地图
export GOOGLE_MAPS_API_KEY="your-google-key"

# Set default provider (optional, defaults to 'hms') / 设置默认 provider（可选，默认 'hms'）
export MAP_AGENT_DEFAULT_PROVIDER="hms"  # or 'gaode', 'google'
```

### MCP Server Configuration / MCP 服务器配置

#### Claude Desktop / Claude Desktop

Add to `claude_desktop_config.json`: / 添加到 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "map-agent": {
      "command": "map-agent-mcp",
      "env": {
        "MAP_AGENT_DEFAULT_PROVIDER": "hms",
        "HUAWEI_MAP_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### VS Code / Cursor

Add to `.vscode/mcp.json`: / 添加到 `.vscode/mcp.json`：

```json
{
  "servers": {
    "map-agent": {
      "command": "map-agent-mcp",
      "env": {
        "MAP_AGENT_DEFAULT_PROVIDER": "hms",
        "HUAWEI_MAP_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### SSE / Streamable-HTTP Transport

For web clients or custom integrations: / 适用于 Web 客户端或自定义集成：

```bash
# SSE transport / SSE 传输
map-agent serve --transport sse --host 0.0.0.0 --port 8000

# Streamable-HTTP transport
map-agent serve --transport streamable-http --host 0.0.0.0 --port 8001

# Use Gaode provider / 使用高德地图
export MAP_AGENT_DEFAULT_PROVIDER=gaode
export AMAP_API_KEY=your-gaode-key
map-agent serve --transport sse

# Use Google provider / 使用谷歌地图
export MAP_AGENT_DEFAULT_PROVIDER=google
export GOOGLE_MAPS_API_KEY=your-google-key
map-agent serve --transport sse
```

## MCP Tools / MCP 工具

| Tool / 工具 | Description / 描述 |
|---------------|---------------------|
| `search_nearby` | Search for places near a location / 搜索附近地点 |
| `search_keyword` | Search for places by keyword / 按关键词搜索地点 |
| `place_detail` | Get detailed information about a place / 获取地点详情 |
| `query_suggestion` | Get search query suggestions / 获取搜索建议 |
| `geocode` | Convert address to coordinates / 地址转坐标 |
| `reverse_geocode` | Convert coordinates to address / 坐标转地址 |
| `driving_route` | Plan a driving route / 规划驾车路线 |
| `walking_route` | Plan a walking route / 规划步行路线 |
| `bicycling_route` | Plan a bicycling route / 规划骑行路线 |
| `transit_route` | Plan a public transit route (bus/metro) / 规划公交路线 |
| `measure_distance` | Measure distance between points / 测量点间距离 |
| `ip_geolocate` | Get geolocation from IP address / IP 地理定位 |

### Tool Parameters / 工具参数

#### Search Tools / 搜索工具

**`search_nearby`** — `lng`, `lat`, `query?`, `radius?` (default 1000), `category?`, `language?`, `pageSize?`, `pageIndex?`

**`search_keyword`** — `query`, `lng?`, `lat?`, `radius?`, `category?`, `language?`, `pageSize?`, `pageIndex?`

**`place_detail`** — `poi_id`, `language?`

**`query_suggestion`** — `query`, `lng?`, `lat?`, `radius?`, `language?`

#### Geocoding Tools / 地理编码工具

**`geocode`** — `address`, `language?`

**`reverse_geocode`** — `lng`, `lat`, `language?`, `radius?`

#### Route Planning Tools / 路径规划工具

**`driving_route`** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `waypoints?`, `avoid?` ("toll", "highway", "ferry"), `alternatives?`, `language?`

**`walking_route`** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `language?`

**`bicycling_route`** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `avoid?`, `language?`

**`transit_route`** — `origin_lng`, `origin_lat`, `dest_lng`, `dest_lat`, `language?` (Google only / 仅 Google 支持)

#### Utility Tools / 实用工具

**`measure_distance`** — `points` (list of {lat, lng}), `mode?` ("straight" | "route")

**`ip_geolocate`** — `ip_address?` (optional / 可选，默认使用客户端 IP)

## CLI Usage / 命令行使用

```bash
# Nearby search / 附近搜索
map-agent nearby --lng 114.0533 --lat 22.5347 --query "coffee" --radius 2000

# Keyword search / 关键词搜索
map-agent keyword "restaurants" --lng 114.0533 --lat 22.5347

# Place detail / 地点详情
map-agent detail --poi-id "poi-123"

# Query suggestions / 搜索建议
map-agent suggest "starbucks" --lng 114.0533 --lat 22.5347

# Geocode / 地址转坐标
map-agent geocode --address "Shenzhen, China"

# Reverse geocode / 坐标转地址
map-agent reverse-geocode --lng 114.0533 --lat 22.5347

# Route planning / 路径规划
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode driving
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode walking
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode bicycling
```

## Provider Comparison / Provider 对比

| Feature / 特性 | HMS (华为) | Gaode (高德) | Google (谷歌) |
|----------------|-------------|---------------|----------------|
| POI Search / POI 搜索 | ✅ | ✅ | ✅ |
| Geocoding / 地理编码 | ✅ | ✅ | ✅ |
| Route Planning / 路径规划 | ✅ | ✅ | ✅ |
| Transit Mode / 公交模式 | ❌ | ❌ | ✅ |
| Regions / 覆盖区域 | Global / 全球 | China / 中国 | Global / 全球 |
| Language Support / 语言支持 | CN/EN | CN/EN | 70+ languages |

## Development / 开发

```bash
# Clone repository / 克隆仓库
git clone https://github.com/uulichen-sketch/map-agent.git
cd map-agent

# Create virtual environment / 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install in development mode / 开发模式安装
pip install -e ".[dev]"

# Run tests / 运行测试
pytest

# Run tests with coverage / 带覆盖率运行测试
pytest --cov=map_agent --cov-report=html
```

## Architecture / 架构

```
map-agent/
├── src/map_agent/
│   ├── providers/          # Multi-provider implementations / 多 Provider 实现
│   │   ├── base.py      # MapProvider abstract base / MapProvider 抽象基类
│   │   ├── hms.py       # HMS (Huawei) provider / 华为 Provider
│   │   ├── gaode.py     # Amap (Gaode) provider / 高德 Provider
│   │   ├── google.py    # Google Maps provider / 谷歌 Provider
│   │   ├── registry.py   # Provider registry / Provider 注册表
│   │   └── factory.py   # Provider factory / Provider 工厂
│   ├── transports/         # Transport implementations / 传输实现
│   │   ├── sse.py         # SSE transport / SSE 传输
│   │   └── streamable_http.py  # Streamable-HTTP / Streamable-HTTP 传输
│   ├── server.py           # MCP server / MCP 服务器
│   ├── client.py          # HTTP client / HTTP 客户端
│   ├── models.py          # Pydantic models / Pydantic 模型
│   └── cli.py            # CLI interface / 命令行接口
└── tests/                 # Test suite / 测试套件
    ├── conftest.py        # Test fixtures / 测试 fixtures
    └── test_providers/    # Provider tests / Provider 测试
```

## Contributing / 贡献

Contributions are welcome! / 欢迎贡献！

1. Fork the repository / Fork 仓库
2. Create a feature branch / 创建功能分支: `git checkout -b my-new-feature`
3. Make your changes / 进行修改
4. Run tests / 运行测试: `pytest`
5. Commit your changes / 提交修改: `git commit -am 'Add some feature'`
6. Push to the branch / 推送到分支: `git push origin my-new-feature`
7. Open a Pull Request / 提交 PR

## License / 许可证

[MIT](LICENSE)

## Acknowledgments / 致谢

- [Huawei HMS Map Kit](https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V5/map-introduction-V5)
- [Amap (Gaode)](https://lbs.amap.com/)
- [Google Maps Platform](https://developers.google.com/maps)

## Related Projects / 相关项目

- [hms-map](https://github.com/uulichen-sketch/hms-map) — Original HMS Map Kit MCP server
- [baidu-maps/mcp](https://github.com/baidu-maps/mcp) — Baidu Maps MCP server
- [sugarforever/amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — Amap MCP server
