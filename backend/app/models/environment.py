"""
测试环境管理模型

支持多环境配置、动态切换、健康检查
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class EnvironmentType(str, enum.Enum):
    """环境类型"""
    DEVELOPMENT = "development"      # 开发环境
    TESTING = "testing"              # 测试环境
    STAGING = "staging"              # 预发布环境
    PRODUCTION = "production"        # 生产环境
    SANDBOX = "sandbox"              # 沙箱环境


class EnvironmentStatus(str, enum.Enum):
    """环境状态"""
    ACTIVE = "active"                # 活跃
    MAINTENANCE = "maintenance"      # 维护中
    OFFLINE = "offline"              # 离线
    ERROR = "error"                  # 异常


class AuthType(str, enum.Enum):
    """认证类型"""
    NONE = "none"                    # 无认证
    TOKEN = "token"                  # Token认证
    BASIC = "basic"                  # Basic Auth
    OAUTH2 = "oauth2"                # OAuth2
    API_KEY = "api_key"              # API Key


class TestEnvironment(Base):
    """测试环境"""
    __tablename__ = "test_environments"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 环境类型和状态
    env_type: Mapped[EnvironmentType] = mapped_column(
        SQLEnum(EnvironmentType),
        default=EnvironmentType.TESTING,
        nullable=False
    )
    status: Mapped[EnvironmentStatus] = mapped_column(
        SQLEnum(EnvironmentStatus),
        default=EnvironmentStatus.ACTIVE,
        nullable=False
    )
    
    # 基础配置
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_gateway: Mapped[Optional[str]] = mapped_column(String(500))
    
    # 数据库配置（加密存储）
    database_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # Redis配置
    redis_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # 认证配置
    auth_type: Mapped[AuthType] = mapped_column(
        SQLEnum(AuthType),
        default=AuthType.NONE,
        nullable=False
    )
    auth_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # 请求配置
    request_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # 健康检查配置
    health_check_url: Mapped[Optional[str]] = mapped_column(String(500))
    health_check_interval: Mapped[int] = mapped_column(Integer, default=300)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    health_status: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # 环境变量
    variables: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # 使用统计
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    
    # 优先级
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="environments")


class EnvironmentVariable(Base):
    """环境变量"""
    __tablename__ = "environment_variables"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    environment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("test_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 变量类型
    var_type: Mapped[str] = mapped_column(String(20), default="static")
    script: Mapped[Optional[str]] = mapped_column(Text)
    
    # 是否敏感
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnvironmentHealthLog(Base):
    """环境健康检查日志"""
    __tablename__ = "environment_health_logs"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    environment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("test_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    response_time: Mapped[Optional[int]] = mapped_column(Integer)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())