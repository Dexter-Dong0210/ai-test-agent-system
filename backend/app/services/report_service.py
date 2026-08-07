"""
测试报告生成服务

使用ECharts MCP动态生成图表配置
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_report import TestReport, ReportType, ReportFormat, ReportStatus
from app.models.test_run import TestRun
from app.models.test_result import TestResult
from app.repositories.test_report_repo import TestReportRepository
from app.services.echarts_mcp import echarts_generator
from app.config.minio_client import MinIOClient
from app.config.settings import settings
from app.utils.exceptions import NotFoundException


class ReportDataService:
    """报告数据收集服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def collect_test_run_data(self, test_run_ids: List[UUID]) -> Dict:
        """收集测试运行数据"""
        
        # 查询测试运行
        test_runs = await self.session.execute(
            select(TestRun).where(TestRun.id.in_(test_run_ids))
        )
        test_runs = test_runs.scalars().all()
        
        # 收集统计信息
        statistics = {
            "total_cases": 0,
            "passed": 0,
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "total_duration": 0,
            "avg_duration": 0,
        }
        
        test_results = []
        
        for run in test_runs:
            results = await self.session.execute(
                select(TestResult).where(TestResult.test_run_id == run.id)
            )
            results = results.scalars().all()
            
            for result in results:
                statistics["total_cases"] += 1
                
                if result.status == "passed":
                    statistics["passed"] += 1
                elif result.status == "failed":
                    statistics["failed"] += 1
                elif result.status == "blocked":
                    statistics["blocked"] += 1
                elif result.status == "skipped":
                    statistics["skipped"] += 1
                
                if result.duration:
                    statistics["total_duration"] += result.duration
                
                test_results.append({
                    "name": result.test_case.name if result.test_case else "Unknown",
                    "status": result.status,
                    "duration": result.duration,
                    "error_message": result.error_message,
                    "executed_at": result.executed_at.isoformat() if result.executed_at else None
                })
        
        # 计算通过率和平均耗时
        if statistics["total_cases"] > 0:
            statistics["pass_rate"] = round(
                (statistics["passed"] / statistics["total_cases"]) * 100, 2
            )
            statistics["avg_duration"] = round(
                statistics["total_duration"] / statistics["total_cases"], 2
            )
        
        return {
            "statistics": statistics,
            "test_results": test_results,
            "test_runs": [
                {
                    "id": str(run.id),
                    "name": run.name,
                    "status": run.status,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "completed_at": run.completed_at.isoformat() if run.completed_at else None
                }
                for run in test_runs
            ]
        }
    
    async def collect_trend_data(self, project_id: UUID, days: int = 30) -> Dict:
        """收集趋势数据"""
        
        from datetime import timedelta
        from sqlalchemy import and_
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询最近N天的测试运行
        test_runs = await self.session.execute(
            select(TestRun)
            .where(
                and_(
                    TestRun.project_id == project_id,
                    TestRun.started_at >= start_date
                )
            )
            .order_by(TestRun.started_at)
        )
        test_runs = test_runs.scalars().all()
        
        # 按天统计
        daily_stats = {}
        for run in test_runs:
            if run.started_at:
                date_key = run.started_at.strftime("%Y-%m-%d")
                
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0
                    }
                
                # 获取该运行的结果统计
                results = await self.session.execute(
                    select(TestResult).where(TestResult.test_run_id == run.id)
                )
                results = results.scalars().all()
                
                for result in results:
                    daily_stats[date_key]["total"] += 1
                    if result.status == "passed":
                        daily_stats[date_key]["passed"] += 1
                    elif result.status == "failed":
                        daily_stats[date_key]["failed"] += 1
        
        # 计算每日通过率
        trend_data = {
            "dates": [],
            "pass_rates": [],
            "total_cases": [],
            "failed_cases": []
        }
        
        for date, stats in sorted(daily_stats.items()):
            trend_data["dates"].append(date)
            if stats["total"] > 0:
                trend_data["pass_rates"].append(
                    round((stats["passed"] / stats["total"]) * 100, 2)
                )
            else:
                trend_data["pass_rates"].append(0)
            trend_data["total_cases"].append(stats["total"])
            trend_data["failed_cases"].append(stats["failed"])
        
        return trend_data


class ReportGenerator:
    """报告生成器（使用ECharts MCP）"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.data_service = ReportDataService(session)
        self.minio_client = MinIOClient()
        
        # Jinja2模板环境
        self.template_env = Environment(
            loader=FileSystemLoader('app/templates/reports')
        )
    
    async def generate_summary_report(
        self,
        project_id: UUID,
        test_run_ids: List[UUID],
        **options
    ) -> str:
        """生成汇总报告（HTML）"""
        
        # 收集数据
        data = await self.data_service.collect_test_run_data(test_run_ids)
        trend_data = await self.data_service.collect_trend_data(project_id)
        
        # 使用ECharts MCP生成图表配置
        charts = await self._generate_charts(data, trend_data)
        
        # 渲染HTML
        template = self.template_env.get_template('summary.html')
        
        html_content = template.render(
            project_name=options.get("project_name", "项目"),
            report_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            statistics=data["statistics"],
            test_results=data["test_results"],
            charts=charts,
            echarts_cdn="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"
        )
        
        return html_content
    
    async def _generate_charts(
        self,
        data: Dict,
        trend_data: Dict
    ) -> Dict[str, Any]:
        """使用ECharts MCP生成图表配置"""
        
        stats = data["statistics"]
        
        charts = {}
        
        # 1. 通过率仪表盘
        charts["gauge"] = echarts_generator.generate_gauge_chart(
            title="通过率",
            value=stats.get("pass_rate", 0)
        )
        
        # 2. 测试结果分布饼图
        charts["pie"] = echarts_generator.generate_pie_chart(
            title="测试结果分布",
            data=[
                {"name": "通过", "value": stats.get("passed", 0)},
                {"name": "失败", "value": stats.get("failed", 0)},
                {"name": "阻塞", "value": stats.get("blocked", 0)},
                {"name": "跳过", "value": stats.get("skipped", 0)}
            ]
        )
        
        # 3. 执行趋势折线图
        charts["trend"] = echarts_generator.generate_line_chart(
            title="执行趋势（最近30天）",
            x_axis_data=trend_data.get("dates", []),
            series_data=[
                {
                    "name": "通过率",
                    "data": trend_data.get("pass_rates", [])
                },
                {
                    "name": "用例数",
                    "data": trend_data.get("total_cases", [])
                }
            ]
        )
        
        return charts
    
    async def save_report(
        self,
        project_id: UUID,
        report_type: ReportType,
        html_content: str,
        **metadata
    ) -> TestReport:
        """保存报告到MinIO和数据库"""
        
        # 上传到MinIO
        from datetime import timedelta
        file_name = f"reports/{project_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        self.minio_client.client.put_object(
            bucket_name=settings.minio_bucket,
            object_name=file_name,
            data=html_content.encode('utf-8'),
            length=len(html_content.encode('utf-8')),
            content_type='text/html'
        )
        
        # 创建数据库记录
        report = TestReport(
            project_id=project_id,
            title=metadata.get("title", "测试报告"),
            report_type=report_type,
            report_format=ReportFormat.HTML,
            file_path=file_name,
            file_size=len(html_content.encode('utf-8')),
            status=ReportStatus.COMPLETED,
            generated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=90)
        )
        
        self.session.add(report)
        await self.session.commit()
        
        return report


class ReportService:
    """报告服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TestReportRepository(session)
        self.generator = ReportGenerator(session)
    
    async def create_report(
        self,
        project_id: UUID,
        test_run_ids: List[UUID],
        title: str = "测试报告",
        report_type: ReportType = ReportType.SUMMARY
    ) -> TestReport:
        """创建测试报告"""
        
        # 生成报告
        html_content = await self.generator.generate_summary_report(
            project_id=project_id,
            test_run_ids=test_run_ids,
            project_name=title
        )
        
        # 保存报告
        report = await self.generator.save_report(
            project_id=project_id,
            report_type=report_type,
            html_content=html_content,
            title=title
        )
        
        return report
    
    async def get_report(self, report_id: UUID) -> str:
        """获取报告内容"""
        
        report = await self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("报告不存在")
        
        # 从MinIO读取
        response = self.generator.minio_client.client.get_object(
            bucket_name=settings.minio_bucket,
            object_name=report.file_path
        )
        
        html_content = response.read().decode('utf-8')
        
        return html_content