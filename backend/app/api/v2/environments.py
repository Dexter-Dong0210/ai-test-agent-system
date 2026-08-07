"""
测试环境管理API

核心功能：环境配置、切换、健康检查
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSessionDep, CurrentUserIdDep
from app.models.environment import EnvironmentType, EnvironmentStatus, AuthType
from app.services.environment_service import EnvironmentService
from app.schemas.common import SuccessResponse, MessageResponse


router = APIRouter(prefix="/projects/{project_identifier}/environments", tags=["测试环境管理"])


# ==================== Schema ====================

class EnvironmentCreate(BaseModel):
    """创建环境请求"""
    name: str = Field(..., description="环境名称")
    code: str = Field(..., description="环境代码")
    base_url: str = Field(..., description="基础URL")
    env_type: EnvironmentType = Field(default=EnvironmentType.TESTING)
    database_config: dict = Field(default={})
    auth_type: AuthType = Field(default=AuthType.NONE)
    auth_config: dict = Field(default={})
    health_check_url: Optional[str] = None
    variables: dict = Field(default={})


class EnvironmentUpdate(BaseModel):
    """更新环境请求"""
    name: Optional[str] = None
    base_url: Optional[str] = None
    database_config: Optional[dict] = None
    auth_config: Optional[dict] = None
    request_config: Optional[dict] = None
    health_check_url: Optional[str] = None
    variables: Optional[dict] = None
    status: Optional[EnvironmentStatus] = None


class EnvironmentInfo(BaseModel):
    """环境信息"""
    id: UUID
    name: str
    code: str
    base_url: str
    env_type: EnvironmentType
    status: EnvironmentStatus
    auth_type: AuthType
    is_default: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    response_time: Optional[int] = None
    status_code: Optional[int] = None
    checked_at: str
    error: Optional[str] = None


# ==================== API端点 ====================

@router.post("", response_model=EnvironmentInfo, status_code=status.HTTP_201_CREATED)
async def create_environment(
    project_identifier: str,
    request: EnvironmentCreate,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """创建测试环境"""
    
    # TODO: 从project_identifier获取project_id
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = EnvironmentService(session)
    
    env = await service.create_environment(
        project_id=project_id,
        created_by=current_user_id,
        **request.model_dump()
    )
    
    return EnvironmentInfo.from_orm(env)


@router.get("", response_model=List[EnvironmentInfo])
async def list_environments(
    project_identifier: str,
    session: DbSessionDep,
    env_type: Optional[EnvironmentType] = Query(None),
    status: Optional[EnvironmentStatus] = Query(None)
):
    """获取环境列表"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = EnvironmentService(session)
    
    envs = await service.list_environments(project_id, env_type, status)
    
    return [EnvironmentInfo.from_orm(env) for env in envs]


@router.get("/{env_id}", response_model=EnvironmentInfo)
async def get_environment(
    project_identifier: str,
    env_id: UUID,
    session: DbSessionDep
):
    """获取环境详情"""
    
    service = EnvironmentService(session)
    
    env = await service.get_environment(env_id)
    
    return EnvironmentInfo.from_orm(env)


@router.put("/{env_id}", response_model=EnvironmentInfo)
async def update_environment(
    project_identifier: str,
    env_id: UUID,
    request: EnvironmentUpdate,
    session: DbSessionDep
):
    """更新环境配置"""
    
    service = EnvironmentService(session)
    
    env = await service.update_environment(env_id, **request.model_dump(exclude_unset=True))
    
    return EnvironmentInfo.from_orm(env)


@router.post("/{env_id}/switch", response_model=MessageResponse)
async def switch_environment(
    project_identifier: str,
    env_id: UUID,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """切换环境"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = EnvironmentService(session)
    
    await service.switch_environment(project_id, env_id, current_user_id)
    
    return MessageResponse(
        success=True,
        message=f"环境 {env_id} 已切换为默认环境"
    )


@router.post("/{env_id}/health-check", response_model=HealthCheckResponse)
async def health_check(
    project_identifier: str,
    env_id: UUID,
    session: DbSessionDep
):
    """环境健康检查"""
    
    service = EnvironmentService(session)
    
    result = await service.health_check(env_id)
    
    return HealthCheckResponse(**result)


@router.post("/{env_id}/clone", response_model=EnvironmentInfo)
async def clone_environment(
    project_identifier: str,
    env_id: UUID,
    new_name: str = Query(...),
    new_code: str = Query(...),
    session: DbSessionDep
):
    """克隆环境配置"""
    
    service = EnvironmentService(session)
    
    new_env = await service.clone_environment(env_id, new_name, new_code)
    
    return EnvironmentInfo.from_orm(new_env)


@router.delete("/{env_id}", response_model=MessageResponse)
async def delete_environment(
    project_identifier: str,
    env_id: UUID,
    session: DbSessionDep
):
    """删除环境"""
    
    service = EnvironmentService(session)
    
    await service.delete_environment(env_id)
    
    return MessageResponse(
        success=True,
        message=f"环境 {env_id} 已删除"
    )