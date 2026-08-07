"""
门禁机制

职责：
1. 评估测试结果
2. 判断是否通过门禁
3. 阻断/放行决策
4. 更新 MR 状态
5. 发送通知
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
import httpx
import structlog

logger = structlog.get_logger()


class GateStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class GateAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    MANUAL_APPROVAL = "manual"


@dataclass
class GateResult:
    """门禁结果"""
    status: GateStatus
    action: GateAction
    test_results: Dict
    block_reason: Optional[str] = None
    approval_required: bool = False
    violations: List[str] = None
    
    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class QualityGate:
    """质量门禁"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rules = config.get("rules", self._default_rules())
    
    async def evaluate(
        self,
        test_results: Dict,
        analysis_result: Dict
    ) -> GateResult:
        """
        评估是否通过门禁
        
        Args:
            test_results: 测试执行结果
            analysis_result: 变更分析结果
        
        Returns:
            门禁决策结果
        """
        if test_results.get("status") == "skipped":
            return GateResult(
                status=GateStatus.SKIPPED,
                action=GateAction.ALLOW,
                test_results=test_results
            )
        
        pass_rate = self._calculate_pass_rate(test_results)
        coverage = test_results.get("coverage", 0)
        critical_failures = test_results.get("critical_failures", 0)
        
        risk_level = analysis_result.get("risk_level", "LOW")
        rules = self._get_rules_for_risk(risk_level)
        
        violations = []
        
        if pass_rate < rules.get("min_pass_rate", 100):
            violations.append(f"测试通过率 {pass_rate:.1f}% < {rules['min_pass_rate']}%")
        
        if coverage < rules.get("min_coverage", 0):
            violations.append(f"覆盖率 {coverage:.1f}% < {rules['min_coverage']}%")
        
        if critical_failures > 0:
            violations.append(f"存在 {critical_failures} 个严重级别测试失败")
        
        if test_results.get("failed", 0) > 0 and risk_level in ["HIGH", "CRITICAL"]:
            violations.append(f"存在 {test_results['failed']} 个测试失败")
        
        if not violations:
            return GateResult(
                status=GateStatus.PASSED,
                action=GateAction.ALLOW,
                test_results=test_results
            )
        
        action = rules.get("action", "block")
        require_approval = rules.get("require_approval", False)
        
        if action == "block":
            return GateResult(
                status=GateStatus.FAILED,
                action=GateAction.BLOCK,
                test_results=test_results,
                block_reason="\n".join(violations),
                violations=violations
            )
        elif action == "warn":
            return GateResult(
                status=GateStatus.FAILED,
                action=GateAction.WARN,
                test_results=test_results,
                block_reason="\n".join(violations),
                violations=violations
            )
        else:
            if require_approval:
                return GateResult(
                    status=GateStatus.FAILED,
                    action=GateAction.MANUAL_APPROVAL,
                    test_results=test_results,
                    block_reason="\n".join(violations),
                    approval_required=True,
                    violations=violations
                )
            
            return GateResult(
                status=GateStatus.PASSED,
                action=GateAction.ALLOW,
                test_results=test_results
            )
    
    def _default_rules(self) -> Dict:
        """默认规则"""
        return {
            "LOW": {"min_pass_rate": 80, "min_coverage": 0, "action": "allow"},
            "MEDIUM": {"min_pass_rate": 90, "min_coverage": 50, "action": "warn"},
            "HIGH": {"min_pass_rate": 100, "min_coverage": 70, "action": "block"},
            "CRITICAL": {
                "min_pass_rate": 100,
                "min_coverage": 80,
                "action": "block",
                "require_approval": True
            }
        }
    
    def _get_rules_for_risk(self, risk_level: str) -> Dict:
        """获取对应风险等级的规则"""
        return self.rules.get(risk_level, self.rules["LOW"])
    
    def _calculate_pass_rate(self, test_results: Dict) -> float:
        """计算测试通过率"""
        total = test_results.get("total", 0)
        passed = test_results.get("passed", 0)
        
        if total == 0:
            return 100.0
        
        return (passed / total) * 100


class GitLabIntegration:
    """GitLab 集成"""
    
    def __init__(self, gitlab_url: str, token: str):
        self.gitlab_url = gitlab_url.rstrip("/")
        self.token = token
        self.headers = {"PRIVATE-TOKEN": token}
    
    async def update_mr_status(
        self,
        project_id: int,
        mr_iid: int,
        gate_result: GateResult
    ):
        """更新 MR 状态"""
        state_map = {
            GateStatus.PENDING: "pending",
            GateStatus.RUNNING: "running",
            GateStatus.PASSED: "success",
            GateStatus.FAILED: "failed",
            GateStatus.SKIPPED: "canceled"
        }
        
        url = f"{self.gitlab_url}/api/v4/projects/{project_id}/statuses/{gate_result.test_results.get('commit_sha', 'HEAD')}"
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    url,
                    headers=self.headers,
                    json={
                        "state": state_map[gate_result.status],
                        "name": "AI Quality Gate",
                        "description": gate_result.block_reason or "Quality gate passed",
                        "target_url": f"{self.gitlab_url}/-/merge_requests/{mr_iid}"
                    },
                    timeout=30
                )
            except Exception as e:
                logger.error("gitlab_status_update_failed", error=str(e))
    
    async def add_mr_comment(
        self,
        project_id: int,
        mr_iid: int,
        comment: str
    ):
        """添加 MR 评论"""
        url = f"{self.gitlab_url}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    url,
                    headers=self.headers,
                    json={"body": comment},
                    timeout=30
                )
            except Exception as e:
                logger.error("gitlab_comment_failed", error=str(e))
    
    async def block_mr(
        self,
        project_id: int,
        mr_iid: int,
        reason: str
    ):
        """阻断 MR"""
        comment = f"""🚫 **质量门禁未通过**

{reason}

请修复以上问题后重新提交。

---
*此消息由 AI 测试平台自动生成*
"""
        await self.add_mr_comment(project_id, mr_iid, comment)


class NotificationService:
    """通知服务"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    async def notify(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        channel: str = "dingtalk"
    ):
        """发送通知"""
        if channel == "dingtalk":
            await self._send_dingtalk(recipients, subject, content)
        elif channel == "feishu":
            await self._send_feishu(recipients, subject, content)
        elif channel == "email":
            await self._send_email(recipients, subject, content)
    
    async def _send_dingtalk(
        self,
        webhook: str,
        title: str,
        content: str
    ):
        """发送钉钉通知"""
        if not webhook:
            webhook = self.config.get("dingtalk_webhook")
        
        if not webhook:
            return
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    webhook,
                    json={
                        "msgtype": "markdown",
                        "markdown": {
                            "title": title,
                            "text": content
                        }
                    },
                    timeout=10
                )
            except Exception as e:
                logger.error("dingtalk_notify_failed", error=str(e))
    
    async def _send_feishu(
        self,
        webhook: str,
        title: str,
        content: str
    ):
        """发送飞书通知"""
        if not webhook:
            webhook = self.config.get("feishu_webhook")
        
        if not webhook:
            return
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    webhook,
                    json={
                        "msg_type": "interactive",
                        "card": {
                            "header": {
                                "title": {"tag": "plain_text", "content": title}
                            },
                            "elements": [
                                {"tag": "markdown", "content": content}
                            ]
                        }
                    },
                    timeout=10
                )
            except Exception as e:
                logger.error("feishu_notify_failed", error=str(e))
    
    async def _send_email(
        self,
        recipients: List[str],
        subject: str,
        content: str
    ):
        """发送邮件通知"""
        pass
