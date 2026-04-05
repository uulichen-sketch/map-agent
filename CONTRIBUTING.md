# Contributing to Map Agent / 为 Map Agent 做贡献

Thank you for your interest in contributing to Map Agent! / 感谢您对 Map Agent 的贡献兴趣！

## Getting Started / 快速开始

### Prerequisites / 前置要求

- Python 3.10+ / Python 3.10+
- Git / Git
- Basic knowledge of MCP (Model Context Protocol) / 对 MCP (Model Context Protocol) 的基本了解
- Understanding of async/await in Python / 理解 Python 中的 async/await

### Fork and Clone / Fork 和克隆

1. Fork the repository on GitHub / 在 GitHub 上 Fork 仓库
2. Clone your fork locally / 本地克隆您的 fork:

```bash
git clone https://github.com/YOUR_USERNAME/map-agent.git
cd map-agent
```

### Set Up Development Environment / 设置开发环境

```bash
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

## Development Workflow / 开发工作流

### Branch Naming / 分支命名

Use descriptive branch names: / 使用描述性分支名称：

- `feature/add-new-provider` - New feature / 新功能
- `fix/fix-geocoding-error` - Bug fix / 错误修复
- `docs/update-readme` - Documentation update / 文档更新
- `refactor/improve-performance` - Code refactoring / 代码重构

### Commit Messages / 提交信息

Follow conventional commit format: / 遵循约定式提交格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types / 类型:**

- `feat`: New feature / 新功能
- `fix`: Bug fix / 错误修复
- `docs`: Documentation changes / 文档变更
- `style`: Code style changes (formatting, etc.) / 代码风格变更（格式化等）
- `refactor`: Code refactoring / 代码重构
- `test`: Adding or updating tests / 添加或更新测试
- `chore`: Maintenance tasks / 维护任务

**Examples / 示例:**

```bash
feat(providers): add Google Maps provider

fix(api): handle timeout errors in geocoding

docs(readme): update installation instructions

test(hms): add tests for nearby search
```

### Testing / 测试

Before submitting a pull request: / 在提交 Pull Request 之前：

1. Write tests for new functionality / 为新功能编写测试
2. Ensure all tests pass / 确保所有测试通过
3. Maintain test coverage / 维护测试覆盖率

```bash
# Run specific test file / 运行特定测试文件
pytest tests/test_providers/test_hms.py

# Run with verbose output / 详细输出
pytest -v

# Run tests for a specific provider / 运行特定 provider 的测试
pytest tests/test_providers/ -k "hms"
```

## Code Style / 代码风格

### Formatting / 格式化

We recommend using `black` for Python code formatting: / 我们推荐使用 `black` 进行 Python 代码格式化：

```bash
pip install black
black src/map_agent tests/
```

### Type Hints / 类型提示

All new code should include type hints: / 所有新代码应包含类型提示：

```python
from typing import Optional, List

async def search_nearby(
    lat: float,
    lon: float,
    keyword: Optional[str] = None,
) -> List[POI]:
    """Search for places near a location."""
    pass
```

### Docstrings / 文档字符串

Use Google-style docstrings: / 使用 Google 风格的文档字符串：

```python
def search_nearby(lat: float, lon: float, keyword: str) -> List[POI]:
    """Search for places near a given location.

    Args:
        lat: Latitude of the center point.
        lon: Longitude of the center point.
        keyword: Search keyword to filter results.

    Returns:
        List of POI objects sorted by distance.

    Raises:
        NetworkError: On network connectivity issues.
        APIError: On provider API errors.
    """
```

## Adding a New Provider / 添加新 Provider

### Step 1: Create Provider Class / 第一步：创建 Provider 类

Create a new file in `src/map_agent/providers/` following the pattern: / 在 `src/map_agent/providers/` 中创建新文件，遵循模式：

```python
# src/map_agent/providers/newprovider.py

from .base import MapProvider, POI, Route, GeocodeResult

class NewProvider(MapProvider):
    provider_id = "newprovider"
    provider_name = "New Provider Name"

    async def search_nearby(self, lat, lon, radius, keyword=None, ...):
        # Implementation / 实现
        pass

    # Implement all other required methods / 实现所有其他必需方法
```

### Step 2: Register Provider / 第二步：注册 Provider

Add to `src/map_agent/providers/factory.py`: / 添加到 `src/map_agent/providers/factory.py`：

```python
from .newprovider import NewProvider

ProviderRegistry.register("newprovider", NewProvider)
```

Add to `src/map_agent/providers/__init__.py`: / 添加到 `src/map_agent/providers/__init__.py`：

```python
from .newprovider import NewProvider

__all__ = [
    # ... existing exports
    "NewProvider",
]
```

### Step 3: Add Configuration / 第三步：添加配置

Add environment variable support in `factory.py`: / 在 `factory.py` 中添加环境变量支持：

```python
elif provider_id == "newprovider":
    api_key = os.getenv("NEWPROVIDER_API_KEY")
    if not api_key:
        raise ValueError("NEWPROVIDER_API_KEY environment variable is not set.")
    config["api_key"] = api_key
```

### Step 4: Add Tests / 第四步：添加测试

Create `tests/test_providers/test_newprovider.py`: / 创建 `tests/test_providers/test_newprovider.py`：

```python
import pytest
from map_agent.providers.newprovider import NewProvider

@pytest.mark.asyncio
async def test_new_provider_creation():
    provider = NewProvider(api_key="test-key")
    assert provider.provider_id == "newprovider"

# Add more tests / 添加更多测试
```

## Adding a New Tool / 添加新工具

### Step 1: Define Tool / 第一步：定义工具

Add to `src/map_agent/server.py`: / 添加到 `src/map_agent/server.py`：

```python
@mcp_server.tool()
async def new_tool(
    param1: str,
    param2: int,
) -> str:
    """Description of what this tool does.

    Args:
        param1: Description
        param2: Description

    Returns:
        JSON string response
    """
    try:
        # Implementation / 实现
        result = await _get_provider().some_method()
        return json.dumps({"returnCode": "0", "data": result})
    except Exception as e:
        return json.dumps({"error": True, "message": str(e)})
```

### Step 2: Add Tests / 第二步：添加测试

Create tests in `tests/test_tools/`: / 在 `tests/test_tools/` 中创建测试：

```python
@pytest.mark.asyncio
async def test_new_tool():
    # Test implementation / 测试实现
    pass
```

### Step 3: Update Documentation / 第三步：更新文档

- Update `README.md` with the new tool / 在 `README.md` 中更新新工具
- Update `docs/API.md` with parameters and examples / 在 `docs/API.md` 中更新参数和示例
- Add examples to `docs/QUICKSTART.md` / 向 `docs/QUICKSTART.md` 添加示例

## Submitting Changes / 提交更改

### Pull Request Process / Pull Request 流程

1. Update documentation / 更新文档
2. Add or update tests / 添加或更新测试
3. Ensure all tests pass / 确保所有测试通过
4. Push to your fork / 推送到您的 fork
5. Create Pull Request on GitHub / 在 GitHub 上创建 Pull Request

### Pull Request Description / Pull Request 描述

Include in your PR: / 在您的 PR 中包含：

- Description of changes / 变更描述
- Related issue number (if any) / 相关问题编号（如果适用）
- Screenshots (if UI changes) / 截图（如果是 UI 变更）
- Test results / 测试结果

## Questions? / 有问题？

- Open an issue for feature requests / 为功能请求提交 issue
- Open an issue for bugs / 为错误提交 issue
- Ask in Discussions / 在 Discussions 中提问

## Code Review Guidelines / 代码审查指南

### What to Review / 审查什么

- **Functionality**: Does it work as expected? / 功能：是否按预期工作？
- **Tests**: Are tests comprehensive? / 测试：测试是否全面？
- **Documentation**: Is documentation updated? / 文档：文档是否更新？
- **Code Style**: Does it follow conventions? / 代码风格：是否遵循约定？
- **Type Safety**: Are type hints correct? / 类型安全：类型提示是否正确？
- **Error Handling**: Are errors properly handled? / 错误处理：错误是否正确处理？

### Review Feedback / 审查反馈

- Be constructive and respectful / 建设性和尊重
- Explain your reasoning / 解释你的理由
- Suggest improvements / 建议改进
- Thank contributors / 感谢贡献者

## License / 许可证

By contributing, you agree that your contributions will be licensed under the MIT License. / 通过贡献，您同意您的贡献将在 MIT 许可证下许可。

---

**Thank you for contributing to Map Agent! / 感谢您为 Map Agent 做贡献！**
