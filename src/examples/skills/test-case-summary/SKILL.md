---
name: test-case-summary
description: Generates comprehensive test case summary reports including statistics, priority distribution, and risk analysis. Use when the user asks for test case statistics, summary report, or quality assessment.
---

# Test Case Summary Skill

## Summary Process

### Step 1: Read All Test Files

Read the completed test case file and review report:

```
read_file test_[feature_name]/test_cases.md
read_file test_[feature_name]/review_report.md
```

### Step 2: Analyze and Statistics

Extract and calculate the following metrics:

#### Priority Distribution
| Priority | Count | Percentage | Description |
|----------|-------|------------|-------------|
| P0 | [N] | [N%] | 核心功能，必须100%执行 |
| P1 | [N] | [N%] | 重要功能，建议全量执行 |
| P2 | [N] | [N%] | 一般功能，选择性执行 |
| **Total** | **[N]** | **100%** | |

#### Test Type Distribution
| Type | Count | Percentage |
|------|-------|------------|
| 正向用例 | [N] | [N%] |
| 反向用例 | [N] | [N%] |
| 边界用例 | [N] | [N%] |
| **Total** | **[N]** | **100%** |

#### Module Distribution
| Module | P0 | P1 | P2 | Total |
|--------|----|----|----|-------|
| [模块1] | [N] | [N] | [N] | [N] |
| [模块2] | [N] | [N] | [N] | [N] |
| **Total** | **[N]** | **[N]** | **[N]** | **[N]** |

### Step 3: Generate Summary Report

Create `test_[feature_name]/test_summary.md`:

```markdown
# 测试用例总结报告 - [功能名称]

## 1. 测试范围概述

### 1.1 功能描述
[描述被测功能的主要内容和业务范围]

### 1.2 测试目标
[说明本次测试的主要目标和关注点]

### 1.3 测试范围
- **包含范围**: [列出包含的功能点]
- **排除范围**: [列出不包含的功能点]

---

## 2. 用例统计

### 2.1 总体统计

| 统计项 | 数量 | 占比 |
|--------|------|------|
| 总用例数 | [N] | 100% |
| P0用例 | [N] | [N%] |
| P1用例 | [N] | [N%] |
| P2用例 | [N] | [N%] |

### 2.2 按类型统计

| 类型 | 数量 | 占比 |
|------|------|------|
| 正向用例 | [N] | [N%] |
| 反向用例 | [N] | [N%] |
| 边界用例 | [N] | [N%] |

### 2.3 按模块统计

| 模块 | P0 | P1 | P2 | 合计 |
|------|----|----|----|------|
| [模块1] | [N] | [N] | [N] | [N] |
| [模块2] | [N] | [N] | [N] | [N] |
| **合计** | **[N]** | **[N]** | **[N]** | **[N]** |

---

## 3. 优先级分布分析

### 3.1 P0用例分析

**数量**: [N]个，占总用例的[N]%

**覆盖范围**:
- [核心功能点1]
- [核心功能点2]

**执行要求**: 必须100%执行通过，任一场景失败阻塞发布

### 3.2 P1用例分析

**数量**: [N]个，占总用例的[N]%

**覆盖范围**:
- [重要功能点1]
- [重要功能点2]

**执行要求**: 建议全量执行，失败不阻塞发布

### 3.3 P2用例分析

**数量**: [N]个，占总用例的[N]%

**覆盖范围**:
- [一般功能点1]
- [优化类场景]

**执行要求**: 选择性执行，建议修复但不强制

---

## 4. 测试覆盖评估

### 4.1 覆盖度评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能覆盖 | [N]/100 | |
| 场景覆盖 | [N]/100 | |
| 边界覆盖 | [N]/100 | |
| 异常覆盖 | [N]/100 | |
| **综合评分** | **[N]/100** | |

### 4.2 覆盖亮点

1. [亮点1]
2. [亮点2]

### 4.3 覆盖不足

1. [不足1]
2. [不足2]

---

## 5. 风险评估与建议

### 5.1 风险识别

| 风险等级 | 描述 | 影响 | 缓解措施 |
|----------|------|------|----------|
| 高 | [风险1] | [影响] | [措施] |
| 中 | [风险2] | [影响] | [措施] |
| 低 | [风险3] | [影响] | [措施] |

### 5.2 测试执行建议

1. **执行顺序**: 建议按 P0 → P1 → P2 的顺序执行
2. **回归范围**: 代码变更影响以下模块时，需执行对应P0用例
3. **自动化建议**: 以下P0用例建议自动化

### 5.3 资源估算

| 执行范围 | 用例数 | 估算工时 |
|----------|--------|----------|
| P0全量 | [N] | [N]人日 |
| P0+P1 | [N] | [N]人日 |
| 全量 | [N] | [N]人日 |

---

## 6. 附件

- [需求分析文档](requirements_analysis.md)
- [测试用例文档](test_cases.md)
- [用例评审报告](review_report.md)

---

报告生成时间: [日期]
报告生成人: 测试专家Agent
```

## Priority Distribution Guidelines

### Ideal Distribution
| Priority | Target Range | Description |
|----------|--------------|-------------|
| P0 | 20-30% | Core critical paths |
| P1 | 40-50% | Important features |
| P2 | 20-30% | Edge cases and enhancements |

### Warning Signs
| Issue | Threshold | Action |
|-------|-----------|--------|
| P0占比过高 | >40% | 重新评估优先级定义 |
| P0占比过低 | <10% | 可能存在遗漏核心场景 |
| 无P0用例 | 0% | 必须补充核心功能用例 |

## Best Practices

- **Data-driven** - Base analysis on actual test case data
- **Visual-friendly** - Use tables and charts for statistics
- **Actionable insights** - Provide specific recommendations
- **Risk-focused** - Highlight risks and mitigation strategies
- **Time-aware** - Provide execution time estimates
