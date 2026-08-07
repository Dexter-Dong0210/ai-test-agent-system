"""
测试数据管理API

核心功能：数据池、Mock数据、数据生成
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSessionDep, CurrentUserIdDep
from app.models.test_data import DataType, DataSource, DataStatus
from app.services.test_data_service import TestDataService
from app.schemas.common import SuccessResponse, MessageResponse


router = APIRouter(prefix="/projects/{project_identifier}/test-data", tags=["测试数据管理"])


# ==================== Schema ====================

class DataCreate(BaseModel):
    """创建测试数据请求"""
    name: str = Field(..., description="数据名称")
    code: str = Field(..., description="数据代码")
    data_type: DataType = Field(default=DataType.CUSTOM)
    data_content: dict = Field(..., description="数据内容")
    description: Optional[str] = None
    tags: List[str] = Field(default=[])
    is_sensitive: bool = Field(default=False)
    sensitive_fields: List[str] = Field(default=[])


class DataUpdate(BaseModel):
    """更新测试数据请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    data_content: Optional[dict] = None
    tags: Optional[List[str]] = None
    status: Optional[DataStatus] = None


class DataInfo(BaseModel):
    """测试数据信息"""
    id: UUID
    name: str
    code: str
    data_type: DataType
    data_source: DataSource
    status: DataStatus
    is_sensitive: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MockConfigCreate(BaseModel):
    """创建Mock配置请求"""
    name: str
    api_endpoint: str
    http_method: str
    mock_data: dict
    mock_strategy: str = Field(default="static")
    response_delay: int = Field(default=0)
    status_code: int = Field(default=200)


class DataGenerateRequest(BaseModel):
    """数据生成请求"""
    template_id: UUID
    count: int = Field(default=10, ge=1, le=100)


class DataStatistics(BaseModel):
    """数据统计"""
    total: int
    by_type: dict
    by_status: dict


# ==================== API端点 ====================

@router.post("", response_model=DataInfo, status_code=status.HTTP_201_CREATED)
async def create_data(
    project_identifier: str,
    request: DataCreate,
    session: DbSessionDep,
    current_user_id: CurrentUserIdDep
):
    """创建测试数据"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    data = await service.create_data(
        project_id=project_id,
        created_by=current_user_id,
        **request.model_dump()
    )
    
    return DataInfo.from_orm(data)


@router.get("", response_model=List[DataInfo])
async def list_data(
    project_identifier: str,
    session: DbSessionDep,
    data_type: Optional[DataType] = Query(None),
    status: Optional[DataStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100)
):
    """获取测试数据列表"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    data_list = await service.repo.get_by_project(project_id, data_type, status, skip, limit)
    
    return [DataInfo.from_orm(d) for d in data_list]


@router.get("/statistics", response_model=DataStatistics)
async def get_statistics(
    project_identifier: str,
    session: DbSessionDep
):
    """获取数据统计"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    stats = await service.get_usage_statistics(project_id)
    
    return DataStatistics(**stats)


@router.get("/search", response_model=List[DataInfo])
async def search_data(
    project_identifier: str,
    q: str = Query(..., description="搜索关键词"),
    data_type: Optional[DataType] = Query(None),
    session: DbSessionDep = None
):
    """搜索测试数据"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    results = await service.search_data(project_id, q, data_type)
    
    return [DataInfo.from_orm(d) for d in results]


@router.get("/{data_id}", response_model=dict)
async def get_data(
    project_identifier: str,
    data_id: UUID,
    session: DbSessionDep
):
    """获取测试数据详情（自动脱敏）"""
    
    service = TestDataService(session)
    
    data = await service.get_data(data_id)
    
    # 应用脱敏
    masked_content = await service.mask_sensitive_data(data)
    
    return {
        "id": str(data.id),
        "name": data.name,
        "code": data.code,
        "data_type": data.data_type.value,
        "status": data.status.value,
        "data_content": masked_content,
        "is_sensitive": data.is_sensitive,
        "usage_count": data.usage_count,
        "created_at": data.created_at.isoformat()
    }


@router.put("/{data_id}", response_model=DataInfo)
async def update_data(
    project_identifier: str,
    data_id: UUID,
    request: DataUpdate,
    session: DbSessionDep
):
    """更新测试数据"""
    
    service = TestDataService(session)
    
    data = await service.update_data(data_id, **request.model_dump(exclude_unset=True))
    
    return DataInfo.from_orm(data)


@router.post("/{data_id}/link-testcase/{test_case_id}", response_model=MessageResponse)
async def link_test_case(
    project_identifier: str,
    data_id: UUID,
    test_case_id: UUID,
    session: DbSessionDep
):
    """关联测试用例"""
    
    service = TestDataService(session)
    
    await service.link_test_case(data_id, test_case_id)
    
    return MessageResponse(
        success=True,
        message="测试数据已关联测试用例"
    )


@router.post("/generate", response_model=List[DataInfo])
async def generate_data(
    project_identifier: str,
    request: DataGenerateRequest,
    session: DbSessionDep
):
    """批量生成测试数据"""
    
    service = TestDataService(session)
    
    generated = await service.generate_data_batch(request.template_id, request.count)
    
    return [DataInfo.from_orm(d) for d in generated]


# ==================== Mock数据管理 ====================

@router.post("/mock", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_mock_config(
    project_identifier: str,
    request: MockConfigCreate,
    session: DbSessionDep
):
    """创建Mock配置"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    mock = await service.create_mock_config(
        project_id=project_id,
        **request.model_dump()
    )
    
    return {
        "id": str(mock.id),
        "name": mock.name,
        "api_endpoint": mock.api_endpoint,
        "http_method": mock.http_method,
        "status": "created"
    }


@router.post("/mock/execute", response_model=dict)
async def execute_mock(
    project_identifier: str,
    api_endpoint: str,
    http_method: str,
    session: DbSessionDep
):
    """执行Mock请求"""
    
    project_id = UUID("00000000-0000-0000-0000-000000000001")
    
    service = TestDataService(session)
    
    response = await service.get_mock_response(project_id, api_endpoint, http_method)
    
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到匹配的Mock配置"
        )
    
    return response


@router.delete("/{data_id}", response_model=MessageResponse)
async def delete_data(
    project_identifier: str,
    data_id: UUID,
    session: DbSessionDep
):
    """删除测试数据"""
    
    service = TestDataService(session)
    
    data = await service.get_data(data_id)
    await service.repo.delete(data)
    
    return MessageResponse(
        success=True,
        message=f"测试数据 {data_id} 已删除"
    )