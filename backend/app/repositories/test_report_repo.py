"""
测试报告Repository
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_report import TestReport, ReportStatus
from app.repositories.base import BaseRepository


class TestReportRepository(BaseRepository[TestReport]):
    """测试报告Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TestReport, session)
    
    async def get_by_project(
        self,
        project_id: UUID,
        status: Optional[ReportStatus] = None,
        skip: int = 0,
        limit: int = 30
    ) -> List[TestReport]:
        """获取项目的报告列表"""
        
        query = select(TestReport).where(TestReport.project_id == project_id)
        
        if status:
            query = query.where(TestReport.status == status)
        
        query = query.order_by(TestReport.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_by_project(
        self,
        project_id: UUID,
        status: Optional[ReportStatus] = None
    ) -> int:
        """统计项目的报告数量"""
        
        from sqlalchemy import func
        
        query = select(func.count(TestReport.id)).where(TestReport.project_id == project_id)
        
        if status:
            query = query.where(TestReport.status == status)
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def get_by_access_token(self, access_token: str) -> Optional[TestReport]:
        """通过访问令牌获取报告"""
        
        result = await self.session.execute(
            select(TestReport).where(TestReport.access_token == access_token)
        )
        return result.scalar_one_or_none()
    
    async def delete_expired_reports(self) -> int:
        """删除过期报告"""
        
        from datetime import datetime
        
        result = await self.session.execute(
            select(TestReport).where(
                and_(
                    TestReport.expires_at < datetime.now(),
                    TestReport.expires_at.isnot(None)
                )
            )
        )
        expired_reports = result.scalars().all()
        
        count = 0
        for report in expired_reports:
            await self.session.delete(report)
            count += 1
        
        await self.session.commit()
        
        return count