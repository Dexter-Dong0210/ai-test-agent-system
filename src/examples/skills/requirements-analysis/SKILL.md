---
name: requirements-analysis
description: Analyzes testing requirements for a given feature or user story, identifying functional points, business rules, boundary conditions, and risk areas. Use when the user asks to analyze test requirements, identify test points, or understand what needs to be tested.
---

# Requirements Analysis Skill

## Analysis Process

### Step 1: Create Test Project Folder

Before starting analysis, create a dedicated folder:

```
mkdir test_[feature_name]
```

This keeps all test-related files organized in one location.

### Step 2: Analyze Testing Requirements

Break down the input (feature description, user story, or PRD) into:

**Functional Requirements:**
- Core functionality - essential features that must work
- Secondary functionality - supporting features
- User workflows - end-to-end user journeys
- Data flows - input processing and output generation

**Non-Functional Requirements:**
- Performance expectations (response time, throughput)
- Security considerations (authentication, authorization, data protection)
- Compatibility (browsers, devices, OS versions)
- Usability and accessibility

**Boundary Conditions:**
- Input limits (min/max length, value ranges)
- State transitions (valid/invalid state changes)
- Concurrent access scenarios
- Error handling and recovery

### Step 3: Write Requirements Analysis Document

Create `test_[feature_name]/requirements_analysis.md` containing:

```markdown
# 测试需求分析 - [功能名称]

## 1. 需求概述
- 功能描述
- 业务价值
- 用户场景

## 2. 功能测试点清单

### 2.1 核心功能
| 序号 | 测试点 | 优先级 | 备注 |
|------|--------|--------|------|
| 1 | [具体测试点] | P0 | |

### 2.2 次要功能
| 序号 | 测试点 | 优先级 | 备注 |
|------|--------|--------|------|
| 1 | [具体测试点] | P1 | |

## 3. 非功能测试点清单

### 3.1 性能测试
- [性能测试点]

### 3.2 安全测试
- [安全测试点]

### 3.3 兼容性测试
- [兼容性测试点]

## 4. 边界条件和异常场景

| 场景类型 | 描述 | 预期行为 |
|----------|------|----------|
| 边界值 | [描述] | [预期] |
| 异常输入 | [描述] | [预期] |
| 状态异常 | [描述] | [预期] |

## 5. 风险点和注意事项

| 风险等级 | 描述 | 缓解措施 |
|----------|------|----------|
| 高 | [风险描述] | [措施] |
```

## Best Practices

- **Comprehensive coverage** - Consider both happy path and edge cases
- **Clear priorities** - Mark P0/P1/P2 for each test point
- **Specific details** - Include concrete examples, not vague descriptions
- **File-based output** - Always save analysis to a file for downstream use
- **Risk awareness** - Highlight potential risks and dependencies

## Priority Definitions

| Priority | Description | When to Use |
|----------|-------------|-------------|
| **P0** | Core functionality, blocking issues | Features that block release if broken |
| **P1** | Important functionality, non-blocking | Features that should work but don't block |
| **P2** | Nice-to-have, optimization | Enhancement features, minor issues |
