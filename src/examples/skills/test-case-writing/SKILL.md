---
name: test-case-writing
description: Writes detailed, executable test cases based on requirements analysis. Creates standardized test case documents with clear steps, expected results, and priorities. Use when the user asks to write test cases, create test scenarios, or generate test documentation.
---

# Test Case Writing Skill

## Writing Process

### Step 1: Read Requirements Analysis

Before writing test cases, read the requirements analysis file:

```
read_file test_[feature_name]/requirements_analysis.md
```

Understand all functional points, boundary conditions, and risk areas identified.

### Step 2: Design Test Cases

For each test point in the requirements analysis, create test cases covering:

**Test Case Types:**
- **Positive cases** - Valid inputs, normal flow
- **Negative cases** - Invalid inputs, error handling
- **Boundary cases** - Edge values, limit conditions
- **State transition cases** - Valid/invalid state changes

**Test Case Structure:**
| Field | Description |
|-------|-------------|
| 用例ID | Unique identifier (e.g., TC-LOGIN-001) |
| 模块 | Feature/module name |
| 标题 | Clear, concise description of what is being tested |
| 前置条件 | Setup required before executing the test |
| 测试步骤 | Numbered, actionable steps |
| 测试数据 | Specific input values (if applicable) |
| 预期结果 | Observable, verifiable expected outcome |
| 优先级 | P0 / P1 / P2 |
| 用例类型 | 正向 / 反向 / 边界 |

### Step 3: Write Test Cases to File

Create `test_[feature_name]/test_cases.md` with the following structure:

```markdown
# 测试用例 - [功能名称]

## 统计概览

| 统计项 | 数量 |
|--------|------|
| 总用例数 | [N] |
| P0用例 | [N] |
| P1用例 | [N] |
| P2用例 | [N] |
| 正向用例 | [N] |
| 反向用例 | [N] |
| 边界用例 | [N] |

---

## 用例详情

### 模块: [模块名称]

#### TC-[模块]-001: [用例标题]

| 字段 | 内容 |
|------|------|
| 用例ID | TC-[模块]-001 |
| 模块 | [模块名] |
| 标题 | [清晰描述] |
| 前置条件 | 1. [条件1]<br>2. [条件2] |
| 测试步骤 | 1. [步骤1]<br>2. [步骤2]<br>3. [步骤3] |
| 测试数据 | [数据，如有] |
| 预期结果 | 1. [结果1]<br>2. [结果2] |
| 优先级 | P0/P1/P2 |
| 用例类型 | 正向/反向/边界 |

---

#### TC-[模块]-002: [用例标题]
...
```

## Test Case Writing Guidelines

### Title Guidelines
- Be specific and descriptive
- Include the action and expected outcome
- Examples:
  - ✅ "使用有效用户名密码成功登录系统"
  - ❌ "测试登录功能"

### Step Guidelines
- Number each step (1, 2, 3...)
- One action per step
- Be specific about UI elements:
  - ✅ "点击右上角的【登录】按钮"
  - ❌ "点击登录"

### Expected Result Guidelines
- Must be observable and verifiable
- Include specific values when applicable
- Examples:
  - ✅ "页面跳转至首页，显示用户昵称'张三'"
  - ❌ "登录成功"

### Priority Assignment

| Priority | Assignment Criteria |
|----------|-------------------|
| **P0** | Core user journeys, critical business functions, blocking issues |
| **P1** | Important features, common user scenarios |
| **P2** | Edge cases, minor features, optimization scenarios |

## Best Practices

- **Traceability** - Each test case should map to a requirement
- **Independence** - Each test case should be executable independently
- **Repeatability** - Same inputs should always produce same results
- **Atomicity** - One test case tests one specific aspect
- **Clarity** - Anyone should be able to execute the test case without asking questions
