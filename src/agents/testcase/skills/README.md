# 测试用例生成智能体 Skills 总览

本目录包含测试用例生成智能体的全部 Skill 模块，覆盖从需求分析到最终输出的完整工作流程。

---

## Skills 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    测试用例生成工作流程                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: 需求分析        ┌──────────────────┐              │
│  ───────────────────────> │ requirements-    │              │
│  输入: PRD/文档/描述       │ analysis         │              │
│  输出: 需求解析报告        │ (需求分析)        │              │
│                           └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│  Phase 2: 测试策略        │ test-strategy    │              │
│  ───────────────────────> │ (测试策略)        │              │
│  输入: 需求解析报告        │                  │              │
│  输出: 测试策略文档        └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│  Phase 3: 用例设计        │ test-design      │              │
│  ───────────────────────> │ (用例设计)        │              │
│  输入: 测试策略            │                  │              │
│  输出: 测试用例            └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│  Phase 4: 数据构造        │ test-data        │              │
│  ───────────────────────> │ (测试数据)        │              │
│  输入: 用例框架            │                  │              │
│  输出: 完整用例（含数据）   └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│  Phase 5: 质量评审        │ quality-review   │              │
│  ───────────────────────> │ (质量评审)        │              │
│  输入: 完整用例            │                  │              │
│  输出: 质量报告            └────────┬─────────┘              │
│                                    │                        │
│                                    ▼                        │
│                           ┌──────────────────┐              │
│  输出阶段                 │ output-formatter │              │
│  ───────────────────────> │ (输出格式)        │              │
│  输入: 已评审用例          │                  │              │
│  输出: Markdown/Excel/JSON └──────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Skills 清单

| Skill | 名称 | 职责 | 触发条件 |
|-------|------|------|----------|
| [requirements-analysis](./requirements-analysis/SKILL.md) | 需求分析 | 解析需求文档，提取功能模块、业务流程、风险点 | 收到任何需求输入 |
| [test-strategy](./test-strategy/SKILL.md) | 测试策略 | 制定测试类型、测试深度、优先级分布策略 | Phase 1 完成后 |
| [test-design](./test-design/SKILL.md) | 用例设计 | 运用六大设计技术生成测试用例 | Phase 2 完成后 |
| [test-data](./test-data/SKILL.md) | 测试数据 | 构造有效/边界/无效/安全测试数据 | Phase 3 完成后 |
| [quality-review](./quality-review/SKILL.md) | 质量评审 | 10项自检、质量评分、问题清单 | Phase 4 完成后 |
| [output-formatter](./output-formatter/SKILL.md) | 输出格式 | 多格式输出（Markdown/Excel/JSON） | 用户要求导出时 |

---

## 使用方式

### 完整流程（自动生成）

当用户要求"生成测试用例"时，智能体会自动按以下流程执行：

1. **requirements-analysis**: 分析需求 → 输出需求解析报告
2. **test-strategy**: 制定策略 → 输出测试策略文档
3. **test-design**: 设计用例 → 输出测试用例（Markdown）
4. **test-data**: 补充数据 → 完善测试数据
5. **quality-review**: 质量评审 → 输出评审报告
6. **output-formatter**: 按用户要求格式输出

### 单 Skill 调用（定向使用）

用户明确指定某项能力时：

```
"帮我分析这个需求"          → 激活 requirements-analysis
"制定测试策略"              → 激活 test-strategy
"为登录功能设计测试用例"     → 激活 test-design
"构造一些测试数据"          → 激活 test-data
"评审这些测试用例"          → 激活 quality-review
"导出为 Excel"             → 激活 output-formatter
```

---

## 核心原则

### 1. 顺序执行
Skills 有明确的依赖关系，原则上按 Phase 1→5 顺序执行，前一阶段输出作为后一阶段输入。

### 2. 强制检查点
- Phase 1 未完成前，禁止进入 Phase 2
- Phase 5 质量评审不通过，需返回修改

### 3. 用户确认机制
- Phase 1 完成后需用户确认需求理解
- Phase 2 完成后需用户确认测试策略

### 4. 输出规范
所有 Skill 的输出必须符合 `output-formatter` 定义的格式规范。

---

## 扩展开发

如需新增 Skill：

1. 在 `skills/` 目录下新建子目录
2. 创建 `SKILL.md` 文件，包含：
   - Frontmatter（name, description）
   - 激活场景
   - 执行流程
   - 输入/输出格式
3. 在 `agent.py` 的 SYSTEM_PROMPT 中引用新 Skill
4. 更新本 README

---

## 依赖关系

```
requirements-analysis
        │
        ▼
test-strategy
        │
        ▼
test-design ◄──── test-data（辅助）
        │
        ▼
quality-review
        │
        ▼
output-formatter
```

---

## 版本信息

- **Version**: 1.0.0
- **Created**: 2026-04-03
- **Author**: AI Assistant
- **Description**: 企业级测试用例生成智能体 Skill 体系
