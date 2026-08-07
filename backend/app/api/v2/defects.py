"""
缺陷管理API

核心功能：缺陷跟踪、状态流转、外部集成
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSessionDep, CurrentUserIdDep
from app.models.defect import (
    DefectSeverity,
    DefectPriority,
    DefectStatus,
    ExternalSystem
)
from app.services.defect_service import DefectService
from app.schemas.common import SuccessResponse, MessageResponse


router = APIRouter(prefix="/projects/{project_identifier}/defects", tags=["缺陷管理"])


# ==================== Schema ====================

class DefectCreate(BaseModel):
    """创建缺陷请求"""
    title: str = Field(..., description="缺陷标题")
    description: str = Field(..., description="缺陷描述")
    severity: DefectSeverity = Field(default=DefectSeverity.NORMAL)
    priority: DefectPriority = Field(default=DefectPriority.MEDIUM)
    test_result_id: Optional[UUID] = None
    module: Optional[str] = None
    environment: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    tags: List[str] = Field(default=[])


class DefectUpdate(BaseModel):
    """更新缺陷请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[DefectSeverity] = None
    priority: Optional[DefectPriority] = None
    module: Optional[str] = None
    environment: Optional[str] = None
    assignee: Optional[UUID] = None


class DefectInfo(BaseModel):
    """缺陷信息"""
    id: UUID
    title: str
    description: str
    severity: DefectSeverity
    priority: DefectPriority
    status: DefectStatus
    module: Optional[str]
    environment: Optional[str]
    external_key: Optional[str]
    external_url: Optional[str]
    ai_root_cause: Optional[str]
    ai_suggested_fix: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DefectStatistics(BaseModel):
    """缺陷统计"""
    total: int
    by_status: dict
    by_severity: dict


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., description="评论内容")


# ==================== API端点 ====================

@router.post("", response_model=DefectInfo, status_code=status.HTTP_201_CREATED)
async def create_defect(
    project_identifier: str,
    request: DefectCreate,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """创建缺陷"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = DefectService(session)
    
    defect = await service.create_defect(
        project_id=project_id,
        reporter=current_user_id,
        **request.model_dump()
    )
    
    return DefectInfo.from_orm(defect)


@router.get("", response_model=List[DefectInfo])
async def list_defects(
    project_identifier: str,
    session: DbSessionDep,
    status: Optional[DefectStatus] = Query(None),
    severity: Optional[DefectSeverity] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100)
):
    """获取缺陷列表"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = DefectService(session)
    
    defects = await service.repo.get_by_project(project_id, status, severity, skip=skip, limit=limit)
    
    return [DefectInfo.from_orm(d) for d in defects]


@router.get("/statistics", response_model=DefectStatistics)
async def get_statistics(
    project_identifier: str,
    session: DbSessionDep
):
    """获取缺陷统计"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = DefectService(session)
    
    stats = await service.get_statistics(project_id)
    
    return DefectStatistics(**stats)


@router.get("/{defect_id}", response_model=DefectInfo)
async def get_defect(
    project_identifier: str,
    defect_id: UUID,
    session: DbSessionDep
):
    """获取缺陷详情"""
    
    service = DefectService(session)
    
    defect = await service.get_defect(defect_id)
    
    return DefectInfo.from_orm(defect)


@router.put("/{defect_id}", response_model=DefectInfo)
async def update_defect(
    project_identifier: str,
    defect_id: UUID,
    request: DefectUpdate,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """更新缺陷"""
    
    service = DefectService(session)
    
    defect = await service.update_defect(
        defect_id,
        current_user_id,
        **request.model_dump(exclude_unset=True)
    )
    
    return DefectInfo.from_orm(defect)


@router.post("/{defect_id}/status", response_model=DefectInfo)
async def change_status(
    project_identifier: str,
    defect_id: UUID,
    new_status: DefectStatus,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep,
    comment: Optional[str] = Query(None)
):
    """更改缺陷状态"""
    
    service = DefectService(session)
    
    defect = await service.change_status(defect_id, new_status, current_user_id, comment)
    
    return DefectInfo.from_orm(defect)


@router.post("/{defect_id}/comments", response_model=MessageResponse)
async def add_comment(
    project_identifier: str,
    defect_id: UUID,
    request: CommentCreate,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """添加评论"""
    
    service = DefectService(session)
    
    await service.add_comment(defect_id, current_user_id, request.content)
    
    return MessageResponse(
        success=True,
        message="评论添加成功"
    )


@router.post("/{defect_id}/sync/jira", response_model=dict)
async def sync_to_jira(
    project_identifier: str,
    defect_id: UUID,
    session: DbSessionDep
):
    """同步到Jira"""
    
    service = DefectService(session)
    
    result = await service.sync_to_jira(defect_id)
    
    return result


@router.post("/{defect_id}/ai-analyze", response_model=dict)
async def ai_analyze(
    project_identifier: str,
    defect_id: UUID,
    session: DbSessionDep
):
    """AI分析根因"""
    
    service = DefectService(session)
    
    result = await service.ai_analyze_root_cause(defect_id)
    
    return result


@router.delete("/{defect_id}", response_model=MessageResponse)
async def delete_defect(
    project_identifier: str,
    defect_id: UUID,
    session: DbSessionDep
):
    """删除缺陷"""
    
    service = DefectService(session)
    
    defect = await service.get_defect(defect_id)
    await service.repo.delete(defect)
    
    return MessageResponse(
        success=True,
        message=f"缺陷 {defect_id} 已删除"
    )