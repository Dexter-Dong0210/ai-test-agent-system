# 测试指南

## 📋 测试概览

本项目采用 pytest 作为测试框架，包含单元测试和集成测试。

## 🚀 快速开始

### 安装测试依赖

```bash
cd backend
pip install -e ".[dev]"
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行单个文件
pytest tests/unit/test_project_service.py

# 运行单个测试方法
pytest tests/unit/test_project_service.py::TestProjectService::test_get_project_success
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看HTML报告
open htmlcov/index.html
```

## 📁 测试结构

```
backend/tests/
├── conftest.py              # 测试配置和fixtures
├── unit/                    # 单元测试
│   ├── test_project_service.py
│   ├── test_folder_service.py
│   └── test_cache.py
├── integration/             # 集成测试
│   ├── test_api_projects.py
│   └── test_api_folders.py
└── fixtures/                # 测试数据
    ├── projects.json
    └── folders.json
```

## ✍️ 编写测试

### 单元测试示例

```python
import pytest
from app.services.project_service import ProjectService

@pytest.mark.asyncio
class TestProjectService:
    async def test_get_project(self, db_session):
        """测试获取项目"""
        service = ProjectService(db_session)
        # 测试逻辑
        assert True
```

### 集成测试示例

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestAPI:
    async def test_endpoint(self, client: AsyncClient):
        """测试API端点"""
        response = await client.get("/api/v2/projects")
        assert response.status_code == 200
```

### 使用 Fixtures

```python
@pytest.mark.asyncio
async def test_with_fixtures(
    db_session,      # 数据库会话
    client,          # HTTP客户端
    test_user_id,    # 测试用户ID
    auth_headers     # 认证头
):
    # 测试逻辑
    pass
```

## 🔧 测试配置

测试配置位于 `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--cov=app",
    "--cov-fail-under=60"
]
```

## 📊 测试目标

- **单元测试覆盖率**: > 80%
- **集成测试覆盖**: 核心API端点100%
- **测试执行时间**: < 30秒

## ⚠️ 注意事项

1. **异步测试**: 使用 `@pytest.mark.asyncio`
2. **数据库隔离**: 每个测试使用独立的内存数据库
3. **Mock外部依赖**: 使用 `unittest.mock` 或 `pytest-mock`
4. **测试数据**: 使用 fixtures 或工厂模式

## 🐛 调试测试

```bash
# 显示打印输出
pytest -s tests/unit/test_example.py

# 详细输出
pytest -vv tests/unit/test_example.py

# 进入调试器
pytest --pdb tests/unit/test_example.py
```

## 📚 参考资料

- [pytest文档](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)