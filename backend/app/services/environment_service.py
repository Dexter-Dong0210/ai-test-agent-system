"""
测试环境管理服务

核心功能：环境配置、健康检查、环境切换
"""
import httpx
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.environment import (
    TestEnvironment,
    EnvironmentVariable,
    EnvironmentHealthLog,
    EnvironmentType,
    EnvironmentStatus,
    AuthType
)
from app.repositories.base import BaseRepository
from app.utils.exceptions import NotFoundException, BadRequestException
from app.config.settings import settings


class EnvironmentRepository(BaseRepository[TestEnvironment]):
    """环境Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TestEnvironment, session)
    
    async def get_by_project(
        self,
        project_id: UUID,
        env_type: Optional[EnvironmentType] = None,
        status: Optional[EnvironmentStatus] = None
    ) -> List[TestEnvironment]:
        """获取项目的环境列表"""
        
        query = select(TestEnvironment).where(
            TestEnvironment.project_id == project_id
        )
        
        if env_type:
            query = query.where(TestEnvironment.env_type == env_type)
        
        if status:
            query = query.where(TestEnvironment.status == status)
        
        query = query.order_by(TestEnvironment.priority, TestEnvironment.created_at)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_default(self, project_id: UUID) -> Optional[TestEnvironment]:
        """获取默认环境"""
        
        result = await self.session.execute(
            select(TestEnvironment).where(
                and_(
                    TestEnvironment.project_id == project_id,
                    TestEnvironment.is_default == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def set_default(self, project_id: UUID, env_id: UUID) -> None:
        """设置默认环境"""
        
        # 先清除其他默认环境
        envs = await self.get_by_project(project_id)
        for env in envs:
            env.is_default = False
        
        # 设置新的默认环境
        target_env = await self.get(env_id)
        if target_env:
            target_env.is_default = True
        
        await self.session.commit()


class EnvironmentService:
    """环境管理服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EnvironmentRepository(session)
    
    async def create_environment(
        self,
        project_id: UUID,
        name: str,
        code: str,
        base_url: str,
        env_type: EnvironmentType = EnvironmentType.TESTING,
        **kwargs
    ) -> TestEnvironment:
        """创建测试环境"""
        
        # 检查code是否重复
        existing = await self.session.execute(
            select(TestEnvironment).where(TestEnvironment.code == code)
        )
        if existing.scalar_one_or_none():
            raise BadRequestException(f"环境代码 '{code}' 已存在")
        
        # 创建环境
        env = TestEnvironment(
            project_id=project_id,
            name=name,
            code=code,
            base_url=base_url,
            env_type=env_type,
            database_config=kwargs.get("database_config", {}),
            redis_config=kwargs.get("redis_config", {}),
            auth_type=kwargs.get("auth_type", AuthType.NONE),
            auth_config=kwargs.get("auth_config", {}),
            request_config=kwargs.get("request_config", {}),
            health_check_url=kwargs.get("health_check_url"),
            variables=kwargs.get("variables", {}),
            created_by=kwargs.get("created_by")
        )
        
        self.session.add(env)
        await self.session.commit()
        
        return env
    
    async def get_environment(self, env_id: UUID) -> TestEnvironment:
        """获取环境详情"""
        
        env = await self.repo.get(env_id)
        if not env:
            raise NotFoundException(f"环境 {env_id} 不存在")
        
        return env
    
    async def list_environments(
        self,
        project_id: UUID,
        env_type: Optional[EnvironmentType] = None,
        status: Optional[EnvironmentStatus] = None
    ) -> List[TestEnvironment]:
        """获取环境列表"""
        
        return await self.repo.get_by_project(project_id, env_type, status)
    
    async def update_environment(
        self,
        env_id: UUID,
        **kwargs
    ) -> TestEnvironment:
        """更新环境配置"""
        
        env = await self.get_environment(env_id)
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(env, key) and value is not None:
                setattr(env, key, value)
        
        await self.session.commit()
        
        return env
    
    async def delete_environment(self, env_id: UUID) -> None:
        """删除环境"""
        
        env = await self.get_environment(env_id)
        await self.repo.delete(env)
    
    async def switch_environment(
        self,
        project_id: UUID,
        env_id: UUID,
        user_id: UUID
    ) -> TestEnvironment:
        """切换环境"""
        
        # 设置为默认环境
        await self.repo.set_default(project_id, env_id)
        
        # 记录使用
        env = await self.get_environment(env_id)
        env.last_used_at = datetime.now()
        env.usage_count += 1
        env.last_used_by = user_id
        
        await self.session.commit()
        
        return env
    
    async def health_check(self, env_id: UUID) -> Dict:
        """环境健康检查"""
        
        env = await self.get_environment(env_id)
        
        if not env.health_check_url:
            return {
                "status": "unknown",
                "message": "未配置健康检查URL"
            }
        
        try:
            # 发送健康检查请求
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(env.health_check_url)
            
            end_time = datetime.now()
            response_time = int((end_time - start_time).total_seconds() * 1000)
            
            # 判断健康状态
            is_healthy = 200 <= response.status_code < 300
            
            health_status = {
                "status": "healthy" if is_healthy else "unhealthy",
                "status_code": response.status_code,
                "response_time": response_time,
                "checked_at": datetime.now().isoformat()
            }
            
            # 更新环境状态
            env.last_health_check = datetime.now()
            env.health_status = health_status
            
            if not is_healthy:
                env.status = EnvironmentStatus.ERROR
            
            # 记录健康检查日志
            log = EnvironmentHealthLog(
                environment_id=env.id,
                status="healthy" if is_healthy else "unhealthy",
                response_time=response_time,
                status_code=response.status_code,
                details={"url": env.health_check_url}
            )
            self.session.add(log)
            
            await self.session.commit()
            
            return health_status
        
        except Exception as e:
            error_status = {
                "status": "error",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
            
            env.status = EnvironmentStatus.ERROR
            env.health_status = error_status
            env.last_health_check = datetime.now()
            
            # 记录错误日志
            log = EnvironmentHealthLog(
                environment_id=env.id,
                status="error",
                error_message=str(e),
                details={"url": env.health_check_url}
            )
            self.session.add(log)
            
            await self.session.commit()
            
            return error_status
    
    async def clone_environment(
        self,
        env_id: UUID,
        new_name: str,
        new_code: str
    ) -> TestEnvironment:
        """克隆环境配置"""
        
        source_env = await self.get_environment(env_id)
        
        # 创建新环境
        new_env = await self.create_environment(
            project_id=source_env.project_id,
            name=new_name,
            code=new_code,
            base_url=source_env.base_url,
            env_type=source_env.env_type,
            database_config=source_env.database_config,
            redis_config=source_env.redis_config,
            auth_type=source_env.auth_type,
            auth_config=source_env.auth_config,
            request_config=source_env.request_config,
            health_check_url=source_env.health_check_url,
            variables=source_env.variables
        )
        
        return new_env
    
    async def export_config(self, env_id: UUID) -> Dict:
        """导出环境配置"""
        
        env = await self.get_environment(env_id)
        
        config = {
            "name": env.name,
            "code": env.code,
            "base_url": env.base_url,
            "env_type": env.env_type.value,
            "auth_type": env.auth_type.value,
            "request_config": env.request_config,
            "variables": env.variables,
            "health_check_url": env.health_check_url
        }
        
        return config
    
    async def import_config(
        self,
        project_id: UUID,
        config: Dict
    ) -> TestEnvironment:
        """导入环境配置"""
        
        return await self.create_environment(
            project_id=project_id,
            name=config["name"],
            code=config["code"],
            base_url=config["base_url"],
            env_type=EnvironmentType(config.get("env_type", "testing")),
            auth_type=AuthType(config.get("auth_type", "none")),
            request_config=config.get("request_config", {}),
            variables=config.get("variables", {}),
            health_check_url=config.get("health_check_url")
        )