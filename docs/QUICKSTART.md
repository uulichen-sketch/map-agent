# Quick Start Guide / 快速上手指南

## 5-Minute Setup / 5 分钟快速配置

### Step 1: Install / 第一步：安装

```bash
pip install map-agent
```

### Step 2: Get API Key / 第二步：获取 API Key

Choose a provider and get your API key: / 选择一个 provider 并获取 API Key：

#### Option A: HMS (Huawei) / 选项 A：华为

1. Visit [AppGallery Connect](https://developer.huawei.com/consumer/cn/service/josp/agc/index.html) / 访问 AppGallery Connect
2. Create an account or sign in / 创建账号或登录
3. Go to "My Projects" → "Manage APIs" → "Map Kit" / 进入"我的项目" → "管理 API" → "Map Kit"
4. Enable Map Kit API / 启用 Map Kit API
5. Copy the API Key / 复制 API Key

```bash
export HUAWEI_MAP_API_KEY="your-hms-api-key"
```

#### Option B: Gaode (Amap) / 选项 B：高德

1. Visit [Amap Console](https://console.amap.com/dev/key/app) / 访问高德控制台
2. Sign in with your account / 使用账号登录
3. Click "Create App" → "Key Management" / 点击"创建应用" → "Key 管理"
4. Add your app and get the API Key / 添加应用并获取 API Key

```bash
export AMAP_API_KEY="your-gaode-api-key"
```

#### Option C: Google Maps / 选项 C：谷歌

1. Visit [Google Cloud Console](https://console.cloud.google.com/apis/library) / 访问 Google Cloud Console
2. Create a new project or select existing / 创建新项目或选择现有项目
3. Enable Maps JavaScript API and Places API / 启用 Maps JavaScript API 和 Places API
4. Go to "Credentials" → "Create Credentials" → "API Key" / 进入"凭据" → "创建凭据" → "API Key"
5. Copy the API Key / 复制 API Key

```bash
export GOOGLE_MAPS_API_KEY="your-google-api-key"
```

### Step 3: Set Default Provider / 第三步：设置默认 Provider

```bash
export MAP_AGENT_DEFAULT_PROVIDER="hms"  # or 'gaode' or 'google'
```

## Configuration Examples / 配置示例

### Claude Desktop Configuration

Create or edit `~/.config/claude/claude_desktop_config.json`: / 创建或编辑 `~/.config/claude/claude_desktop_config.json`：

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

### VS Code Configuration

Create `.vscode/mcp.json` in your project: / 在项目目录中创建 `.vscode/mcp.json`：

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

### Web Application (SSE Transport)

For web-based applications: / 适用于 Web 应用：

```bash
# Start SSE server / 启动 SSE 服务器
map-agent serve --transport sse --host 0.0.0.0 --port 8000
```

Then connect to `http://localhost:8000/sse` for Server-Sent Events. / 然后连接到 `http://localhost:8000/sse` 接收服务器推送事件。

### Streamable-HTTP Transport

For long-running operations with progress updates: / 适用于需要进度更新的长时操作：

```bash
map-agent serve --transport streamable-http --host 0.0.0.0 --port 8001
```

Send POST requests to `http://localhost:8001/mcp/stream`. / 向 `http://localhost:8001/mcp/stream` 发送 POST 请求。

## Common Use Cases / 常见使用场景

### Scenario 1: Find Nearby Restaurants / 场景 1：查找附近餐厅

**In Claude Desktop / Claude Desktop 中:**

```
Search for restaurants within 1km of my current location.
I'm at coordinates 114.0533, 22.5347.
```

**Response / 响应:**

The MCP server will call `search_nearby` with:
- `lng`: 114.0533
- `lat`: 22.5347
- `query`: "restaurants"
- `radius`: 1000

### Scenario 2: Plan a Route / 场景 2：规划路线

**In Claude Desktop / Claude Desktop 中:**

```
Plan a driving route from my location to Shenzhen Bay Park.
I'm at 114.0533, 22.5347.
Shenzhen Bay Park is at 113.9342, 22.4879.
```

**Response / 响应:**

The MCP server will call `driving_route` with:
- `origin_lng`: 114.0533
- `origin_lat`: 22.5347
- `dest_lng`: 113.9342
- `dest_lat`: 22.4879
- `mode`: "driving"

### Scenario 3: Convert Address to Coordinates / 场景 3：地址转坐标

**In Claude Desktop / Claude Desktop 中:**

```
Convert "深圳市南山区科技园" to coordinates.
```

**Response / 响应:**

The MCP server will call `geocode` with:
- `address`: "深圳市南山区科技园"
- `language`: "zh-CN"

### Scenario 4: Measure Distance / 场景 4：测量距离

**In Claude Desktop / Claude Desktop 中:**

```
Measure the straight-line distance between:
1. Shenzhen University (22.5431, 114.0579)
2. Shenzhen Bay Park (22.4879, 113.9342)
```

**Response / 响应:**

The MCP server will call `measure_distance` with:
- `points`: [
    {"lat": 22.5431, "lng": 114.0579},
    {"lat": 22.4879, "lng": 113.9342}
  ]
- `mode`: "straight"

### Scenario 5: Get IP Geolocation / 场景 5：获取 IP 地理定位

**In Claude Desktop / Claude Desktop 中:**

```
Where is the IP address 8.8.8.8 located?
```

**Response / 响应:**

The MCP server will call `ip_geolocate` with:
- `ip_address`: "8.8.8.8"

## CLI Quick Reference / 命令行快速参考

```bash
# Search tools / 搜索工具
map-agent nearby --lng 114.0533 --lat 22.5347 --query "coffee" --radius 2000
map-agent keyword "restaurants" --lng 114.0533 --lat 22.5347
map-agent detail --poi-id "poi-123"
map-agent suggest "starbucks" --lng 114.0533 --lat 22.5347

# Geocoding / 地理编码
map-agent geocode --address "Shenzhen, China"
map-agent reverse-geocode --lng 114.0533 --lat 22.5347

# Route planning / 路径规划
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode driving
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode walking
map-agent route --origin "114.0533,22.5347" --dest "114.0579,22.5431" --mode bicycling

# Server modes / 服务器模式
map-agent serve --transport stdio    # Default / 默认
map-agent serve --transport sse       # Web SSE / Web SSE
map-agent serve --transport streamable-http  # Long-running ops / 长时操作
```

## Troubleshooting / 故障排除

### Issue: API Key Not Found / 问题：找不到 API Key

**Solution / 解决方案:**

```bash
# Check if API key is set / 检查 API Key 是否设置
echo $HUAWEI_MAP_API_KEY
echo $AMAP_API_KEY
echo $GOOGLE_MAPS_API_KEY

# If empty, set it / 如果为空，则设置
export HUAWEI_MAP_API_KEY="your-key"
```

### Issue: MCP Server Not Connecting / 问题：MCP 服务器无法连接

**Solution / 解决方案:**

```bash
# Test server manually / 手动测试服务器
map-agent-mcp

# Should see logs like / 应该看到类似日志：
# Using provider: hms
# Starting MCP server with stdio transport...
```

### Issue: Provider Not Supported / 问题：Provider 不支持

**Solution / 解决方案:**

```bash
# List available providers / 列出可用 providers
python -c "from map_agent.providers import list_providers; print(list_providers())"

# Should output: / 应该输出:
# {'hms': 'Huawei Map Kit', 'gaode': 'Amap (高德地图)', 'google': 'Google Maps Platform'}
```

### Issue: CORS Errors on Web Client / 问题：Web 客户端 CORS 错误

**Solution / 解决方案:**

When using SSE or streamable-http transport from a web application, ensure CORS is configured: / 使用 SSE 或 streamable-http 传输时，确保已配置 CORS：

```bash
# The server should be started with proper host binding / 服务器应使用正确的主机绑定
map-agent serve --transport sse --host 0.0.0.0 --port 8000
```

## Next Steps / 下一步

- Read the full [API documentation](API.md) / 阅读完整的 [API 文档](API.md)
- Explore [CLI examples](README.md#cli-usage) / 探索 [CLI 示例](README.md#cli-usage)
- Check out the [architecture](README.md#architecture) / 查看 [架构说明](README.md#architecture)
- [Contributing guidelines](README.md#contributing) / [贡献指南](README.md#contributing)

## Getting Help / 获取帮助

- **GitHub Issues**: https://github.com/uulichen-sketch/map-agent/issues
- **Documentation**: https://github.com/uulichen-sketch/map-agent/blob/main/README.md
- **API Reference**: https://github.com/uulichen-sketch/map-agent/blob/main/docs/API.md
