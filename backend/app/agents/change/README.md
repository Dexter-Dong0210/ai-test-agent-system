# 代码变更自动化测试系统

## 概述

本系统实现了"代码改动 → 自动分析影响范围 → 自动生成测试用例 → 自动执行测试 → 门禁判断"的完整闭环。

## 架构

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Git Hook    │───▶│  变更分析     │───▶│  测试生成     │───▶│  门禁判断     │
│  触发器      │    │  Agent       │    │  + 执行      │    │  + 通知      │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ GitLab/GitHub│    │  GitNexus    │    │  API Agent   │    │  测试报告     │
│  Webhook     │    │  impact()    │    │  已有能力    │    │  + 钉钉通知   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

## 文件结构

```
backend/app/
├── agents/
│   └── change/                    # 变更分析 Agent
│       ├── __init__.py
│       └── agent.py               # Agent 定义和系统提示词
│
├── agents/tools/change/           # 变更分析工具
│   ├── __init__.py
│   ├── git_tools.py               # Git 操作（变更检测）
│   ├── impact_tools.py            # 影响分析（GitNexus 集成）
│   ├── mapping_tools.py           # 代码→接口映射
│   ├── risk_tools.py              # 风险评估
│   ├── test_tools.py              # 测试触发
│   └── endpoint_tools.py          # 端点查询
│
├── api/v2/
│   ├── change.py                  # 变更分析 API
│   └── change_webhook.py          # Git Webhook 接收器
│
├── integrations/
│   └── gate.py                    # 门禁机制
│
├── services/
│   ├── change_workflow.py         # 工作流编排
│   └── change_workflow_store.py   # 工作流存储
│
└── config/
    └── change_analysis.py         # 配置

scripts/git-hooks/
├── pre-push                       # Git pre-push hook
└── pre-commit                     # Git pre-commit hook

ci-templates/
├── .gitlab-ci.yml                 # GitLab CI 配置
└── Jenkinsfile                    # Jenkins Pipeline
```

## 使用方式

### 方式一：GitLab Webhook（推荐）

1. **配置 GitLab Webhook**

   在 GitLab 项目设置中添加 Webhook：
   - URL: `http://your-platform:8001/api/v2/webhook/gitlab/merge_request`
   - Secret Token: 你的密钥
   - Trigger: Merge Request events

2. **配置环境变量**

   在 `.env` 文件中添加：
   ```env
   GITLAB_URL=https://gitlab.example.com
   GITLAB_TOKEN=your-gitlab-token
   DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
   ```

3. **创建 MR 触发分析**

   当创建或更新 MR 时，系统会自动：
   - 检测代码变更
   - 分析影响范围
   - 映射到 API 端点
   - 触发测试
   - 评估门禁
   - 更新 MR 状态

### 方式二：本地 Git Hook

1. **安装 Git Hook**

   ```bash
   # 复制 hook 脚本
   cp scripts/git-hooks/pre-push .git/hooks/
   chmod +x .git/hooks/pre-push
   
   # 配置环境变量
   export AI_TEST_PLATFORM=http://localhost:8001
   export AI_PLATFORM_TOKEN=your-token
   ```

2. **推送代码触发分析**

   ```bash
   git push origin feature/xxx
   ```

### 方式三：手动调用 API

```bash
curl -X POST http://localhost:8001/api/v2/change/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "base_branch": "develop",
    "compare_branch": "feature/user-service",
    "repo_url": "https://gitlab.example.com/project.git",
    "project_id": "project-123"
  }'
```

### 方式四：CI/CD 集成

参考 `ci-templates/` 目录下的配置文件。

## 工作流步骤

```
Step 1: 变更检测
   ↓
Step 2: 影响分析（调用 GitNexus impact）
   ↓
Step 3: 接口映射（Controller → API 端点）
   ↓
Step 4: 风险评估
   ↓
Step 5: 测试触发
   ↓
Step 6: 获取测试结果
   ↓
Step 7: 门禁评估
   ↓
Step 8: 结果处理（更新 MR、发送通知）
```

## 风险等级

| 风险等级 | 触发条件 | 测试范围 | 门禁动作 |
|---------|---------|---------|---------|
| LOW | 仅文档/注释变更 | 无需测试 | 放行 |
| MEDIUM | 工具类/配置变更 | 单元测试 | 警告 |
| HIGH | Service/Controller 变更 | 冒烟+回归 | 阻断 |
| CRITICAL | DTO/Entity 变更 | 全量回归 | 阻断+需审批 |

## 门禁规则

```yaml
LOW:
  min_pass_rate: 80%
  action: allow

MEDIUM:
  min_pass_rate: 90%
  min_coverage: 50%
  action: warn

HIGH:
  min_pass_rate: 100%
  min_coverage: 70%
  action: block

CRITICAL:
  min_pass_rate: 100%
  min_coverage: 80%
  action: block
  require_approval: true
```

## API 接口

### 触发变更分析

```
POST /api/v2/change/analyze
```

请求体：
```json
{
  "base_branch": "develop",
  "compare_branch": "feature-xxx",
  "repo_url": "https://gitlab.example.com/project.git",
  "project_id": "project-123",
  "mr_iid": 42
}
```

响应：
```json
{
  "workflow_id": "uuid",
  "status": "triggered",
  "message": "变更分析已触发"
}
```

### 查询工作流状态

```
GET /api/v2/change/workflow/{workflow_id}
```

响应：
```json
{
  "workflow_id": "uuid",
  "status": "passed",
  "steps": [...],
  "analysis_result": {
    "risk_level": "HIGH",
    "affected_endpoints": [...]
  },
  "test_result": {
    "total": 10,
    "passed": 10
  },
  "gate_result": {
    "status": "passed",
    "action": "allow"
  }
}
```

### 评估门禁

```
POST /api/v2/change/gate/evaluate
```

请求体：
```json
{
  "test_results": {
    "total": 10,
    "passed": 9,
    "failed": 1
  },
  "analysis_result": {
    "risk_level": "HIGH"
  }
}
```

## GitNexus 集成

系统通过 MCP 协议调用 GitNexus 的以下工具：

- `impact`: 分析代码变更的影响范围
- `detect_changes`: 检测 Git diff
- `context`: 获取符号上下文

## 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| CHANGE_ANALYSIS_ENABLED | 是否启用 | true |
| CHANGE_ANALYSIS_TRIGGER_BRANCHES | 触发分支 | feature/*, hotfix/* |
| CHANGE_ANALYSIS_IMPACT_MAX_DEPTH | 影响分析深度 | 3 |
| CHANGE_ANALYSIS_GATE_ENABLED | 是否启用门禁 | true |
| GITLAB_URL | GitLab 地址 | - |
| GITLAB_TOKEN | GitLab Token | - |
| DINGTALK_WEBHOOK | 钉钉 Webhook | - |

## 通知

支持以下通知渠道：

- 钉钉
- 飞书
- 邮件

通知场景：
- 工作流开始
- 工作流完成
- 门禁失败
- 工作流异常

## 扩展

### 添加新的代码框架支持

在 `mapping_tools.py` 中添加新的解析函数：

```python
def _parse_spring_controller(file_path: str) -> List[Dict]:
    # 解析 Spring Boot Controller
    pass

def _parse_nestjs_controller(file_path: str) -> List[Dict]:
    # 解析 NestJS Controller
    pass
```

### 添加新的门禁规则

在 `gate.py` 的 `_default_rules()` 中添加：

```python
def _default_rules(self) -> Dict:
    return {
        # ... 现有规则
        "CUSTOM": {
            "min_pass_rate": 95,
            "min_coverage": 60,
            "custom_check": "xxx",
            "action": "block"
        }
    }
```

## 故障排查

### GitNexus 连接失败

```bash
# 检查 GitNexus 是否安装
gitnexus --version

# 检查 MCP 服务
gitnexus mcp
```

### Webhook 未触发

1. 检查 Webhook URL 是否正确
2. 检查分支是否在触发条件中
3. 查看日志：`docker logs ai-test-platform`

### 测试未执行

1. 检查 API Agent 是否正常
2. 检查端点是否在数据库中
3. 检查测试脚本是否生成

## 许可证

版权所有 (c) 2023-2026 北京慧测信息技术有限公司
