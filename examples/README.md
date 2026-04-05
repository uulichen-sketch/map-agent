# Map Agent - Example Agents

This directory contains example AI agents that use Map Agent MCP tools for specific use cases. / 本目录包含使用 Map Agent MCP 工具的特定用例示例 AI agent。

## Examples / 示例

### 1. Travel Planner Agent / 旅行规划 Agent

A simple agent that plans trips using map-agent's route planning and POI search tools. / 简单 agent，使用 map-agent 的路径规划和 POI 搜索工具进行旅行规划。

**Features / 功能:**
- Multi-destination trip planning / 多目的地旅行规划
- POI search along route / 路线周边 POI 搜索
- Route optimization (shortest/fastest) / 路线优化（最短/最快）
- Travel time estimation / 旅行时间估算

**Tools Used / 使用的工具:**
- `search_nearby` - Find POIs around locations / 查找位置周边的 POI
- `search_keyword` - Search for specific places / 搜索特定地点
- `driving_route` - Plan driving routes / 规划驾驶路线
- `walking_route` - Plan walking routes / 规划步行路线
- `measure_distance` - Calculate distances / 计算距离

### 2. Place Recommendation Agent / 地点推荐 Agent

An agent that recommends places based on user preferences and map data. / 根据 用户偏好和地图数据推荐地点的 agent。

**Features / 功能:**
- Category-based recommendations (restaurants, cafes, hotels, etc.) / 基于分类的推荐（餐厅、咖啡馆、酒店等）
- Location-based recommendations (nearby popular spots) / 基于位置的推荐（附近热门地点）
- Multi-provider support (HMS/Gaode/Google) / 多 Provider 支持（华为/高德/谷歌）
- Personalized suggestions / 个性化建议

**Tools Used / 使用的工具:**
- `search_nearby` - Find places by category / 按分类查找地点
- `search_keyword` - Search for specific types of places / 搜索特定类型的地点
- `place_detail` - Get detailed information / 获取详细信息
- `geocode` - Convert addresses to coordinates / 将地址转换为坐标

### 3. Local Guide Agent / 本地向导 Agent

An agent that acts as a local tour guide, providing information about nearby attractions, restaurants, and services. / 充当地向导的 agent，提供附近景点、餐厅和服务的信息。

**Features / 功能:**
- Curated local recommendations / 精选的本地推荐
- Route planning between attractions / 景点之间的路线规划
- Real-time POI search / 实时 POI 搜索
- Category filtering (food, attractions, shopping) / 分类过滤（美食、景点、购物）

**Tools Used / 使用的工具:**
- `search_nearby` - Discover local spots / 发现本地地点
- `place_detail` - Get detailed info / 获取详细信息
- `driving_route` - Plan visits / 规划行程
- `walking_route` - Plan walking tours / 规划步行游览
- `query_suggestion` - Auto-complete location names / 地点名称自动补全

## How to Use / 如何使用

### Setup / 设置

1. Install map-agent: / 安装 map-agent

```bash
pip install map-agent
```

2. Set up environment variables: / 设置环境变量

```bash
# For HMS (Huawei) / 华为地图
export HUAWEI_MAP_API_KEY="your-hms-key"

# For Gaode (Amap) / 高德地图
export AMAP_API_KEY="your-gaode-key"
export MAP_AGENT_DEFAULT_PROVIDER="gaode"

# For Google Maps / 谷歌地图
export GOOGLE_MAPS_API_KEY="your-google-key"
export MAP_AGENT_DEFAULT_PROVIDER="google"
```

### Running Examples / 运行示例

Each example can be run independently or integrated into your own AI system. / 每个示例可以独立运行，或集成到你自己的 AI 系统中。

See individual example directories for detailed instructions. / 查看各个示例目录的详细说明。

## Provider Configuration / Provider 配置

Map Agent supports multiple map providers. Configure the default provider using the `MAP_AGENT_DEFAULT_PROVIDER` environment variable: / Map Agent 支持多个地图 Provider。使用 `MAP_AGENT_DEFAULT_PROVIDER` 环境变量配置默认 Provider：

| Provider / 服务商 | Environment Variable / 环境变量 | Default / 默认 | Best For / 最适用 |
|------------------|------------------------|---------|------------|
| HMS (Huawei) / 华为 | `HUAWEI_MAP_API_KEY` | ✅ Yes | Global / 全球 |
| Gaode (Amap) / 高德 | `AMAP_API_KEY` + `MAP_AGENT_DEFAULT_PROVIDER=gaode` | - | China / 中国 |
| Google Maps / 谷歌 | `GOOGLE_MAPS_API_KEY` + `MAP_AGENT_DEFAULT_PROVIDER=google` | - | International / 国际 |

## Integration Examples / 集成示例

### Claude Desktop Integration

Add map-agent to your `claude_desktop_config.json`: / 将 map-agent 添加到你的 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "map-agent": {
      "command": "map-agent-mcp",
      "env": {
        "MAP_AGENT_DEFAULT_PROVIDER": "gaode",
        "AMAP_API_KEY": "your-api-key"
      }
    }
  }
}
```

Then create custom agent prompts that use the available tools. / 然后创建使用可用工具的自定义 agent 提示词。

### Python Integration

```python
from mcp import Client

# Connect to map-agent server / 连接到 map-agent 服务器
client = Client("stdio")
await client.initialize()

# Use tools / 使用工具
result = await client.call_tool("search_nearby", {
    "lng": 114.0533,
    "lat": 22.5347,
    "query": "restaurants",
    "radius": 1000
})
```

## Tips / 提示

1. **Choose the right provider** / 选择正确的 Provider
   - Use HMS for global coverage / 使用 HMS 进行全球覆盖
   - Use Gaode for best China coverage / 使用高德在中国获得最佳覆盖
   - Use Google for international users and transit mode / 使用 Google 服务国际用户和公交模式

2. **Handle API rate limits** / 处理 API 速率限制
   - Implement request queuing / 实现请求队列
   - Cache results when possible / 可能时缓存结果
   - Use appropriate timeouts / 使用适当的超时

3. **Error handling** / 错误处理
   - Always check for error codes / 始终检查错误码
   - Provide helpful error messages / 提供有用的错误信息
   - Fallback to alternative providers / 回退到备用 Provider

4. **Optimize for your use case** / 优化你的用例
   - For local guides: Use Gaode (best China coverage) / 本地向导：使用高德（中国最佳覆盖）
   - For international travel: Use Google (transit mode) / 国际旅行：使用谷歌（公交模式）
   - For quick lookups: Use HMS or cache results / 快速查找：使用 HMS 或缓存结果

## Contributing / 贡献

Have an idea for a new example agent? / 有新示例 agent 的想法？

1. Create a new directory in `examples/` / 在 `examples/` 中创建新目录
2. Implement your agent logic / 实现 agent 逻辑
3. Document the tools used / 记录使用的工具
4. Add usage instructions / 添加使用说明
5. Submit a pull request! / 提交 PR！

---

For more information about Map Agent, visit: / 更多关于 Map Agent 的信息，请访问：
- Repository: https://github.com/uulichen-sketch/map-agent
- Documentation: https://github.com/uulichen-sketch/map-agent/blob/main/README.md
- API Reference: https://github.com/uulichen-sketch/map-agent/blob/main/docs/API.md
