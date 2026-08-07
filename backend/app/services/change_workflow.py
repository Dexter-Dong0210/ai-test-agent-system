"""
变更分析工作流编排

职责：
1. 编排变更分析完整流程
2. 协调各 Agent 和服务
3. 管理工作流状态
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import structlog

from app.integrations.gate import (
    QualityGate,
    GitLabIntegration,
    NotificationService,
    GateStatus
)

logger = structlog.get_logger()


@dataclass
class WorkflowContext:
    """工作流上下文"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    base_branch: str = "develop"
    compare_branch: str = ""
    repo_url: str = ""
    mr_iid: Optional[int] = None
    commit_sha: Optional[str] = None
    commits: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowResult:
    """工作流结果"""
    workflow_id: str
    status: str
    steps: List[Dict]
    analysis_result: Optional[Dict] = None
    test_result: Optional[Dict] = None
    gate_result: Optional[Dict] = None
    error: Optional[str] = None


class ChangeAnalysisWorkflow:
    """变更分析工作流"""
    
    def __init__(
        self,
        change_agent,
        api_agent,
        quality_gate: QualityGate,
        gitlab: Optional[GitLabIntegration] = None,
        notification: Optional[NotificationService] = None
    ):
        self.change_agent = change_agent
        self.api_agent = api_agent
        self.quality_gate = quality_gate
        self.gitlab = gitlab
        self.notification = notification
    
    async def run(self, ctx: WorkflowContext) -> WorkflowResult:
        """执行完整工作流"""
        
        result = WorkflowResult(
            workflow_id=ctx.workflow_id,
            status="running",
            steps=[]
        )
        
        try:
            logger.info(
                "workflow_started",
                workflow_id=ctx.workflow_id,
                project_id=ctx.project_id,
                compare_branch=ctx.compare_branch
            )
            
            # Step 1: 变更检测
            step1 = await self._step_detect_changes(ctx)
            result.steps.append(step1)
            
            if step1.get("error"):
                result.status = "error"
                result.error = step1["error"]
                return result
            
            # Step 2: 影响分析
            step2 = await self._step_analyze_impact(ctx, step1["data"])
            result.steps.append(step2)
            
            # Step 3: 接口映射
            step3 = await self._step_map_endpoints(ctx, step2["data"])
            result.steps.append(step3)
            
            # Step 4: 风险评估
            step4 = await self._step_assess_risk(
                ctx,
                step1["data"],
                step2["data"],
                step3["data"]
            )
            result.steps.append(step4)
            
            analysis_result = {
                **step1["data"],
                **step2["data"],
                **step3["data"],
                **step4["data"]
            }
            result.analysis_result = analysis_result
            
            # Step 5: 测试决策
            if step4["data"]["risk_level"] == "LOW":
                result.status = "passed"
                result.gate_result = {
                    "status": "skipped",
                    "action": "allow",
                    "reason": "风险等级 LOW，无需测试"
                }
                return result
            
            # Step 6: 触发测试
            step5 = await self._step_trigger_tests(ctx, analysis_result)
            result.steps.append(step5)
            
            if step5.get("error"):
                result.status = "error"
                result.error = step5["error"]
                return result
            
            # Step 7: 等待测试完成并获取结果
            step6 = await self._step_get_test_results(ctx, step5["data"])
            result.steps.append(step6)
            result.test_result = step6["data"]
            
            # Step 8: 门禁评估
            step7 = await self._step_evaluate_gate(
                ctx,
                step6["data"],
                analysis_result
            )
            result.steps.append(step7)
            result.gate_result = step7["data"]
            
            # Step 9: 结果处理
            await self._step_handle_result(ctx, step7["data"], analysis_result)
            
            result.status = step7["data"]["status"]
            
            logger.info(
                "workflow_completed",
                workflow_id=ctx.workflow_id,
                status=result.status
            )
            
        except Exception as e:
            result.status = "error"
            result.error = str(e)
            
            logger.exception(
                "workflow_failed",
                workflow_id=ctx.workflow_id,
                error=str(e)
            )
            
            if self.notification:
                await self.notification.notify(
                    recipients=["dev-team"],
                    subject="变更分析工作流异常",
                    content=f"工作流 ID: {ctx.workflow_id}\n项目: {ctx.project_id}\n分支: {ctx.compare_branch}\n错误: {str(e)}",
                    channel="dingtalk"
                )
        
        return result
    
    async def _step_detect_changes(self, ctx: WorkflowContext) -> Dict:
        """Step 1: 变更检测"""
        logger.info("step_detect_changes", workflow_id=ctx.workflow_id)
        
        try:
            result = await self.change_agent.invoke({
                "task": "detect_changes",
                "base_branch": ctx.base_branch,
                "compare_branch": ctx.compare_branch,
                "repo_url": ctx.repo_url
            })
            
            return {
                "step": "detect_changes",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "detect_changes",
                "status": "error",
                "error": str(e)
            }
    
    async def _step_analyze_impact(
        self,
        ctx: WorkflowContext,
        changes: Dict
    ) -> Dict:
        """Step 2: 影响分析"""
        logger.info("step_analyze_impact", workflow_id=ctx.workflow_id)
        
        try:
            changed_files = changes.get("changed_files", [])
            targets = [
                f["path"].split("/")[-1].replace(".java", "").replace(".py", "")
                for f in changed_files
                if f.get("is_code")
            ]
            
            result = await self.change_agent.invoke({
                "task": "impact_analysis",
                "targets": targets[:10]
            })
            
            return {
                "step": "analyze_impact",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "analyze_impact",
                "status": "error",
                "error": str(e),
                "data": {}
            }
    
    async def _step_map_endpoints(
        self,
        ctx: WorkflowContext,
        impact: Dict
    ) -> Dict:
        """Step 3: 接口映射"""
        logger.info("step_map_endpoints", workflow_id=ctx.workflow_id)
        
        try:
            affected_classes = impact.get("affected_classes", [])
            
            result = await self.change_agent.invoke({
                "task": "map_to_endpoints",
                "affected_classes": affected_classes,
                "project_identifier": ctx.project_id
            })
            
            return {
                "step": "map_endpoints",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "map_endpoints",
                "status": "error",
                "error": str(e),
                "data": {"endpoints": []}
            }
    
    async def _step_assess_risk(
        self,
        ctx: WorkflowContext,
        changes: Dict,
        impact: Dict,
        endpoints: Dict
    ) -> Dict:
        """Step 4: 风险评估"""
        logger.info("step_assess_risk", workflow_id=ctx.workflow_id)
        
        try:
            result = await self.change_agent.invoke({
                "task": "assess_risk",
                "changed_files": changes.get("changed_files", []),
                "affected_endpoints": endpoints.get("endpoints", []),
                "impact_result": impact
            })
            
            return {
                "step": "assess_risk",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "assess_risk",
                "status": "error",
                "error": str(e),
                "data": {"risk_level": "MEDIUM", "test_scope": "smoke"}
            }
    
    async def _step_trigger_tests(
        self,
        ctx: WorkflowContext,
        analysis: Dict
    ) -> Dict:
        """Step 5: 触发测试"""
        logger.info("step_trigger_tests", workflow_id=ctx.workflow_id)
        
        try:
            result = await self.api_agent.invoke({
                "task": "trigger_tests",
                "affected_endpoints": analysis.get("endpoints", []),
                "risk_level": analysis.get("risk_level", "MEDIUM"),
                "test_scope": analysis.get("test_scope", "smoke"),
                "project_identifier": ctx.project_id
            })
            
            return {
                "step": "trigger_tests",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "trigger_tests",
                "status": "error",
                "error": str(e)
            }
    
    async def _step_get_test_results(
        self,
        ctx: WorkflowContext,
        test_info: Dict
    ) -> Dict:
        """Step 6: 获取测试结果"""
        logger.info("step_get_test_results", workflow_id=ctx.workflow_id)
        
        test_plan_id = test_info.get("test_plan_id")
        
        if not test_plan_id:
            return {
                "step": "get_test_results",
                "status": "skipped",
                "data": {"status": "skipped", "total": 0, "passed": 0}
            }
        
        try:
            result = await self.api_agent.invoke({
                "task": "get_test_results",
                "test_plan_id": test_plan_id
            })
            
            return {
                "step": "get_test_results",
                "status": "completed",
                "data": result
            }
        except Exception as e:
            return {
                "step": "get_test_results",
                "status": "error",
                "error": str(e),
                "data": {"status": "error", "total": 0, "passed": 0}
            }
    
    async def _step_evaluate_gate(
        self,
        ctx: WorkflowContext,
        test_results: Dict,
        analysis: Dict
    ) -> Dict:
        """Step 7: 门禁评估"""
        logger.info("step_evaluate_gate", workflow_id=ctx.workflow_id)
        
        try:
            gate_result = await self.quality_gate.evaluate(
                test_results=test_results,
                analysis_result=analysis
            )
            
            return {
                "step": "evaluate_gate",
                "status": "completed",
                "data": {
                    "status": gate_result.status,
                    "action": gate_result.action,
                    "block_reason": gate_result.block_reason,
                    "violations": gate_result.violations
                }
            }
        except Exception as e:
            return {
                "step": "evaluate_gate",
                "status": "error",
                "error": str(e),
                "data": {
                    "status": "error",
                    "action": "allow"
                }
            }
    
    async def _step_handle_result(
        self,
        ctx: WorkflowContext,
        gate_data: Dict,
        analysis: Dict
    ):
        """Step 8: 结果处理"""
        logger.info("step_handle_result", workflow_id=ctx.workflow_id)
        
        if self.gitlab and ctx.mr_iid:
            gate_status = GateStatus(gate_data.get("status", "pending"))
            
            await self.gitlab.update_mr_status(
                project_id=int(ctx.project_id),
                mr_iid=ctx.mr_iid,
                gate_result=type('obj', (object,), {
                    'status': gate_status,
                    'test_results': {'commit_sha': ctx.commit_sha},
                    'block_reason': gate_data.get('block_reason')
                })()
            )
            
            if gate_data.get("action") == "block":
                await self.gitlab.block_mr(
                    project_id=int(ctx.project_id),
                    mr_iid=ctx.mr_iid,
                    reason=gate_data.get("block_reason", "质量门禁未通过")
                )
        
        if self.notification:
            status_emoji = "✅" if gate_data.get("status") == "passed" else "❌"
            
            await self.notification.notify(
                recipients=["dev-team"],
                subject=f"{status_emoji} 变更分析完成 - {gate_data.get('status')}",
                content=self._format_notification(ctx, gate_data, analysis),
                channel="dingtalk"
            )
    
    def _format_notification(
        self,
        ctx: WorkflowContext,
        gate_data: Dict,
        analysis: Dict
    ) -> str:
        """格式化通知内容"""
        status_emoji = "✅" if gate_data.get("status") == "passed" else "❌"
        
        content = f"""## {status_emoji} 变更分析完成

**工作流 ID**: {ctx.workflow_id}
**项目**: {ctx.project_id}
**分支**: {ctx.compare_branch} → {ctx.base_branch}
**风险等级**: {analysis.get('risk_level', 'N/A')}
**状态**: {gate_data.get('status')}
**决策**: {gate_data.get('action')}
"""
        
        if gate_data.get("block_reason"):
            content += f"\n**原因**:\n{gate_data['block_reason']}\n"
        
        content += "\n---\n*AI 测试平台*"
        
        return content


async def trigger_change_analysis(
    background_tasks,
    project_id: str,
    base_branch: str,
    compare_branch: str,
    repo_url: str,
    mr_iid: Optional[int] = None,
    commits: Optional[List[str]] = None
) -> str:
    """触发变更分析（后台任务）"""
    from app.agents.change import agent as change_agent
    from app.agents.api import agent as api_agent
    from app.config.settings import settings
    
    ctx = WorkflowContext(
        project_id=project_id,
        base_branch=base_branch,
        compare_branch=compare_branch,
        repo_url=repo_url,
        mr_iid=mr_iid,
        commits=commits or []
    )
    
    quality_gate = QualityGate(config={})
    
    gitlab = None
    if settings.GITLAB_URL and settings.GITLAB_TOKEN:
        gitlab = GitLabIntegration(
            gitlab_url=settings.GITLAB_URL,
            token=settings.GITLAB_TOKEN
        )
    
    notification = NotificationService(config={
        "dingtalk_webhook": settings.DINGTALK_WEBHOOK
    })
    
    workflow = ChangeAnalysisWorkflow(
        change_agent=change_agent,
        api_agent=api_agent,
        quality_gate=quality_gate,
        gitlab=gitlab,
        notification=notification
    )
    
    background_tasks.add_task(workflow.run, ctx)
    
    return ctx.workflow_id
