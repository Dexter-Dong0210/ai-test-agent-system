---
name: test-case-review
description: Reviews test cases for completeness, executability, coverage, and quality. Identifies gaps, inconsistencies, and improvement opportunities. Use when the user asks to review test cases, check test quality, or validate test coverage.
---

# Test Case Review Skill

## Review Process

### Step 1: Read Test Cases

Read the test case file to be reviewed:

```
read_file test_[feature_name]/test_cases.md
```

Also read the requirements analysis for reference:

```
read_file test_[feature_name]/requirements_analysis.md
```

### Step 2: Evaluate Against Checklist

Review each test case against the following criteria:

#### Completeness Check
| Check Item | Pass Criteria |
|------------|---------------|
| 用例ID | 唯一且格式规范 |
| 标题 | 清晰描述测试内容 |
| 前置条件 | 完整且可准备 |
| 测试步骤 | 编号清晰，可操作 |
| 预期结果 | 明确可验证 |
| 优先级 | P0/P1/P2正确标注 |

#### Quality Check
| Check Item | Pass Criteria |
|------------|---------------|
| 步骤描述 | 具体，无歧义 |
| 预期结果 | 可观察，可验证 |
| 测试数据 | 具体值，非模糊描述 |
| 标题描述 | 包含动作和预期结果 |

#### Coverage Check
| Check Item | Pass Criteria |
|------------|---------------|
| 需求覆盖 | 每个需求点都有对应用例 |
| 场景覆盖 | 正向、反向、边界都有覆盖 |
| 优先级分布 | P0核心功能全覆盖 |

### Step 3: Write Review Report

Create `test_[feature_name]/review_report.md`:

```markdown
# 测试用例评审报告 - [功能名称]

## 评审概览

| 评审项 | 结果 |
|--------|------|
| 评审日期 | [日期] |
| 总用例数 | [N] |
| 通过用例 | [N] |
| 需修改用例 | [N] |
| 评审结论 | 通过/有条件通过/不通过 |

## 详细评审结果

### 问题汇总

| 序号 | 用例ID | 问题类型 | 问题描述 | 严重程度 | 建议修改 |
|------|--------|----------|----------|----------|----------|
| 1 | TC-XXX-001 | [类型] | [描述] | 高/中/低 | [建议] |

### 问题分类统计

| 问题类型 | 数量 |
|----------|------|
| 描述不清晰 | [N] |
| 缺少预期结果 | [N] |
| 步骤不可执行 | [N] |
| 缺少边界场景 | [N] |
| 优先级不合理 | [N] |

## 用例质量评分

| 评分维度 | 满分 | 得分 | 说明 |
|----------|------|------|------|
| 完整性 | 25 | [N] | |
| 可执行性 | 25 | [N] | |
| 覆盖度 | 25 | [N] | |
| 规范性 | 25 | [N] | |
| **总分** | **100** | **[N]** | |

## 改进建议

1. [建议1]
2. [建议2]
3. [建议3]

## 评审结论

[通过/有条件通过/不通过]

[详细说明]
```

## Review Checklist Detail

### Completeness Items

| # | Check Item | Description |
|---|------------|-------------|
| 1 | 用例ID规范 | 格式统一，如 TC-MODULE-001 |
| 2 | 标题完整 | 动作 + 预期结果 |
| 3 | 前置条件完整 | 环境、数据、状态准备 |
| 4 | 步骤编号 | 使用 1, 2, 3... 编号 |
| 5 | 预期结果明确 | 具体、可验证的描述 |
| 6 | 优先级合理 | P0/P1/P2 分类正确 |

### Quality Items

| # | Check Item | Description |
|---|------------|-------------|
| 1 | 步骤具体 | 明确指出操作对象 |
| 2 | 无歧义 | 描述清晰无多种理解 |
| 3 | 数据具体 | 使用具体值而非"有效数据" |
| 4 | 结果可测 | 能够明确判断是否通过 |

### Coverage Items

| # | Check Item | Description |
|---|------------|-------------|
| 1 | 需求全覆盖 | 所有需求点有对应用例 |
| 2 | 正向覆盖 | 正常流程有覆盖 |
| 3 | 反向覆盖 | 异常处理有覆盖 |
| 4 | 边界覆盖 | 边界值、极限值有覆盖 |
| 5 | P0完整性 | 核心功能100%覆盖 |

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **高** | 阻塞性问题，无法执行或重大遗漏 | 必须修复 |
| **中** | 影响质量，但可以执行 | 建议修复 |
| **低** |  minor improvements | 可选修复 |

## Best Practices

- **Objective review** - Base comments on standards, not personal preference
- **Constructive feedback** - Provide specific improvement suggestions
- **Prioritize issues** - Focus on high-severity issues first
- **Trace to requirements** - Ensure each requirement has test coverage
