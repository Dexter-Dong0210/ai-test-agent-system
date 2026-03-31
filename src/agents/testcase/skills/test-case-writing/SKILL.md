---
name: test-case-writing
description: Writes detailed, executable test cases based on a test point inventory and requirements analysis. Outputs standardized test case documents with actionable steps, specific test data, observable expected results, and traceability to requirements and test points. Use after test-point-extraction and before test-case-review.
compatibility: Requires filesystem access to read and write markdown files. No external network dependencies.
metadata:
  version: "1.0.0"
  author: "Test Agent System"
  domain: "software-testing"
  stage: "03-test-case-writing"
---

# 用例编写技能 (Test Case Writing Skill)

## 技能目标
将测试点清单中的每个测试意图转化为结构化、可执行、可验证的测试用例。确保每个用例具备清晰的前置条件、编号步骤、具体测试数据、明确预期结果，并建立与需求条目（REQ）、测试点（TP）的双向追踪关系。输出结果可直接供手工执行或自动化脚本对接。

## 适用场景 / 不适用场景

**适用场景：**
- 已存在结构化的测试点清单（TP）和需求分析文档
- 需要输出可直接用于测试执行的用例文档
- 需要建立用例与需求之间的追踪矩阵

**不适用场景：**
- 测试点尚未提取或需求分析缺失（应先执行 test-point-extraction）
- 仅需高层测试方案或测试策略，无需详细执行步骤
- 用例已经由其他团队编写完成，仅需评审

## 输入定义

### 必填项
| 字段 | 数据格式 | 说明 | 示例 |
|------|----------|------|------|
| `feature_name` | 字符串 | 功能标识 | `user_login` |
| `test_points_file` | 文件路径 | 测试点清单文件 | `test_user_login/02_test_points.md` |
| `requirements_analysis_file` | 文件路径 | 需求分析文档 | `test_user_login/01_requirements_analysis.md` |

### 可选项
| 字段 | 数据格式 | 说明 | 示例 |
|------|----------|------|------|
| `case_id_prefix` | 字符串 | 用例ID前缀 | `TC-LOGIN` |
| `output_format` | 枚举 | 输出格式：markdown / json / csv | `markdown` |
| `automation_target` | 枚举 | 自动化对接目标：none / pytest / robot / selenium | `none` |
| `language` | 枚举 | 用例语言：zh / en | `zh` |

## 输出定义

输出文件路径：`test_{feature_name}/03_test_cases.md`
（可选）`test_{feature_name}/03_test_cases.json`

### 结构化格式（Markdown）
```markdown
# 测试用例 - {feature_name}

## 元信息
| 字段 | 值 |
|------|-----|
| 来源测试点文档 | 02_test_points.md |
| 来源需求文档 | 01_requirements_analysis.md |
| 用例总数 | N |
| 编写日期 | YYYY-MM-DD |

## 1. 统计概览
| 统计项 | 数量 |
|--------|------|
| 总用例数 | 12 |
| P0用例 | 4 |
| P1用例 | 5 |
| P2用例 | 3 |
| 正向用例 | 4 |
| 反向用例 | 4 |
| 边界用例 | 3 |
| 异常用例 | 1 |

## 2. 需求追踪矩阵 (RTM)
| 需求ID | 覆盖用例ID | 覆盖状态 |
|--------|------------|----------|
| REQ-001 | TC-LOGIN-001, TC-LOGIN-002 | 已覆盖 |
| REQ-002 | TC-LOGIN-005 | 已覆盖 |

## 3. 用例详情

### TC-LOGIN-001: 使用有效手机号和正确验证码成功登录

#### 基础信息
| 字段 | 内容 |
|------|------|
| 用例ID | TC-LOGIN-001 |
| 模块 | 用户登录 |
| 标题 | 使用有效手机号和正确验证码成功登录 |
| 优先级 | P0 |
| 用例类型 | 正向 |
| 来源测试点 | TP-001 |
| 来源需求 | REQ-001, BR-001 |
| 编写人 | Test Agent |
| 版本 | v1.0 |

#### 前置条件
1. 用户已访问登录页面 `https://app.example.com/login`
2. 测试手机号 `13800138000` 已在系统中注册且状态正常
3. 短信网关服务可用

#### 测试数据
| 数据项 | 值 | 说明 |
|--------|-----|------|
| 手机号 | 13800138000 | 已注册的有效手机号 |
| 验证码 | 123456 | 通过短信接口获取的有效验证码（5分钟内） |

#### 测试步骤
1. 在【手机号】输入框中输入 `13800138000`
2. 点击【获取验证码】按钮
3. 等待短信接收，在【验证码】输入框中输入 `123456`
4. 勾选【用户协议】复选框
5. 点击【登录】按钮

#### 预期结果
1. 页面跳转至系统首页 `https://app.example.com/home`
2. 页面右上角显示用户昵称 "测试用户A"
3. 浏览器本地存储（LocalStorage）中写入 `auth_token`，且值不为空
4. 系统后台记录登录成功日志，包含用户ID和时间戳

#### 清理步骤
1. 点击右上角【退出登录】
2. 清除浏览器缓存和 LocalStorage
```

### 字段说明
- `用例ID`：格式 `{prefix}-NNN`，如 `TC-LOGIN-001`
- `模块`：功能模块名称
- `标题`：动作 + 条件 + 预期结果，避免模糊词
- `前置条件`：环境、数据、状态、权限的具体准备要求
- `测试数据`：具体值，非"有效数据"等模糊描述
- `测试步骤`：编号列表，每步一个动作，明确操作对象
- `预期结果`：可观察、可验证的具体现象或数据
- `清理步骤`：恢复环境，保证用例独立性

## 执行步骤

### Step 1: 读取上游文档
读取 `01_requirements_analysis.md` 和 `02_test_points.md`，理解需求背景、业务规则、测试意图。

### Step 2: 用例设计
对每个测试点（TP）进行用例转化：
1. **确定用例范围**：一个 TP 可对应1个或多个用例。若 TP 包含多个等价类，可合并为1个用例的数据驱动形式；若涉及不同前置状态，拆分为多个用例
2. **编写用例标题**：格式为 `[动作] + [条件] + [预期结果]`，如 "使用已过期验证码登录时系统提示重新获取"
3. **设计前置条件**：列出执行本用例前必须满足的所有条件，包括页面URL、账号状态、环境配置、第三方服务状态
4. **设计测试数据**：给出具体输入值，必要时使用表格呈现多组数据
5. **编写测试步骤**：每步只描述一个动作，使用明确的UI元素名称或API接口路径
6. **编写预期结果**：每条预期结果对应一个可验证的观察点，避免使用"成功"、"正常"等模糊词
7. **标注追踪关系**：在用例中明确标注 `来源测试点` 和 `来源需求`

### Step 3: 构建需求追踪矩阵 (RTM)
在文档中建立表格，列出每个 REQ 被哪些用例ID覆盖，确保无遗漏。

### Step 4: 统计与校验
统计用例总数、优先级分布、类型分布，检查是否有重复ID、缺失字段。

### Step 5: 输出用例文档
写入 `test_{feature_name}/03_test_cases.md`。若 `output_format` 包含 json，同时输出 `03_test_cases.json`。

## 质量门禁 (DoD)

| 检查项 | 验收标准 | 检查方式 |
|--------|----------|----------|
| 可执行性 | 每个用例的前置条件、步骤、预期结果明确到可直接交给初级测试工程师执行 | 抽样执行模拟 |
| 完整性 | 每个 TP 至少转化为1个用例；每个 REQ 至少被1个用例覆盖 | RTM核对 |
| 可追踪性 | 每个用例必须标注 `来源测试点` 和 `来源需求` | 正则扫描 |
| 一致性 | 用例ID格式统一，术语与需求分析文档一致 | 格式校验 |
| 数据具体性 | 测试数据中无"有效"、"任意"、"正常"等模糊词 | 关键词过滤 |
| 预期结果可验证 | 预期结果中包含可观察的UI元素、返回值、状态码、日志记录等 | 人工审查 |

## 异常与边界处理

| 异常场景 | 处理策略 |
|----------|----------|
| 测试点描述过于抽象 | 结合需求分析文档中的业务规则进行细化，拆分为多个具体用例，并在用例中补充业务上下文 |
| 测试数据无法构造 | 使用 `【数据待准备】` 标注，给出数据构造建议（如SQL插入、Mock接口、测试账号申请流程） |
| 前置条件依赖外部系统 | 明确写出外部系统的预期状态，并提供降级方案（如使用Mock服务、测试环境白名单） |
| 同一TP需要大量数据组合 | 采用数据驱动方式，在"测试数据"表格中列出多组数据，步骤中引用表格行号，避免步骤冗余 |
| 需求变更导致TP失效 | 在用例中标注 `【关联TP已变更】`，保留原用例并新增修订版本，确保历史可追溯 |

## 与上下游技能的衔接规则

### 输入来源
- **上游技能**：`test-point-extraction`、`requirements-analysis`
- **输入文件**：`02_test_points.md`、`01_requirements_analysis.md`

### 输出去向
- **下游技能**：`test-case-review`
- **输出文件**：`03_test_cases.md`（可选 `03_test_cases.json`）

### 字段映射
| 本技能输出字段 | 下游技能输入字段 | 说明 |
|----------------|------------------|------|
| `用例ID` | `case_id` | 评审对象标识 |
| `来源测试点` | `source_tp_id` | 评审时核对TP覆盖完整性 |
| `来源需求` | `source_req_id` | 评审时核对需求覆盖完整性 |
| `优先级` | `priority` | 评审优先级合理性 |
| `预期结果` | `expected_result` | 评审可验证性 |
| `RTM表格` | `rtm` | 评审追踪关系 |

## 复用与扩展点

- **自动化模板**：在 `references/` 目录下维护不同自动化框架的用例模板（pytest、Robot Framework、Selenium）
- **数据驱动扩展**：支持将多组测试数据抽取为独立JSON/CSV，便于自动化参数化
- **多语言输出**：通过 `language` 参数支持中英文用例输出
- **领域词库**：维护企业级术语词库，确保跨模块用例术语一致
