# 缺陷管理使用指南

## 📖 概述

缺陷管理功能支持**缺陷跟踪、外部系统集成（Jira/禅道）、AI根因分析**，提供完整的缺陷生命周期管理。

---

## 🎯 核心功能

### 1. 缺陷跟踪
- ✅ 完整的缺陷生命周期（新建→确认→分配→处理→解决→验证→关闭）
- ✅ 严重程度和优先级分类
- ✅ 模块和环境影响范围标记
- ✅ 重现步骤、预期结果、实际结果记录

### 2. 外部系统集成
- ✅ 支持Jira/禅道/TAPD/GitLab/GitHub
- ✅ 双向同步缺陷状态
- ✅ 字段映射配置

### 3. AI分析
- ✅ 自动分析根本原因
- ✅ 智能修复建议
- ✅ 相似缺陷推荐

---

## 🚀 快速开始

### 1. 创建缺陷

```bash
POST /api/v2/projects/{project_id}/defects

{
  "title": "登录功能失败",
  "description": "用户无法登录系统",
  "severity": "major",
  "priority": "high",
  "module": "登录模块",
  "environment": "测试环境",
  "steps_to_reproduce": "1. 打开登录页面\n2. 输入用户名密码\n3. 点击登录按钮",
  "expected_result": "登录成功并跳转到首页",
  "actual_result": "提示用户名或密码错误",
  "tags": ["登录", "P1"]
}
```

### 2. 更新状态

```bash
POST /api/v2/projects/{project_id}/defects/{defect_id}/status?new_status=assigned&comment=已分配给开发人员

# 状态流转
NEW → CONFIRMED → ASSIGNED → IN_PROGRESS → RESOLVED → VERIFIED → CLOSED
 ↓                                                 ↑
 └──────────── REOPENED ←──────────────────────────┘
```

### 3. 同步到Jira

```bash
POST /api/v2/projects/{project_id}/defects/{defect_id}/sync/jira

# 响应
{
  "success": true,
  "external_key": "BUG-123",
  "external_url": "https://jira.company.com/browse/BUG-123"
}
```

### 4. AI分析

```bash
POST /api/v2/projects/{project_id}/defects/{defect_id}/ai-analyze

# 响应
{
  "root_cause": "密码加密算法不一致导致验证失败",
  "suggested_fix": "统一使用bcrypt加密算法",
  "confidence": 0.92
}
```

---

## 📊 缺陷等级定义

### 严重程度

| 等级 | 说明 | 示例 |
|------|------|------|
| **Blocker** | 阻塞 | 系统崩溃、数据丢失 |
| **Critical** | 严重 | 核心功能无法使用 |
| **Major** | 主要 | 功能受损但可绕过 |
| **Normal** | 一般 | 功能可用但不完整 |
| **Minor** | 次要 | 界面问题、优化建议 |
| **Trivial** | 轻微 | 文案错误 |

### 优先级

| 优先级 | 处理时间 |
|--------|----------|
| **Urgent** | 立即 |
| **High** | 24小时内 |
| **Medium** | 本周内 |
| **Low** | 有空处理 |

---

## 🔧 外部系统配置

### 配置Jira集成

```python
# 创建Jira配置
config = ExternalSystemConfig(
    project_id=project_id,
    system_type=ExternalSystem.JIRA,
    api_url="https://jira.company.com/rest/api/2",
    username="your-username",
    password="your-password",  # 加密存储
    project_key="PROJECT",
    field_mapping={
        "severity": "priority",
        "module": "component"
    }
)
```

---

## 💡 最佳实践

### 1. 缺陷标题规范
```
【模块名】简要描述问题
示例：【登录】用户输入正确密码无法登录
```

### 2. 重现步骤格式
```
前置条件：已注册用户账号
步骤：
1. 打开 https://test.com/login
2. 输入用户名：test@example.com
3. 输入密码：password123
4. 点击"登录"按钮

预期：登录成功，跳转到首页
实际：提示"用户名或密码错误"
```

### 3. AI分析触发时机
- 创建缺陷后自动触发（可配置）
- 缺陷长时间未解决时手动触发
- 缺陷重开时触发

---

## 📈 统计分析

### 获取统计数据

```bash
GET /api/v2/projects/{project_id}/defects/statistics

# 响应
{
  "total": 25,
  "by_status": {
    "new": 5,
    "in_progress": 8,
    "resolved": 10,
    "closed": 2
  },
  "by_severity": {
    "blocker": 2,
    "critical": 5,
    "major": 10,
    "normal": 8
  }
}
```

---

## 🔄 典型工作流

### 开发人员工作流
```
1. 接收分配的缺陷（ASSIGNED）
2. 开始处理（IN_PROGRESS）
3. 修复完成后（RESOLVED）
4. 等待测试验证
```

### 测试人员工作流
```
1. 发现缺陷并创建（NEW）
2. 确认缺陷有效（CONFIRMED）
3. 验证修复（VERIFIED）
4. 关闭缺陷（CLOSED）
```

---

## 📝 相关功能

- **评论系统**：记录缺陷讨论过程
- **历史记录**：追踪所有变更
- **附件管理**：上传截图、日志文件
- **标签管理**：灵活分类

---

**更新时间**: 2026-06-10  
**维护者**: AI测试平台团队