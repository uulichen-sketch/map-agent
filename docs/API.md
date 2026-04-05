# Map Agent API Reference

## MCP Tools / MCP 工具

### Search Tools / 搜索工具

#### search_nearby

Search for places near a given location. / 在指定位置附近搜索地点。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `lng` | number | ✅ | Longitude / 经度 |
| `lat` | number | ✅ | Latitude / 纬度 |
| `query` | string | ❌ | Search keyword / 搜索关键词 |
| `radius` | number | ❌ | Search radius in meters, default 1000 / 搜索半径（米），默认 1000 |
| `category` | string | ❌ | POI category filter / POI 分类过滤 |
| `language` | string | ❌ | Response language / 响应语言 |
| `pageSize` | number | ❌ | Results per page, default 20 / 每页结果数，默认 20 |
| `pageIndex` | number | ❌ | Page number, default 1 / 页码，默认 1 |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "sites": [
    {
      "siteId": "poi-id",
      "name": "Place Name",
      "formatAddress": "Full Address",
      "location": {"lat": 22.5347, "lng": 114.0533},
      "distance": 150.5,
      "poi": {
        "type": "restaurant",
        "phone": "+86-1234567890",
        "websiteUrl": "https://example.com",
        "rating": 4.5
      }
    }
  ],
  "totalCount": 10
}
```

#### search_keyword

Search for places by keyword across a region. / 按关键词在区域内搜索地点。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `query` | string | ✅ | Search query / 搜索关键词 |
| `lng` | number | ❌ | Center longitude for biasing / 中心经度（用于偏好结果） |
| `lat` | number | ❌ | Center latitude for biasing / 中心纬度（用于偏好结果） |
| `radius` | number | ❌ | Search radius / 搜索半径 |
| `category` | string | ❌ | POI category filter / POI 分类过滤 |
| `language` | string | ❌ | Response language / 响应语言 |
| `pageSize` | number | ❌ | Results per page / 每页结果数 |
| `pageIndex` | number | ❌ | Page number / 页码 |

#### place_detail

Get detailed information about a place. / 获取地点详细信息。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `poi_id` | string | ✅ | Place ID / 地点 ID |
| `language` | string | ❌ | Response language / 响应语言 |

#### query_suggestion

Get search query suggestions / autocomplete. / 获取搜索建议/自动补全。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `query` | string | ✅ | Partial query / 部分查询词 |
| `lng` | number | ❌ | Center longitude / 中心经度 |
| `lat` | number | ❌ | Center latitude / 中心纬度 |
| `radius` | number | ❌ | Search radius / 搜索半径 |
| `language` | string | ❌ | Response language / 响应语言 |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "suggestions": [
    "Shenzhen Bay Park",
    "Shenzhen University",
    "Shenzhen Library"
  ]
}
```

### Geocoding Tools / 地理编码工具

#### geocode

Convert an address to geographic coordinates. / 将地址转换为地理坐标。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `address` | string | ✅ | Structured address / 结构化地址 |
| `language` | string | ❌ | Response language / 响应语言 |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "sites": [
    {
      "name": "Shenzhen, China",
      "location": {"lat": 22.5431, "lng": 114.0579}
    }
  ]
}
```

#### reverse_geocode

Convert geographic coordinates to an address. / 将地理坐标转换为地址。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `lng` | number | ✅ | Longitude / 经度 |
| `lat` | number | ✅ | Latitude / 纬度 |
| `language` | string | ❌ | Response language / 响应语言 |
| `radius` | number | ❌ | Search radius / 搜索半径 |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "sites": [
    {
      "siteId": "geo-001",
      "name": "Shenzhen, China",
      "formatAddress": "Nanshan District, Shenzhen, China",
      "location": {"lat": 22.5431, "lng": 114.0579},
      "address": {
        "country": "China",
        "province": "Guangdong",
        "city": "Shenzhen",
        "district": "Nanshan"
      }
    }
  ]
}
```

### Route Planning Tools / 路径规划工具

#### driving_route

Plan a driving route between two points. / 规划两点间的驾车路线。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `origin_lng` | number | ✅ | Origin longitude / 起点经度 |
| `origin_lat` | number | ✅ | Origin latitude / 起点纬度 |
| `dest_lng` | number | ✅ | Destination longitude / 终点经度 |
| `dest_lat` | number | ✅ | Destination latitude / 终点纬度 |
| `waypoints` | array | ❌ | Intermediate points as [{lat, lng}] / 中途经点 |
| `avoid` | array | ❌ | Avoid features: ["toll", "highway", "ferry"] / 避让特性 |
| `alternatives` | boolean | ❌ | Return multiple routes / 返回多条路线 |
| `language` | string | ❌ | Response language / 响应语言 |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "routes": [
    {
      "distance": 5000,
      "duration": 900,
      "polyline": "encoded_polyline_string",
      "bounds": {
        "southwest": {"lat": 22.52, "lng": 114.04},
        "northeast": {"lat": 22.55, "lng": 114.07}
      },
      "steps": [
        {
          "instruction": "Head north on Main Street",
          "distance": 500,
          "duration": 90,
          "action": "straight"
        },
        {
          "instruction": "Turn right onto Oak Avenue",
          "distance": 300,
          "duration": 60,
          "action": "turn-right"
        }
      ]
    }
  ]
}
```

#### walking_route

Plan a walking route between two points. / 规划两点间的步行路线。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `origin_lng` | number | ✅ | Origin longitude / 起点经度 |
| `origin_lat` | number | ✅ | Origin latitude / 起点纬度 |
| `dest_lng` | number | ✅ | Destination longitude / 终点经度 |
| `dest_lat` | number | ✅ | Destination latitude / 终点纬度 |
| `language` | string | ❌ | Response language / 响应语言 |

#### bicycling_route

Plan a bicycling route between two points. / 规划两点间的骑行路线。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `origin_lng` | number | ✅ | Origin longitude / 起点经度 |
| `origin_lat` | number | ✅ | Origin latitude / 起点纬度 |
| `dest_lng` | number | ✅ | Destination longitude / 终点经度 |
| `dest_lat` | number | ✅ | Destination latitude / 终点纬度 |
| `avoid` | array | ❌ | Avoid features: ["ferry"] / 避让特性（仅支持 ferry） |
| `language` | string | ❌ | Response language / 响应语言 |

#### transit_route

Plan a public transit route (bus/metro) between two points. / 规划两点间的公交路线。

**Note / 注意**: Only Google Maps provider supports this mode. / 仅 Google Maps provider 支持此模式。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `origin_lng` | number | ✅ | Origin longitude / 起点经度 |
| `origin_lat` | number | ✅ | Origin latitude / 起点纬度 |
| `dest_lng` | number | ✅ | Destination longitude / 终点经度 |
| `dest_lat` | number | ✅ | Destination latitude / 终点纬度 |
| `language` | string | ❌ | Response language / 响应语言 |

### Utility Tools / 实用工具

#### measure_distance

Measure distance between multiple points. / 测量多个点之间的距离。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `points` | array | ✅ | List of points: [{lat: 22.5, lng: 114.0}, ...] / 点列表 |
| `mode` | string | ❌ | Mode: "straight" (Euclidean) or "route" (actual driving) / 模式："straight"（欧几里得直线）或 "route"（实际驾驶路线） |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "total_distance": 1500.5,
  "unit": "meters",
  "mode": "straight",
  "segments": [
    {
      "from": {"lat": 22.5347, "lng": 114.0533},
      "to": {"lat": 22.5431, "lng": 114.0579},
      "distance": 1500.5
    }
  ]
}
```

#### ip_geolocate

Get geolocation information for an IP address. / 获取 IP 地址的地理定位信息。

**Parameters / 参数:**

| Name / 名称 | Type / 类型 | Required / 必需 | Description / 描述 |
|-------------|-------------|------------------|---------------------|
| `ip_address` | string | ❌ | IP address to lookup (if None, uses client's IP) / 要查询的 IP（如果为 None，则使用客户端 IP） |

**Returns / 返回:**

```json
{
  "returnCode": "0",
  "ip": "1.2.3.4",
  "country_code": "CN",
  "country": "China",
  "region": "Guangdong",
  "city": "Shenzhen",
  "latitude": 22.5431,
  "longitude": 114.0579,
  "isp": "China Telecom"
}
```

## Error Codes / 错误码

| Code / 代码 | Description / 描述 |
|-------------|---------------------|
| `"0"` | Success / 成功 |
| `"1001"` | Invalid parameter / 无效参数 |
| `"404"` | Not found / 未找到 |
| `"500"` | Internal server error / 服务器内部错误 |

## Coordinate System / 坐标系

All tools use WGS-84 (World Geodetic System 1984) coordinate system. / 所有工具使用 WGS-84 坐标系。

- **Format / 格式**: `(longitude, latitude)` or `{lng, lat}` / （经度, 纬度）或 {lng, lat}
- **Units / 单位**: Degrees decimal / 十进制度
- **Range / 范围**: Longitude: -180 to 180, Latitude: -90 to 90 / 经度：-180 到 180，纬度：-90 到 90

## Provider-Specific Notes / Provider 特定说明

### HMS (Huawei) / 华为

- `hwPoiType` parameter for HMS POI types / `hwPoiType` 参数用于 HMS POI 分类
- Route avoid codes: 1=toll, 2=highway, 8=ferry / 路径避让代码：1=收费站，2=高速，8=轮渡

### Gaode (高德)

- `types` parameter for Gaode POI categories / `types` 参数用于高德 POI 分类
- No public transit route support / 不支持公交路线规划

### Google Maps / 谷歌

- `types` parameter for Google Maps place types / `types` 参数用于 Google 地点类型
- Full transit support with bus/metro/subway / 完整公交支持（公交/地铁/轻轨）
- Route avoid options: "tolls", "highways", "ferries" / 路径避让选项："tolls"（收费站），"highways"（高速），"ferries"（轮渡）
