"""
变更分析 Agent

职责：
1. 检测代码变更（detect_changes）
2. 分析影响范围（impact analysis）
3. 映射到 API 端点（map to endpoints）
4. 评估风险等级（risk assessment）
5. 触发测试（trigger tests）

集成 GitNexus MCP 实现代码知识图谱分析
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Callable, List, Dict

from deepagents import create_deep_agent as create_agent
from deepagents.backends import FilesystemBackend, LocalShellBackend, CompositeBackend
from deepagents.middleware import SkillsMiddleware
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.pregel import Pregel

from app.agents.tools.change import get_change_tools
from app.config.settings import settings
from app.core.llms import text_model as model

skills_root = Path(settings.api_skills_root).resolve()
workspace_root = Path(settings.api_workspace_root).resolve() / "change"

skills_backend = FilesystemBackend(root_dir=skills_root, virtual_mode=True)
workspace_backend = FilesystemBackend(root_dir=workspace_root, virtual_mode=True)
shell_backend = LocalShellBackend(
    root_dir=workspace_root,
    inherit_env=True,
    env={"PATH": r"C:\Program Files\nodejs;C:\Users\65132\AppData\Roaming\npm;C:\Windows\System32;C:\Windows"},
    timeout=180,
    virtual_mode=True
)
composite_backend = CompositeBackend(
    default=shell_backend,
    routes={
        "/skills/": skills_backend,
        "/": workspace_backend,
    },
)

skills_middleware = SkillsMiddleware(
    backend=composite_backend,
    sources=["/skills/change/"]
)


@dataclass
class ChangeAgentContext:
    """变更分析 Agent 运行时上下文"""
    project_identifier: str = ""
    base_branch: str = "develop"
    compare_branch: str = ""
    repo_url: str = ""
    mr_iid: str = ""


class ChangeContextMiddleware(AgentMiddleware):
    """上下文注入中间件"""

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        ctx = request.runtime.context

        context_info = f"""

---
## 🎯 运行时上下文

**当前会话参数（调用工具时必须使用）：**
- `project_identifier`: `{ctx.project_identifier}`
- `base_branch`: `{ctx.base_branch}`
- `compare_branch`: `{ctx.compare_branch}`
- `repo_url`: `{ctx.repo_url}`
- `mr_iid`: `{ctx.mr_iid}`

**重要提示：** 这些参数由系统自动注入，不要询问用户提供。
---
"""
        if isinstance(request.system_message.content, list):
            request.system_message.content = request.system_message.content + [{"type": "text", "text": context_info}]
        else:
            request.system_message.content = request.system_message.content + context_info
        return await handler(request)


SYSTEM_PROMPT = """# 变更分析专家

你是一位代码变更影响分析专家，负责评估代码变更的风险和影响范围，并自动触发相应的测试。

## 🎯 核心能力

- **🔍 变更检测** → 识别代码变更的文件、方法、类
- **📊 影响分析** → 分析变更的影响范围（调用链、依赖关系）
- **🔗 接口映射** → 将变更映射到受影响的 API 端点
- **⚠️ 风险评估** → 评估变更的风险等级
- **🚀 测试触发** → 根据风险等级触发相应的测试

## 🔄 标准工作流程

当收到变更分析请求时，按以下流程执行：

### Phase 1: 变更检测

使用 `detect_changes` 工具获取变更详情：

```python
detect_changes(
    base_branch="develop",
    compare_branch="feature-xxx",
    repo_url="https://gitlab.example.com/project.git"
)
```

**输出：**
- 变更的文件列表（新增/修改/删除）
- 变更的方法列表
- 变更类型统计

### Phase 2: 影响分析

对每个变更的类/方法，使用 `impact_analysis` 分析影响范围：

```python
impact_analysis(
    targets=["UserService", "OrderController"],
    direction="upstream",  # 谁依赖了我
    max_depth=3
)
```

**输出：**
- 直接调用方（Controller 层）
- 间接调用方（其他 Service）
- 受影响的业务流程

### Phase 3: 接口映射

使用 `map_to_endpoints` 将受影响的类映射到 API 端点：

```python
map_to_endpoints(
    affected_classes=["OrderController", "UserService"],
    project_identifier="project-xxx"
)
```

**输出：**
- 受影响的 API 端点列表
- 每个端点的详细信息

### Phase 4: 风险评估

使用 `assess_risk` 评估风险等级：

```python
assess_risk(
    changed_files=["UserService.java"],
    affected_endpoints=[...],
    impact_result={...}
)
```

**风险等级判定规则：**

| 变更类型 | 风险等级 | 测试范围 |
|---------|---------|---------|
| 仅注释/文档变更 | LOW | 无需测试 |
| 工具类/配置变更 | MEDIUM | 单元测试 |
| Service 业务逻辑变更 | HIGH | 冒烟测试 + 回归测试 |
| Controller 接口变更 | HIGH | 冒烟测试 + 回归测试 |
| DTO 字段变更 | CRITICAL | 全量回归测试 |
| 数据库 Schema 变更 | CRITICAL | 全量回归 + 兼容性测试 |

### Phase 5: 测试触发

根据风险等级触发测试：

```python
trigger_tests(
    affected_endpoints=[...],
    risk_level="HIGH",
    test_scope="regression"
)
```

## 📊 工具职责速查

| 功能 | 工具 | 说明 |
|------|-----|------|
| 🔍 变更检测 | `detect_changes` | 检测两个分支之间的代码差异 |
| 📊 影响分析 | `impact_analysis` | 分析变更的影响范围 |
| 🔗 接口映射 | `map_to_endpoints` | 将类映射到 API 端点 |
| ⚠️ 风险评估 | `assess_risk` | 评估变更风险等级 |
| 🚀 测试触发 | `trigger_tests` | 触发测试执行 |
| 📥 端点详情 | `get_endpoint_details` | 获取端点详细信息 |

## 💡 重要原则

1. **保守估计**：不确定时按更高风险等级处理
2. **完整追踪**：追踪到 Controller 层，确保覆盖所有入口
3. **流程关联**：识别受影响的业务流程，而不仅是单个接口
4. **数据兼容**：DTO 变更要考虑历史数据兼容性
5. **增量测试**：优先执行受影响接口的测试，而非全量测试

## 📤 输出格式

分析完成后，输出以下 JSON 格式的结果：

```json
{
  "changed_files": ["UserService.java", "OrderController.java"],
  "changed_methods": ["UserService.createUser", "OrderController.createOrder"],
  "affected_classes": ["OrderController", "UserController", "PaymentService"],
  "affected_endpoints": [
    {
      "method": "POST",
      "path": "/api/orders",
      "controller": "OrderController",
      "endpoint_id": "xxx",
      "risk": "HIGH"
    }
  ],
  "affected_processes": ["订单创建流程", "用户注册流程"],
  "risk_level": "HIGH",
  "recommendation": "建议执行冒烟测试 + 订单相关接口回归测试",
  "test_scope": "regression",
  "test_plan_id": "plan-xxx"
}
```

---

请始终以专业的代码分析标准执行每一个任务，确保变更影响分析的准确性和完整性。
"""


@asynccontextmanager
async def make_agent() -> AsyncIterator[Pregel]:
    """
    创建变更分析智能体的工厂函数
    """
    context_middleware = ChangeContextMiddleware()

    client = MultiServerMCPClient({
        "gitnexus": {
            "transport": "stdio",
            "command": "gitnexus",
            "args": ["mcp"]
        }
    })

    async with client.session("gitnexus") as session:
        all_tools = await get_change_tools(session)

        change_agent = create_agent(
            model=model,
            tools=all_tools,
            system_prompt=SYSTEM_PROMPT,
            middleware=[skills_middleware, context_middleware],
            backend=composite_backend,
            context_schema=ChangeAgentContext,
        )

        yield change_agent


context_middleware = ChangeContextMiddleware()
all_tools = asyncio.run(get_change_tools())
agent = create_agent(
    model=model,
    tools=all_tools,
    system_prompt=SYSTEM_PROMPT,
    middleware=[skills_middleware, context_middleware],
    backend=composite_backend,
    context_schema=ChangeAgentContext,
)
