# 测试报告生成使用指南

## 📖 概述

本系统采用 **ECharts MCP** 方式动态生成测试报告图表，具有以下优势：

- ✅ **AI驱动**：AI根据数据自动选择最佳图表类型和配置
- ✅ **动态灵活**：图表配置由AI生成，无需硬编码
- ✅ **交互丰富**：ECharts提供强大的图表交互能力
- ✅ **易于扩展**：新增图表类型只需添加MCP工具

---

## 🚀 快速开始

### 1. 生成报告

```bash
# API调用
POST /api/v2/projects/{project_identifier}/reports

# 请求体
{
  "title": "登录模块测试报告",
  "test_run_ids": ["uuid-1", "uuid-2"],
  "report_type": "summary",
  "include_details": true
}

# 响应
{
  "id": "report-uuid",
  "title": "登录模块测试报告",
  "status": "completed",
  "generated_at": "2026-06-10T19:30:00Z"
}
```

### 2. 查看报告

```bash
# 在浏览器中打开
GET /api/v2/projects/{project_identifier}/reports/{report_id}

# 返回HTML页面（包含ECharts图表）
```

### 3. 下载报告

```bash
# 下载HTML格式
GET /api/v2/projects/{project_identifier}/reports/{report_id}/download?format=html

# 下载PDF格式（待实现）
GET /api/v2/projects/{project_identifier}/reports/{report_id}/download?format=pdf
```

---

## 🎨 报告内容

### 自动生成的图表

#### 1. 通过率仪表盘
- 显示当前通过率百分比
- 颜色随通过率变化（绿色>80%，黄色>60%，红色<60%）

#### 2. 测试结果分布饼图
- 显示通过、失败、阻塞、跳过用例占比
- 支持交互式选择和放大

#### 3. 执行趋势折线图
- 显示最近30天的通过率趋势
- 包含最大值、最小值标记

#### 4. 详细结果表格
- 分页显示所有用例执行结果
- 支持排序、筛选、搜索

---

## 🔧 ECharts MCP 工具

系统提供了以下MCP工具供AI动态生成图表：

### 1. generate_pie_chart

生成饼图（结果分布）

```python
# AI自动调用
echarts_generator.generate_pie_chart(
    title="测试结果分布",
    data=[
        {"name": "通过", "value": 85},
        {"name": "失败", "value": 15}
    ]
)
```

### 2. generate_line_chart

生成折线图（趋势分析）

```python
echarts_generator.generate_line_chart(
    title="执行趋势",
    x_axis_data=["2026-06-01", "2026-06-02", "2026-06-03"],
    series_data=[
        {"name": "通过率", "data": [85, 90, 88]}
    ]
)
```

### 3. generate_bar_chart

生成柱状图（缺陷分布）

```python
echarts_generator.generate_bar_chart(
    title="缺陷分布",
    x_axis_data=["登录模块", "订单模块", "支付模块"],
    series_data=[
        {"name": "高", "data": [5, 3, 2]},
        {"name": "中", "data": [10, 8, 5]}
    ]
)
```

### 4. generate_radar_chart

生成雷达图（质量综合评估）

```python
echarts_generator.generate_radar_chart(
    title="质量指标",
    indicators=[
        {"name": "覆盖率", "max": 100},
        {"name": "通过率", "max": 100},
        {"name": "自动化率", "max": 100}
    ],
    data=[
        {"value": [85, 90, 88], "name": "当前版本"}
    ]
)
```

### 5. generate_gauge_chart

生成仪表盘（单一指标）

```python
echarts_generator.generate_gauge_chart(
    title="通过率",
    value=85.5
)
```

---

## 💡 使用示例

### Python调用

```python
from app.services.report_service import ReportService
from uuid import UUID

# 创建报告服务
service = ReportService(session)

# 生成报告
report = await service.create_report(
    project_id=UUID("project-uuid"),
    test_run_ids=[UUID("run-1"), UUID("run-2")],
    title="登录模块测试报告"
)

# 获取报告HTML
html_content = await service.get_report(report.id)
```

### 前端集成

```typescript
// 生成报告
const response = await fetch('/api/v2/projects/TEST-001/reports', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: '测试报告',
    test_run_ids: ['run-id-1', 'run-id-2']
  })
});

const report = await response.json();

// 在新窗口打开报告
window.open(`/api/v2/projects/TEST-001/reports/${report.id}`);
```

---

## 🎯 AI增强能力

### 自动选择图表类型

AI会根据数据特征自动选择最合适的图表：

```
数据类型：比例数据（如通过率）
AI选择：饼图或仪表盘

数据类型：时间序列数据
AI选择：折线图

数据类型：分类对比数据
AI选择：柱状图

数据类型：多维度评估
AI选择：雷达图
```

### 自然语言生成报告

```python
# 用户输入
"生成登录模块最近一周的测试报告，重点关注失败用例"

# AI自动：
# 1. 收集最近7天的测试运行数据
# 2. 筛选失败用例
# 3. 分析失败原因
# 4. 选择合适的图表类型
# 5. 生成报告HTML
```

---

## 📊 性能优化

### 1. 数据预聚合

```python
# 统计数据预计算（在报告中）
statistics: {
    "total_cases": 100,
    "passed": 85,
    "pass_rate": 85.0
}
```

### 2. 图表懒加载

```html
<!-- HTML模板中 -->
<script>
// 只在可见区域渲染图表
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            renderChart(entry.target);
        }
    });
});

document.querySelectorAll('.chart-container').forEach(el => {
    observer.observe(el);
});
</script>
```

### 3. 报告缓存

- HTML文件缓存到MinIO（90天）
- 图表配置缓存到Redis（1小时）

---

## 🔍 常见问题

### Q1: 如何自定义图表样式？

A: 在ECharts MCP工具中添加style参数：

```python
generate_pie_chart(
    title="测试结果",
    data=data,
    style_config={
        "colors": ["#67e0e3", "#fd666d"],
        "radius": ["40%", "70%"]
    }
)
```

### Q2: 如何生成PDF格式？

A: 使用WeasyPrint转换：

```python
from weasyprint import HTML

html_content = await service.get_report(report_id)
HTML(string=html_content).write_pdf('report.pdf')
```

### Q3: 如何定时生成报告？

A: 配置定时任务：

```python
# 在test_reports表中设置
schedule_enabled: True
schedule_cron: "0 9 * * 1"  # 每周一早9点
```

---

## 📚 相关文档

- ECharts官方文档：https://echarts.apache.org/
- MCP协议：https://modelcontextprotocol.io/
- WeasyPrint：https://weasyprint.org/

---

**更新时间**: 2026-06-10  
**维护者**: AI测试平台团队