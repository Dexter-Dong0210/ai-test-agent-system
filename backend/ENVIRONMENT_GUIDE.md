# 测试环境管理使用指南

## 📖 概述

测试环境管理功能提供**多环境配置、动态切换、健康检查**能力，解决测试过程中环境配置混乱的问题。

---

## 🎯 核心功能

### 1. 多环境管理
- ✅ 支持**开发/测试/预发布/生产/沙箱**5种环境类型
- ✅ 每个项目可配置多个环境
- ✅ 环境配置加密存储（数据库密码、Token等）

### 2. 环境切换
- ✅ 一键切换默认环境
- ✅ 记录使用历史（谁在什么时候切换了环境）
- ✅ 统计使用频率

### 3. 健康检查
- ✅ 定时检查环境可用性
- ✅ 记录响应时间、状态码
- ✅ 异常自动告警

### 4. 配置管理
- ✅ 克隆环境配置
- ✅ 导出/导入配置（JSON格式）
- ✅ 环境变量管理

---

## 🚀 快速开始

### 1. 创建环境

```bash
POST /api/v2/projects/{project_id}/environments

{
  "name": "测试环境",
  "code": "TEST",
  "base_url": "https://api.test.com",
  "env_type": "testing",
  "auth_type": "token",
  "auth_config": {
    "token": "your-api-token"
  },
  "health_check_url": "https://api.test.com/health",
  "variables": {
    "API_VERSION": "v1",
    "TIMEOUT": "30"
  }
}
```

### 2. 切换环境

```bash
POST /api/v2/projects/{project_id}/environments/{env_id}/switch

# 响应
{
  "success": true,
  "message": "环境已切换为默认环境"
}
```

### 3. 健康检查

```bash
POST /api/v2/projects/{project_id}/environments/{env_id}/health-check

# 响应
{
  "status": "healthy",
  "response_time": 125,
  "status_code": 200,
  "checked_at": "2026-06-10T19:30:00Z"
}
```

---

## 📋 环境配置说明

### 环境类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| **development** | 开发环境 | 开发自测 |
| **testing** | 测试环境 | 功能测试 |
| **staging** | 预发布环境 | 上线前验证 |
| **production** | 生产环境 | 生产数据测试 |
| **sandbox** | 沙箱环境 | 外部系统联调 |

### 认证配置

#### Token认证
```json
{
  "auth_type": "token",
  "auth_config": {
    "token": "Bearer xxxxx"
  }
}
```

#### Basic Auth
```json
{
  "auth_type": "basic",
  "auth_config": {
    "username": "user",
    "password": "pass"
  }
}
```

#### OAuth2
```json
{
  "auth_type": "oauth2",
  "auth_config": {
    "client_id": "xxx",
    "client_secret": "xxx",
    "token_url": "https://auth.com/token"
  }
}
```

---

## 💡 使用示例

### Python调用

```python
from app.services.environment_service import EnvironmentService

service = EnvironmentService(session)

# 创建环境
env = await service.create_environment(
    project_id=project_id,
    name="测试环境",
    code="TEST",
    base_url="https://api.test.com",
    env_type=EnvironmentType.TESTING
)

# 切换环境
await service.switch_environment(project_id, env.id, user_id)

# 健康检查
health = await service.health_check(env.id)
```

### 前端集成

```typescript
// 获取环境列表
const response = await fetch('/api/v2/projects/TEST-001/environments');
const environments = await response.json();

// 切换环境
await fetch(`/api/v2/projects/TEST-001/environments/${envId}/switch`, {
  method: 'POST'
});

// 健康检查
const health = await fetch(
  `/api/v2/projects/TEST-001/environments/${envId}/health-check`,
  { method: 'POST' }
).then(r => r.json());
```

---

## 🔧 高级功能

### 1. 克隆环境

```bash
POST /api/v2/projects/{id}/environments/{env_id}/clone?new_name=新环境&new_code=NEW

# 用途：快速创建相似环境的配置
```

### 2. 导出/导入

```python
# 导出
config = await service.export_config(env_id)

# 导入
new_env = await service.import_config(project_id, config)
```

---

## 🎯 最佳实践

### 1. 环境命名规范
```
推荐格式：{项目名}-{环境类型}-{序号}
示例：ORDER-API-TESTING-01
```

### 2. 敏感信息管理
- 使用环境变量存储敏感信息
- 定期更换Token/密码
- 不要在前端暴露生产环境Token

### 3. 健康检查频率
- 开发环境：5分钟
- 测试环境：3分钟
- 生产环境：1分钟

---

## 📊 环境使用统计

系统自动记录：
- 环境使用次数
- 最后使用时间
- 最后使用用户

可用于分析：
- 环境利用率
- 用户偏好
- 资源规划

---

**更新时间**: 2026-06-10  
**维护者**: AI测试平台团队