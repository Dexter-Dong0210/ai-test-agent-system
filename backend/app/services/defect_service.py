"""
缺陷管理服务

核心功能：缺陷跟踪、外部系统集成、AI分析
"""
import httpx
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.defect import (
    Defect,
    DefectComment,
    DefectHistory,
    ExternalSystemConfig,
    DefectSeverity,
    DefectPriority,
    DefectStatus,
    ExternalSystem
)
from app.repositories.base import BaseRepository
from app.utils.exceptions import NotFoundException, BadRequestException
from app.config.settings import settings


class DefectRepository(BaseRepository[Defect]):
    """缺陷Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Defect, session)
    
    async def get_by_project(
        self,
        project_id: UUID,
        status: Optional[DefectStatus] = None,
        severity: Optional[DefectSeverity] = None,
        assignee: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 30
    ) -> List[Defect]:
        """获取项目的缺陷列表"""
        
        query = select(Defect).where(Defect.project_id == project_id)
        
        if status:
            query = query.where(Defect.status == status)
        
        if severity:
            query = query.where(Defect.severity == severity)
        
        if assignee:
            query = query.where(Defect.assignee == assignee)
        
        query = query.order_by(Defect.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_by_project(
        self,
        project_id: UUID,
        status: Optional[DefectStatus] = None
    ) -> int:
        """统计项目缺陷数量"""
        
        from sqlalchemy import func
        
        query = select(func.count(Defect.id)).where(Defect.project_id == project_id)
        
        if status:
            query = query.where(Defect.status == status)
        
        result = await self.session.execute(query)
        return result.scalar_one()


class DefectService:
    """缺陷管理服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DefectRepository(session)
    
    async def create_defect(
        self,
        project_id: UUID,
        title: str,
        description: str,
        severity: DefectSeverity = DefectSeverity.NORMAL,
        priority: DefectPriority = DefectPriority.MEDIUM,
        test_result_id: Optional[UUID] = None,
        **kwargs
    ) -> Defect:
        """创建缺陷"""
        
        defect = Defect(
            project_id=project_id,
            title=title,
            description=description,
            severity=severity,
            priority=priority,
            test_result_id=test_result_id,
            module=kwargs.get("module"),
            environment=kwargs.get("environment"),
            steps_to_reproduce=kwargs.get("steps_to_reproduce"),
            expected_result=kwargs.get("expected_result"),
            actual_result=kwargs.get("actual_result"),
            reporter=kwargs.get("reporter"),
            tags=kwargs.get("tags", [])
        )
        
        self.session.add(defect)
        await self.session.commit()
        
        # 记录历史
        await self._record_history(defect.id, "status", None, DefectStatus.NEW.value, kwargs.get("reporter"))
        
        return defect
    
    async def get_defect(self, defect_id: UUID) -> Defect:
        """获取缺陷详情"""
        
        defect = await self.repo.get(defect_id)
        if not defect:
            raise NotFoundException(f"缺陷 {defect_id} 不存在")
        
        return defect
    
    async def update_defect(
        self,
        defect_id: UUID,
        user_id: UUID,
        **kwargs
    ) -> Defect:
        """更新缺陷"""
        
        defect = await self.get_defect(defect_id)
        
        # 记录变更历史
        for key, value in kwargs.items():
            if hasattr(defect, key) and value is not None:
                old_value = getattr(defect, key)
                if old_value != value:
                    await self._record_history(defect_id, key, old_value, value, user_id)
                    setattr(defect, key, value)
        
        await self.session.commit()
        
        return defect
    
    async def change_status(
        self,
        defect_id: UUID,
        new_status: DefectStatus,
        user_id: UUID,
        comment: Optional[str] = None
    ) -> Defect:
        """更改缺陷状态"""
        
        defect = await self.get_defect(defect_id)
        
        old_status = defect.status
        defect.status = new_status
        
        # 记录状态变更历史
        await self._record_history(defect_id, "status", old_status.value, new_status.value, user_id)
        
        # 添加评论
        if comment:
            await self.add_comment(defect_id, user_id, comment, "status_change", old_status.value, new_status.value)
        
        # 更新时间戳
        if new_status == DefectStatus.RESOLVED:
            defect.resolved_at = datetime.now()
        elif new_status == DefectStatus.CLOSED:
            defect.closed_at = datetime.now()
        elif new_status == DefectStatus.REOPENED:
            defect.reopen_count += 1
        
        await self.session.commit()
        
        return defect
    
    async def add_comment(
        self,
        defect_id: UUID,
        user_id: UUID,
        content: str,
        comment_type: str = "comment",
        old_status: Optional[str] = None,
        new_status: Optional[str] = None
    ) -> DefectComment:
        """添加评论"""
        
        comment = DefectComment(
            defect_id=defect_id,
            content=content,
            comment_type=comment_type,
            old_status=old_status,
            new_status=new_status,
            author_id=user_id
        )
        
        self.session.add(comment)
        
        # 更新评论数
        defect = await self.get_defect(defect_id)
        defect.comment_count += 1
        
        await self.session.commit()
        
        return comment
    
    async def sync_to_jira(self, defect_id: UUID) -> Dict:
        """同步到Jira"""
        
        defect = await self.get_defect(defect_id)
        
        # 获取Jira配置
        config = await self._get_external_config(defect.project_id, ExternalSystem.JIRA)
        if not config:
            raise BadRequestException("未配置Jira集成")
        
        # 构造Jira请求
        jira_data = {
            "fields": {
                "project": {"key": config.project_key},
                "summary": defect.title,
                "description": defect.description,
                "issuetype": {"name": "Bug"},
                "priority": {"name": self._map_jira_priority(defect.priority)},
                "labels": defect.tags
            }
        }
        
        try:
            # 调用Jira API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.api_url}/issue",
                    json=jira_data,
                    auth=(config.username, config.password),
                    headers={"Content-Type": "application/json"}
                )
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                # 更新缺陷信息
                defect.external_system = ExternalSystem.JIRA
                defect.external_key = result["key"]
                defect.external_url = f"{config.api_url}/browse/{result['key']}"
                defect.synced_at = datetime.now()
                
                await self.session.commit()
                
                return {
                    "success": True,
                    "external_key": result["key"],
                    "external_url": defect.external_url
                }
            else:
                return {
                    "success": False,
                    "error": f"Jira API返回错误: {response.status_code}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def ai_analyze_root_cause(self, defect_id: UUID) -> Dict:
        """AI分析根因（集成LLM）"""
        
        defect = await self.get_defect(defect_id)
        
        # 构造分析提示词
        prompt = f"""
分析以下缺陷的根本原因并提供修复建议：

缺陷标题：{defect.title}
缺陷描述：{defect.description}
严重程度：{defect.severity.value}
重现步骤：{defect.steps_to_reproduce}
预期结果：{defect.expected_result}
实际结果：{defect.actual_result}

请提供：
1. 根本原因分析
2. 建议的修复方案
3. 预估修复时间
"""
        
        # TODO: 调用LLM进行分析
        # 这里需要集成LangChain/LangGraph
        
        # 模拟AI分析结果
        analysis = {
            "root_cause": "需要调用AI模型进行分析",
            "suggested_fix": "建议集成LLM进行智能分析",
            "confidence": 0.85
        }
        
        # 更新缺陷
        defect.ai_root_cause = analysis["root_cause"]
        defect.ai_suggested_fix = analysis["suggested_fix"]
        defect.ai_confidence = analysis["confidence"]
        
        await self.session.commit()
        
        return analysis
    
    async def get_statistics(self, project_id: UUID) -> Dict:
        """获取缺陷统计"""
        
        # 按状态统计
        status_counts = {}
        for status in DefectStatus:
            count = await self.repo.count_by_project(project_id, status)
            status_counts[status.value] = count
        
        # 按严重程度统计
        severity_counts = {}
        for severity in DefectSeverity:
            defects = await self.session.execute(
                select(Defect).where(
                    and_(
                        Defect.project_id == project_id,
                        Defect.severity == severity
                    )
                )
            )
            severity_counts[severity.value] = len(defects.scalars().all())
        
        return {
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "by_severity": severity_counts
        }
    
    async def _record_history(
        self,
        defect_id: UUID,
        field: str,
        old_value: Optional[str],
        new_value: Optional[str],
        user_id: UUID
    ):
        """记录变更历史"""
        
        history = DefectHistory(
            defect_id=defect_id,
            field=field,
            old_value=str(old_value) if old_value else None,
            new_value=str(new_value) if new_value else None,
            changed_by=user_id
        )
        
        self.session.add(history)
    
    async def _get_external_config(
        self,
        project_id: UUID,
        system: ExternalSystem
    ) -> Optional[ExternalSystemConfig]:
        """获取外部系统配置"""
        
        result = await self.session.execute(
            select(ExternalSystemConfig).where(
                and_(
                    ExternalSystemConfig.project_id == project_id,
                    ExternalSystemConfig.system_type == system
                )
            )
        )
        
        return result.scalar_one_or_none()
    
    def _map_jira_priority(self, priority: DefectPriority) -> str:
        """映射到Jira优先级"""
        
        mapping = {
            DefectPriority.URGENT: "Highest",
            DefectPriority.HIGH: "High",
            DefectPriority.MEDIUM: "Medium",
            DefectPriority.LOW: "Low"
        }
        
        return mapping.get(priority, "Medium")