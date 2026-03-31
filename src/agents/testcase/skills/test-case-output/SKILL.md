---
name: test-case-output
description: Produces final test case deliverables in multiple formats (Markdown report, JSON, CSV, and automation-ready templates) based on reviewed test cases, review report, and upstream artifacts. Ensures traceability, quality metrics, and execution readiness are preserved in the final output. Use as the final step in the test case generation pipeline.
compatibility: Requires filesystem access to read markdown files and write output files. No external network dependencies.
metadata:
  version: "1.0.0"
  author: "Test Agent System"
  domain: "software-testing"
  stage: "05-test-case-output"
---

# 用例输出技能 (Test Case Output Skill)

## 技能目标
整合经过评审的测试用例、评审报告及上游需求分析、测试点清单，生成面向不同受众和使用场景的最终交付物。确保交付物具备完整的追踪关系、可量化的质量指标、明确的执行指引，并支持手工执行、测试管理工具导入、自动化脚本对接等多种下游使用方式。

## 适用场景 / 不适用场景

**适用场景：**
- 测试用例已通过评审，需要生成正式交付文档
- 需要将用例导出为不同格式（Markdown报告、JSON、CSV/Excel）
- 需要为自动化团队提供用例框架或数据驱动文件
- 需要向项目干系人汇报测试范围、质量状态和资源配置

**不适用场景：**
- 用例尚未完成评审或评审结论为"不通过"（应先修复用例并重新评审）
- 仅需查看原始用例文档，无需整合报告
- 需要直接对接特定测试管理系统的API（本技能输出标准格式文件，API对接由外部脚本完成）

## 输入定义

### 必填项
| 字段 | 数据格式 | 说明 | 示例 |
|------|----------|------|------|
| `feature_name` | 字符串 | 功能标识 | `user_login` |
| `test_cases_file` | 文件路径 | 测试用例文档 | `test_user_login/03_test_cases.md` |
| `review_report_file` | 文件路径 | 评审报告 | `test_user_login/04_review_report.md` |

### 可选项
| 字段 | 数据格式 | 说明 | 示例 |
|------|----------|------|------|
| `output_formats` | 字符串列表 | 输出格式列表 | `["markdown", "json", "csv"]` |
| `include_automation_template` | 布尔值 | 是否输出自动化模板 | `true` |
| `automation_framework` | 枚举 | 自动化框架：pytest / robot / selenium / playwright | `pytest` |
| `report_language` | 枚举 | 报告语言：zh / en / bilingual | `zh` |
| `delivery_audience` | 枚举 | 交付受众：test_team / management / automation_team / all | `all` |

## 输出定义

### 输出文件清单
| 文件路径 | 格式 | 用途 |
|----------|------|------|
| `test_{feature_name}/05_delivery_report.md` | Markdown | 面向测试团队和管理层的完整交付报告 |
| `test_{feature_name}/05_test_cases.json` | JSON | 结构化数据，供工具和自动化对接 |
| `test_{feature_name}/05_test_cases.csv` | CSV | 供Excel/TestRail等工具导入 |
| `test_{feature_name}/05_automation_template.py` | Python | 自动化测试脚本框架（可选） |

### 结构化格式（Markdown交付报告）
```markdown
# 测试用例交付报告 - {feature_name}

## 元信息
| 字段 | 值 |
|------|-----|
| 功能名称 | 用户登录 |
| 版本 | v1.0 |
| 交付日期 | YYYY-MM-DD |
| 评审结论 | 通过 |
| 质量总分 | 88.9 |
| 交付受众 | 测试团队 / 管理层 / 自动化团队 |

## 1. 交付物清单
- [测试用例文档](03_test_cases.md) — 详细执行用例
- [测试用例JSON](05_test_cases.json) — 结构化数据
- [测试用例CSV](05_test_cases.csv) — 表格格式
- [自动化模板](05_automation_template.py) — pytest框架脚本框架
- [需求分析文档](01_requirements_analysis.md) — 原始需求分析
- [测试点清单](02_test_points.md) — 测试点提取结果
- [评审报告](04_review_report.md) — 质量评审详情

## 2. 执行摘要

### 2.1 测试范围
- **包含范围**：手机号验证码登录、登录状态保持、异常提示
- **排除范围**：第三方OAuth登录、生物识别登录

### 2.2 用例统计
| 统计项 | 数量 | 占比 |
|--------|------|------|
| 总用例数 | 12 | 100% |
| P0用例 | 4 | 33.3% |
| P1用例 | 5 | 41.7% |
| P2用例 | 3 | 25.0% |
| 正向用例 | 4 | 33.3% |
| 反向用例 | 4 | 33.3% |
| 边界用例 | 3 | 25.0% |
| 异常用例 | 1 | 8.3% |

### 2.3 质量状态
- **评审结论**：通过
- **质量总分**：88.9/100
- **已知问题**：2个中等问题（详见评审报告第3节），无阻塞性问题
- **覆盖状态**：100% REQ覆盖，100% TP覆盖

### 2.4 执行建议
1. **执行顺序**：P0 → P1 → P2
2. **回归范围**：任何涉及登录接口、验证码服务、会话管理的代码变更，需全量执行P0用例
3. **自动化建议**：P0用例中的正向场景建议优先自动化（已提供pytest模板）
4. **资源估算**：P0全量约0.5人日；全量执行约1.5人日

## 3. 需求追踪总览
| 需求ID | 需求描述 | 覆盖用例数 | 覆盖状态 |
|--------|----------|------------|----------|
| REQ-001 | 手机号验证码登录 | 4 | 已覆盖 |
| REQ-002 | 登录状态保持 | 2 | 已覆盖 |
| REQ-003 | 异常提示 | 3 | 已覆盖 |

## 4. 风险与注意事项
| 风险等级 | 描述 | 影响 | 缓解措施 |
|----------|------|------|----------|
| 中 | 测试账号需提前申请 | 可能阻塞执行 | 建议提前1个工作日准备测试账号 |
| 低 | 短信网关测试环境不稳定 | 偶发失败 | 失败用例需结合网关日志二次确认 |

## 5. 格式说明与使用指南

### 5.1 Markdown用例文档
适合手工执行和评审会议使用，包含完整的步骤、数据和预期结果。

### 5.2 JSON格式
包含完整的用例字段和元数据，适合对接测试管理平台或CI/CD流水线。
结构示例：
```json
{
  "feature": "user_login",
  "cases": [
    {
      "case_id": "TC-LOGIN-001",
      "title": "使用有效手机号和正确验证码成功登录",
      "priority": "P0",
      "type": "正向",
      "source_req": ["REQ-001"],
      "source_tp": "TP-001",
      "preconditions": [...],
      "steps": [...],
      "expected_results": [...],
      "test_data": {...}
    }
  ]
}
```

### 5.3 CSV格式
包含用例ID、标题、优先级、类型、来源需求、来源测试点、前置条件摘要、步骤摘要、预期结果摘要，适合在Excel中快速浏览和筛选。

### 5.4 自动化模板
提供基于 `{automation_framework}` 的脚本框架，包含：
- 用例函数占位符（与用例ID一一对应）
- 数据驱动参数化示例
- 断言模板
- 注释中标注的来源需求和预期结果

---

报告生成时间: YYYY-MM-DD
报告生成人: 测试专家Agent
```

### JSON格式结构
```json
{
  "metadata": {
    "feature_name": "user_login",
    "version": "v1.0",
    "delivery_date": "YYYY-MM-DD",
    "review_status": "通过",
    "quality_score": 88.9
  },
  "statistics": {
    "total": 12,
    "p0": 4,
    "p1": 5,
    "p2": 3,
    "positive": 4,
    "negative": 4,
    "boundary": 3,
    "exception": 1
  },
  "traceability": [
    {
      "req_id": "REQ-001",
      "req_desc": "手机号验证码登录",
      "case_ids": ["TC-LOGIN-001", "TC-LOGIN-002"]
    }
  ],
  "cases": [ ... ]
}
```

### CSV格式列定义
`用例ID,模块,标题,优先级,类型,来源需求,来源测试点,前置条件,测试步骤,预期结果,清理步骤,备注`

## 执行步骤

### Step 1: 读取上游文档
读取 `03_test_cases.md`、`04_review_report.md`，以及 `02_test_points.md` 和 `01_requirements_analysis.md`（用于补充追踪信息）。

### Step 2: 解析与整合
1. 提取所有用例的完整字段
2. 提取评审结论、质量评分、问题清单、改进建议
3. 构建需求追踪总览表（REQ → 用例列表）
4. 构建测试点追踪总览表（TP → 用例列表）

### Step 3: 生成交付报告（Markdown）
根据 `delivery_audience` 调整报告侧重点：
- `test_team`：侧重用例详情、执行建议、已知问题
- `management`：侧重统计图表、质量评分、风险与资源估算
- `automation_team`：侧重JSON/CSV结构、自动化模板、数据驱动说明
- `all`：生成完整综合报告

### Step 4: 生成结构化数据（JSON）
将用例、统计、追踪关系、元信息输出为规范的JSON文件，确保字段名统一、无嵌套歧义。

### Step 5: 生成表格数据（CSV）
将用例核心字段平铺为CSV，使用 `"` 包裹包含逗号或换行的单元格，确保Excel可直接打开。

### Step 6: 生成自动化模板（可选）
若 `include_automation_template=true`，根据 `automation_framework` 生成对应的脚本框架：
- **pytest**：生成 `test_{feature}.py`，包含 `@pytest.mark.parametrize` 示例和断言模板
- **robot**：生成 `{feature}.robot` 文件框架
- **selenium/playwright**：生成页面对象模式（POM）的测试类框架

### Step 7: 输出所有文件
将生成的文件写入 `test_{feature_name}/` 目录，并在交付报告中列出完整交付物清单。

## 质量门禁 (DoD)

| 检查项 | 验收标准 | 检查方式 |
|--------|----------|----------|
| 交付完整性 | 至少输出 Markdown报告 + JSON + CSV 三种格式 | 文件存在性检查 |
| 数据一致性 | JSON/CSV中的用例数、优先级分布与Markdown报告一致 | 交叉核对 |
| 追踪关系完整 | 交付报告中包含 REQ→用例 的完整映射 | 文档审查 |
| 评审结论引用 | 交付报告中明确引用评审结论和质量评分 | 关键词扫描 |
| 可执行性保障 | 交付报告中包含执行顺序、回归范围、资源估算 | 文档审查 |
| 自动化模板可用 | 自动化模板文件可直接被对应框架解析（无语法错误） | 静态检查 |

## 异常与边界处理

| 异常场景 | 处理策略 |
|----------|----------|
| 评审结论为"不通过" | 在交付报告首页添加 **红色警告区块**，说明"本用例集评审未通过，不建议直接用于生产测试执行"，但仍输出所有格式文件供修复参考 |
| 用例文档中存在格式解析错误 | 跳过该用例并在交付报告的"数据质量说明"中标注，确保其他用例正常输出 |
| 评审报告缺失部分维度评分 | 在交付报告中标注"部分评审数据缺失"，使用可用数据生成报告 |
| CSV中出现特殊字符（换行、逗号、引号） | 严格遵循 RFC 4180 进行转义：字段含特殊字符时用双引号包裹，内部双引号转义为两个双引号 |
| 自动化框架不支持 | 在模板文件中添加注释说明框架限制，并生成最接近的通用模板 |

## 与上下游技能的衔接规则

### 输入来源
- **上游技能**：`test-case-review`、`test-case-writing`、`test-point-extraction`、`requirements-analysis`
- **输入文件**：`04_review_report.md`、`03_test_cases.md`、`02_test_points.md`、`01_requirements_analysis.md`

### 输出去向
- 无下游技能（本技能为流程终点）
- 输出文件供外部系统（测试管理平台、CI/CD、Excel）消费

### 字段映射
| 上游输出字段 | 本技能输入字段 | 说明 |
|--------------|----------------|------|
| `评审结论` | `review_status` | 决定交付策略和警告级别 |
| `质量评分` | `quality_score` | 写入交付报告元信息 |
| `问题清单` | `issue_list` | 在交付报告中转化为"已知问题" |
| `用例详情` | `cases` | 转化为JSON/CSV/报告的核心数据 |
| `RTM` | `traceability` | 生成需求追踪总览 |

## 复用与扩展点

- **模板资产库**：在 `assets/` 目录下维护不同自动化框架的模板文件（pytest、robot、playwright、selenium）
- **企业报表样式**：可在 `assets/` 中维护企业Logo、标准配色、页眉页脚的Markdown模板片段
- **多语言扩展**：通过 `report_language` 支持中英文/双语报告，语言包可放在 `references/i18n.md`
- **测试管理工具映射**：在 `references/` 下维护 TestRail、Jira Xray、禅道等工具的字段映射表，便于外部脚本转换
- **CI/CD对接**：JSON输出可扩展 `ci_metadata` 字段（如测试套件标签、流水线stage名称）
