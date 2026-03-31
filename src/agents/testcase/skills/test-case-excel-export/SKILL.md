---
name: test-case-excel-export
description: Exports reviewed test cases into a formatted Excel workbook with multiple sheets (cases, traceability, statistics, review results). Supports enterprise-level formatting with headers, filters, and frozen panes. Use as the final output step when Excel deliverable is required.
compatibility: Requires Python with openpyxl package installed. Filesystem access for reading JSON and writing .xlsx files.
metadata:
  version: "1.0.0"
  author: "Test Agent System"
  domain: "software-testing"
  stage: "06-excel-export"
  dependencies: ["openpyxl>=3.1.0"]
---

# 测试用例Excel导出技能 (Test Case Excel Export Skill)

## 技能目标
将经过评审的测试用例数据（JSON格式）转换为格式规范、企业级的 Excel 工作簿。生成包含多个工作表（Sheet）的 `.xlsx` 文件，支持表头样式、自动列宽、数据筛选、冻结窗格等格式化特性，便于测试团队使用 Excel 进行用例管理、评审会议展示和归档。

## 适用场景 / 不适用场景

**适用场景：**
- 测试团队习惯使用 Excel 管理测试用例
- 需要向非技术干系人（管理层、业务方）展示测试结果
- 需要将用例导入到仅支持 Excel 的测试管理系统
- 需要进行离线评审或打印纸质评审材料

**不适用场景：**
- 上游测试用例尚未完成评审（应先执行 test-case-review）
- 目标系统仅接受 CSV/JSON 等格式（应使用 test-case-output）
- 环境中未安装 Python 或 openpyxl 库

## 输入定义

### 必填项
| 字段 | 数据格式 | 说明 | 示例 |
|------|----------|------|------|
| `feature_name` | 字符串 | 功能标识，用于文件夹和文件名 | `user_login` |
| `input_json_path` | 文件路径 | 测试用例结构化JSON文件 | `test_user_login/05_test_cases.json` |

### 可选项
| 字段 | 数据格式 | 说明 | 默认值 |
|------|----------|------|--------|
| `output_xlsx_path` | 文件路径 | 输出Excel文件路径 | `test_{feature_name}/06_test_cases.xlsx` |
| `include_sheets` | 字符串列表 | 要包含的工作表 | `["cases", "traceability", "statistics", "review"]` |
| `sheet_style` | 枚举 | 样式主题：blue/gray/green | `blue` |

## 输出定义

### 输出文件
| 文件路径 | 格式 | 用途 |
|----------|------|------|
| `test_{feature_name}/06_test_cases.xlsx` | Excel (.xlsx) | 格式化的测试用例工作簿 |

### Excel 工作表结构

#### Sheet 1: 用例详情 (Cases)
包含完整的测试用例列表，每行一个用例。

**字段映射表（JSON字段 → Excel表头）：**

| JSON字段（英文） | Excel表头（中文） | 说明 | 格式 |
|------------------|-------------------|------|------|
| `case_id` | 用例ID | TC-XXX-NNN | 文本 |
| `module` | 模块 | 功能模块名称 | 文本 |
| `title` | 标题 | 用例描述 | 文本 |
| `priority` | 优先级 | P0/P1/P2 | 文本（建议条件格式高亮P0） |
| `type` | 用例类型 | 正向/反向/边界/异常 | 文本 |
| `source_req` | 来源需求 | REQ-001, REQ-002 | 文本 |
| `source_tp` | 来源测试点 | TP-NNN | 文本 |
| `preconditions` | 前置条件 | 环境准备步骤 | 多行文本，自动换行 |
| `test_data` | 测试数据 | 具体测试数据值 | JSON或文本，自动换行 |
| `steps` | 测试步骤 | 自动转换为 `step1:xxx\nstep2:xxx` 格式 | 多行文本，自动换行 |
| `expected_results` | 预期结果 | 自动转换为 `assert1:xxx\nassert2:xxx` 格式 | 多行文本，自动换行 |
| `cleanup_steps` | 清理步骤 | 环境恢复步骤 | 多行文本，自动换行 |
| `remark` | 备注 | 其他说明 | 文本 |

**格式特性：**
- 首行表头：蓝色背景、白色粗体、居中对齐
- 所有单元格：细边框
- 自动列宽（10-60字符范围）
- 冻结首行
- 启用筛选
- **测试步骤格式**：`step1:操作内容\nstep2:操作内容`（自动转换）
- **预期结果格式**：`assert1:验证点\nassert2:验证点`（自动转换）

#### Sheet 2: 需求追踪 (Traceability)
展示需求到用例的映射关系。

**字段映射表：**

| JSON字段（英文） | Excel表头（中文） | 说明 |
|------------------|-------------------|------|
| `req_id` | 需求ID | REQ-NNN |
| `req_desc` | 需求描述 | 需求简要描述 |
| `case_ids` | 覆盖用例数 | 覆盖该需求的用例数量（整数） |
| `case_ids` | 覆盖用例ID列表 | TC-XXX-001, TC-XXX-002 |
| `coverage_status` | 覆盖状态 | 已覆盖/未覆盖 |

#### Sheet 3: 统计概览 (Statistics)
展示测试用例的统计信息和元数据。

**元信息区域字段映射：**

| JSON字段（英文） | Excel表头（中文） | 示例值 |
|------------------|-------------------|--------|
| `feature_name` | 功能名称 | 用户登录 |
| `version` | 版本 | v1.0 |
| `delivery_date` | 交付日期 | 2024-01-15 |
| `review_status` | 评审结论 | 通过 |
| `quality_score` | 质量总分 | 88.9 |

**用例统计区域字段映射：**

| JSON字段（英文） | Excel表头（中文） | 说明 |
|------------------|-------------------|------|
| `total` | 总用例数 | 全部用例数量 |
| `p0` | P0用例 | 核心功能用例数 |
| `p1` | P1用例 | 重要功能用例数 |
| `p2` | P2用例 | 一般功能用例数 |
| `positive` | 正向用例 | 正常流程用例数 |
| `negative` | 反向用例 | 异常输入用例数 |
| `boundary` | 边界用例 | 边界值测试用例数 |
| `exception` | 异常用例 | 系统异常场景用例数 |

#### Sheet 4: 评审结果 (Review)
展示质量评分和问题清单。

**质量评分区域字段映射：**

| JSON字段（英文） | Excel表头（中文） | 说明 |
|------------------|-------------------|------|
| `dimension` | 评分维度 | 可执行性/完整性/可追踪性/一致性/可维护性/覆盖度 |
| `full_score` | 满分 | 100分制 |
| `score` | 得分 | 实际得分 |
| `weight` | 权重 | 百分比，如25% |
| `weighted_score` | 加权得分 | 得分×权重 |
| `comment` | 说明 | 评分说明 |

**问题清单区域字段映射：**

| JSON字段（英文） | Excel表头（中文） | 说明 |
|------------------|-------------------|------|
| - | 序号 | 问题序号（1,2,3...） |
| `case_id` | 用例ID | 问题关联的用例 |
| `issue_type` | 问题类型 | 覆盖不足/可执行性/一致性等 |
| `description` | 问题描述 | 具体问题说明 |
| `severity` | 严重程度 | 高/中/低 |
| `suggestion` | 修改建议 | 改进方案 |
| `owner` | 责任人 | 负责修复的人员 |

## 执行步骤

### Step 1: 读取输入文件
读取上游生成的 JSON 文件：`test_{feature_name}/05_test_cases.json`

JSON 期望结构：
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
      "case_ids": ["TC-LOGIN-001", "TC-LOGIN-002"],
      "coverage_status": "已覆盖"
    }
  ],
  "cases": [
    {
      "case_id": "TC-LOGIN-001",
      "module": "用户登录",
      "title": "使用有效手机号和正确验证码成功登录",
      "priority": "P0",
      "type": "正向",
      "source_req": ["REQ-001"],
      "source_tp": "TP-001",
      "preconditions": ["用户已访问登录页面"],
      "test_data": {"phone": "13800138000", "code": "123456"},
      "steps": ["1. 输入手机号", "2. 点击获取验证码"],
      "expected_results": ["页面跳转至首页"],
      "cleanup_steps": ["点击退出登录"],
      "remark": ""
    }
  ],
  "review": {
    "scores": [
      {"dimension": "可执行性", "full_score": 100, "score": 92, "weight": "25%", "weighted_score": 23.0, "comment": "..."}
    ],
    "issues": [
      {"case_id": "TC-LOGIN-005", "issue_type": "覆盖不足", "description": "...", "severity": "中", "suggestion": "...", "owner": "..."}
    ]
  }
}
```

### Step 2: 调用导出脚本
运行 Python 脚本生成 Excel：
```bash
python src/agents/testcase/skills/test-case-excel-export/scripts/export_to_excel.py \
    test_{feature_name}/05_test_cases.json \
    test_{feature_name}/06_test_cases.xlsx
```

### Step 3: 验证输出
检查生成的 Excel 文件：
- 文件是否存在且可打开
- 四个工作表是否齐全
- 表头样式是否正确（蓝色背景、白色字体）
- 筛选和冻结窗格是否生效
- 长文本是否正确换行

### Step 4: 记录导出日志
在输出文件夹中创建导出记录：
```
test_{feature_name}/06_export_log.txt
```
内容：
```
导出时间: YYYY-MM-DD HH:MM:SS
导出源文件: 05_test_cases.json
输出文件: 06_test_cases.xlsx
包含工作表: 用例详情, 需求追踪, 统计概览, 评审结果
用例总数: N
```

## 质量门禁 (DoD)

| 检查项 | 验收标准 | 检查方式 |
|--------|----------|----------|
| 文件生成 | Excel文件成功创建且可被Excel/WPS打开 | 手动检查 |
| 数据完整性 | 所有用例数据完整导出，无截断 | 抽样核对 |
| 格式规范 | 表头样式、边框、列宽符合企业级标准 | 视觉检查 |
| 功能特性 | 筛选、冻结窗格、自动换行功能正常 | 手动测试 |
| 追踪关系 | 需求追踪表与用例详情数据一致 | 交叉核对 |

## 异常与边界处理

| 异常场景 | 处理策略 |
|----------|----------|
| JSON文件不存在 | 报错并提示应先执行 `test-case-output` 技能 |
| JSON格式不合法 | 捕获异常，输出具体错误位置和修复建议 |
| openpyxl未安装 | 提示安装命令：`pip install openpyxl` |
| 用例数量过大（>10000） | 分多个Sheet导出，每Sheet最多10000行 |
| 单元格内容超长（>32767字符） | Excel单元格限制，自动截断并添加"[截断]"标记 |
| 文件名冲突 | 自动添加时间戳后缀生成新文件名 |

## 与上下游技能的衔接规则

### 输入来源
- **上游技能**：`test-case-output`（主要）、`test-case-review`（评审数据）
- **输入文件**：`test_{feature_name}/05_test_cases.json`

### 输出去向
- 无下游技能（本技能为流程终点之一，与 `test-case-output` 并行可选）
- 输出文件供测试团队直接使用

### 字段映射
| 上游输出字段 | 本技能输入字段 | 说明 |
|--------------|----------------|------|
| `metadata` | `metadata` | 元信息区域数据来源 |
| `statistics` | `statistics` | 统计概览Sheet数据来源 |
| `traceability` | `traceability` | 需求追踪Sheet数据来源 |
| `cases` | `cases` | 用例详情Sheet数据来源 |
| `review` | `review_data` | 评审结果Sheet数据来源 |

## 复用与扩展点

- **样式主题**：可在 `assets/` 目录下定义多套颜色主题（blue/gray/green），通过 `sheet_style` 参数切换
- **自定义列**：支持在 `references/` 下维护列定义映射表，适应不同企业的Excel模板要求
- **批量导出**：可扩展支持一次导出多个功能的Excel合并文件
- **图表支持**：未来可扩展在"统计概览"Sheet中添加用例分布饼图、优先级柱状图
