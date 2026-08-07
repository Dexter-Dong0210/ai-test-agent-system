"""
测试数据管理模型

支持数据池、Mock数据、数据生成、数据脱敏
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


class DataType(str, enum.Enum):
    """数据类型"""
    USER = "user"              # 用户数据
    ORDER = "order"            # 订单数据
    PRODUCT = "product"        # 商品数据
    PAYMENT = "payment"        # 支付数据
    INVENTORY = "inventory"    # 库存数据
    CUSTOM = "custom"          # 自定义数据


class DataSource(str, enum.Enum):
    """数据来源"""
    MANUAL = "manual"          # 手动创建
    DATABASE = "database"      # 数据库导入
    API = "api"                # API导入
    AI_GENERATED = "ai_generated"  # AI生成
    FILE = "file"              # 文件导入


class DataStatus(str, enum.Enum):
    """数据状态"""
    ACTIVE = "active"          # 可用
    INACTIVE = "inactive"      # 不可用
    EXPIRED = "expired"        # 已过期
    LOCKED = "locked"          # 已锁定（使用中）


class TestDataPool(Base):
    """测试数据池"""
    __tablename__ = "test_data_pools"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 数据分类
    data_type: Mapped[DataType] = mapped_column(
        SQLEnum(DataType),
        default=DataType.CUSTOM,
        nullable=False
    )
    data_source: Mapped[DataSource] = mapped_column(
        SQLEnum(DataSource),
        default=DataSource.MANUAL,
        nullable=False
    )
    
    # 数据内容
    data_content: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # 示例：
    # {
    #   "user_id": "user_001",
    #   "username": "testuser",
    #   "email": "test@example.com",
    #   "phone": "13800138000"
    # }
    
    # 元数据
    schema_definition: Mapped[dict] = mapped_column(JSONB, default=dict)
    # 定义数据结构：
    # {
    #   "fields": [
    #     {"name": "user_id", "type": "string", "required": true},
    #     {"name": "username", "type": "string", "required": true},
    #     {"name": "email", "type": "email", "required": true}
    #   ]
    # }
    
    # 标签和分类
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 敏感数据处理
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    sensitive_fields: Mapped[list] = mapped_column(JSONB, default=list)
    # ["password", "id_card", "phone"]
    
    # 状态和版本
    status: Mapped[DataStatus] = mapped_column(
        SQLEnum(DataStatus),
        default=DataStatus.ACTIVE,
        nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # 有效期
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_used_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    
    # 关联的测试用例
    linked_test_cases: Mapped[list] = mapped_column(JSONB, default=list)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="data_pools")


class MockDataConfig(Base):
    """Mock数据配置"""
    __tablename__ = "mock_data_configs"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # API配置
    api_endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    http_method: Mapped[str] = mapped_column(String(10), nullable=False)  # GET/POST/PUT/DELETE
    
    # Mock策略
    mock_strategy: Mapped[str] = mapped_column(String(20), default="static")  # static/random/script/ai
    # static: 固定返回
    # random: 随机返回
    # script: 脚本生成
    # ai: AI动态生成
    
    # Mock数据
    mock_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "status": "success",
    #   "data": {"user_id": "001", "name": "Test User"}
    # }
    
    # Mock脚本（如果strategy是script）
    mock_script: Mapped[Optional[str]] = mapped_column(Text)
    # 示例：
    # function generate() {
    #   return {
    #     user_id: faker.datatype.uuid(),
    #     name: faker.name.fullName()
    #   }
    # }
    
    # AI生成提示词
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text)
    
    # 响应配置
    response_delay: Mapped[int] = mapped_column(Integer, default=0)  # 毫秒
    response_headers: Mapped[dict] = mapped_column(JSONB, default=dict)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    
    # 条件匹配
    match_rules: Mapped[list] = mapped_column(JSONB, default=list)
    # [
    #   {"field": "user_id", "operator": "==", "value": "001"},
    #   {"field": "status", "operator": "in", "value": ["active", "pending"]}
    # ]
    
    # 启用状态
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 使用统计
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    last_hit_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DataGenerationTemplate(Base):
    """数据生成模板"""
    __tablename__ = "data_generation_templates"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 基本信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    data_type: Mapped[DataType] = mapped_column(SQLEnum(DataType), nullable=False)
    
    # 模板配置
    template_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "fields": [
    #     {"name": "user_id", "generator": "uuid"},
    #     {"name": "username", "generator": "username"},
    #     {"name": "email", "generator": "email"},
    #     {"name": "age", "generator": "number", "min": 18, "max": 65}
    #   ]
    # }
    
    # AI生成提示词
    ai_prompt: Mapped[Optional[str]] = mapped_column(Text)
    # "生成一个电商系统的测试用户数据，包含用户ID、用户名、邮箱、手机号、地址等信息"
    
    # 生成数量
    batch_size: Mapped[int] = mapped_column(Integer, default=10)
    
    # 数据规则
    unique_fields: Mapped[list] = mapped_column(JSONB, default=list)
    # ["user_id", "email"]
    
    default_values: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {"status": "active", "role": "user"}
    
    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DataMaskingRule(Base):
    """数据脱敏规则"""
    __tablename__ = "data_masking_rules"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 规则名称
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 字段匹配
    field_pattern: Mapped[str] = mapped_column(String(200), nullable=False)  # 正则表达式
    # "phone", "id_card", "email", "*password*"
    
    # 脱敏算法
    masking_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # phone: 手机号脱敏（138****8000）
    # email: 邮箱脱敏（t***@example.com）
    # id_card: 身份证脱敏
    # hash: 哈希脱敏
    # random: 随机替换
    # custom: 自定义规则
    
    masking_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "keep_prefix": 3,
    #   "keep_suffix": 4,
    #   "mask_char": "*"
    # }
    
    # 是否启用
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())