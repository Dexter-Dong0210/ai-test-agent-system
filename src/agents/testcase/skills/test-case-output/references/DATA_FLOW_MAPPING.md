# 技能间数据流与字段映射表

## 总体流程

```
[原始需求] 
    ↓
requirements-analysis → 01_requirements_analysis.md
    ↓
test-point-extraction → 02_test_points.md
    ↓
test-case-writing     → 03_test_cases.md
    ↓
test-case-review      → 04_review_report.md
    ↓
test-case-output      → 05_delivery_report.md + JSON + CSV + 自动化模板
    ↓ [可选]
test-case-excel-export → 06_test_cases.xlsx (Excel工作簿)
```

## 阶段一：requirements-analysis → test-point-extraction

| 输出字段（需求分析） | 输入字段（测试点提取） | 说明 |
|----------------------|------------------------|------|
| `feature_name` | `feature_name` | 功能标识，用于文件夹命名 |
| `01_requirements_analysis.md` | `requirements_analysis_file` | 完整的需求分析文档路径 |
| `REQ-NNN` | `source_req_id` | 测试点必须引用来源需求ID |
| `BR-NNN` | `source_rule_id` | 测试点可引用业务规则ID |
| `风险与假设` | `risk_assumptions` | 用于测试点优先级调整 |
| `版本` | `version` | 保持版本一致性 |

## 阶段二：test-point-extraction → test-case-writing

| 输出字段（测试点提取） | 输入字段（用例编写） | 说明 |
|------------------------|----------------------|------|
| `feature_name` | `feature_name` | 功能标识 |
| `02_test_points.md` | `test_points_file` | 测试点清单文件路径 |
| `TP-NNN` | `source_tp_id` | 用例必须引用来源测试点ID |
| `测试类型` | `case_type` | 用例类型继承测试点类型 |
| `优先级` | `priority` | 用例优先级默认继承测试点优先级 |
| `测试点描述` | `test_intent` | 用例标题和意图的来源 |
| `关键输入` | `suggested_data` | 用例测试数据的参考 |
| `预期行为` | `suggested_result` | 用例预期结果的参考 |
| `覆盖度矩阵` | `coverage_matrix` | 用于编写时核对覆盖完整性 |

## 阶段三：test-case-writing → test-case-review

| 输出字段（用例编写） | 输入字段（用例评审） | 说明 |
|----------------------|----------------------|------|
| `feature_name` | `feature_name` | 功能标识 |
| `03_test_cases.md` | `test_cases_file` | 测试用例文档路径 |
| `用例ID` | `case_id` | 评审对象标识 |
| `来源测试点` | `source_tp_id` | 评审时核对TP覆盖完整性 |
| `来源需求` | `source_req_id` | 评审时核对需求覆盖完整性 |
| `优先级` | `priority` | 评审优先级合理性 |
| `预期结果` | `expected_result` | 评审可验证性 |
| `RTM表格` | `rtm` | 评审追踪关系 |
| `01_requirements_analysis.md` | `requirements_analysis_file` | 评审时对照原始需求 |
| `02_test_points.md` | `test_points_file` | 评审时对照测试点清单 |

## 阶段四：test-case-review → test-case-output

| 输出字段（用例评审） | 输入字段（用例输出） | 说明 |
|----------------------|----------------------|------|
| `feature_name` | `feature_name` | 功能标识 |
| `04_review_report.md` | `review_report_file` | 评审报告路径 |
| `评审结论` | `review_status` | 输出阶段根据结论决定交付策略 |
| `问题清单` | `issue_list` | 输出阶段需附带已知问题说明 |
| `质量评分` | `quality_score` | 输出阶段在交付物中体现质量指标 |
| `覆盖度分析` | `coverage_analysis` | 输出阶段生成最终统计报表 |
| `改进建议` | `improvement_suggestions` | 输出阶段纳入交付说明 |
| `03_test_cases.md` | `test_cases_file` | 核心用例数据来源 |

## 阶段五：test-case-output → test-case-excel-export 【可选】

| 输出字段（用例输出） | 输入字段（Excel导出） | 说明 |
|----------------------|-----------------------|------|
| `feature_name` | `feature_name` | 功能标识 |
| `05_test_cases.json` | `input_json_path` | 结构化JSON文件路径 |
| `metadata` | `metadata` | Excel元信息区域数据来源 |
| `statistics` | `statistics` | 统计概览Sheet数据来源 |
| `traceability` | `traceability` | 需求追踪Sheet数据来源 |
| `cases` | `cases` | 用例详情Sheet数据来源 |
| `review` | `review_data` | 评审结果Sheet数据来源 |

**输出文件**：
- `06_test_cases.xlsx` - Excel工作簿（多Sheet）
- `06_export_log.txt` - 导出日志

**Excel工作表结构**：
| Sheet名称 | 内容 |
|-----------|------|
| 用例详情 | 完整用例列表，含表头样式、筛选、冻结首行 |
| 需求追踪 | REQ → 用例映射关系 |
| 统计概览 | 元信息 + 用例统计数据 |
| 评审结果 | 质量评分 + 问题清单 |

## 跨阶段通用字段映射

| 通用概念 | 需求分析阶段 | 测试点提取阶段 | 用例编写阶段 | 用例评审阶段 | 用例输出阶段 | Excel导出阶段 |
|----------|--------------|----------------|--------------|--------------|--------------|---------------|
| 功能标识 | `feature_name` | `feature_name` | `feature_name` | `feature_name` | `feature_name` | `feature_name` |
| 需求条目 | `REQ-NNN` | `source_req_id` | `source_req_id` | `source_req_id` | `req_id` | — |
| 业务规则 | `BR-NNN` | `source_rule_id` | `source_rule_id` | — | — | — |
| 测试点 | — | `TP-NNN` | `source_tp_id` | `source_tp_id` | `tp_id` | — |
| 用例标识 | — | — | `TC-{PREFIX}-NNN` | `case_id` | `case_id` | — |
| 优先级 | `P0/P1/P2` | `P0/P1/P2` | `P0/P1/P2` | `priority` | `priority` | — |
| 文件路径 | `01_requirements_analysis.md` | `02_test_points.md` | `03_test_cases.md` | `04_review_report.md` | `05_delivery_report.md` | `06_test_cases.xlsx` |
