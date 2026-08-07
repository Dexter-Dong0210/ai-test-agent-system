"""
缺陷管理模型

支持缺陷跟踪、外部系统集成（Jira/禅道）、AI根因分析
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
    from app.models.test_result import TestResult


class DefectSeverity(str, enum.Enum):
    """缺陷严重程度"""
    BLOCKER = "blocker"      # 阻塞（系统崩溃、数据丢失）
    CRITICAL = "critical"    # 严重（功能无法使用）
    MAJOR = "major"          # 主要（功能受损）
    NORMAL = "normal"        # 一般（功能可用但不完整）
    MINOR = "minor"          # 次要（界面问题、优化建议）
    TRIVIAL = "trivial"      # 轻微（文案错误）


class DefectPriority(str, enum.Enum):
    """缺陷优先级"""
    URGENT = "urgent"        # 紧急（立即处理）
    HIGH = "high"            # 高（24小时内）
    MEDIUM = "medium"        # 中（本周内）
    LOW = "low"              # 低（有空处理）


class DefectStatus(str, enum.Enum):
    """缺陷状态"""
    NEW = "new"                          # 新建
    CONFIRMED = "confirmed"              # 已确认
    ASSIGNED = "assigned"                # 已分配
    IN_PROGRESS = "in_progress"          # 处理中
    RESOLVED = "resolved"                # 已解决
    VERIFIED = "verified"                # 已验证
    CLOSED = "closed"                    # 已关闭
    REOPENED = "reopened"                # 已重开


class ExternalSystem(str, enum.Enum):
    """外部缺陷管理系统"""
    JIRA = "jira"
    ZENTAO = "zentao"        # 禅道
    TAPD = "tapd"
    GITLAB = "gitlab"
    GITHUB = "github"


class Defect(Base):
    """缺陷"""
    __tablename__ = "defects"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    test_result_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("test_results.id", ondelete="SET NULL")
    )
    
    # 基本信息
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 分类
    severity: Mapped[DefectSeverity] = mapped_column(
        SQLEnum(DefectSeverity),
        default=DefectSeverity.NORMAL,
        nullable=False
    )
    priority: Mapped[DefectPriority] = mapped_column(
        SQLEnum(DefectPriority),
        default=DefectPriority.MEDIUM,
        nullable=False
    )
    status: Mapped[DefectStatus] = mapped_column(
        SQLEnum(DefectStatus),
        default=DefectStatus.NEW,
        nullable=False,
        index=True
    )
    
    # 影响范围
    module: Mapped[Optional[str]] = mapped_column(String(100))
    environment: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 重现信息
    steps_to_reproduce: Mapped[Optional[str]] = mapped_column(Text)
    expected_result: Mapped[Optional[str]] = mapped_column(Text)
    actual_result: Mapped[Optional[str]] = mapped_column(Text)
    
    # 人员信息
    reporter: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    assignee: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    
    # 外部系统集成
    external_system: Mapped[Optional[ExternalSystem]] = mapped_column(SQLEnum(ExternalSystem))
    external_key: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    external_url: Mapped[Optional[str]] = mapped_column(String(500))
    external_status: Mapped[Optional[str]] = mapped_column(String(50))
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # AI分析
    ai_root_cause: Mapped[Optional[str]] = mapped_column(Text)
    ai_suggested_fix: Mapped[Optional[str]] = mapped_column(Text)
    ai_similar_defects: Mapped[list] = mapped_column(JSONB, default=list)
    ai_confidence: Mapped[Optional[float]] = mapped_column()
    
    # 附件
    attachments: Mapped[list] = mapped_column(JSONB, default=list)
    
    # 标签
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    
    # 统计
    reopen_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 时间戳
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="defects")
    test_result: Mapped[Optional["TestResult"]] = relationship("TestResult", back_populates="defects")


class DefectComment(Base):
    """缺陷评论"""
    __tablename__ = "defect_comments"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    defect_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("defects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 评论类型
    comment_type: Mapped[str] = mapped_column(String(20), default="comment")  # comment/status_change
    
    # 状态变更（如果是状态变更评论）
    old_status: Mapped[Optional[str]] = mapped_column(String(20))
    new_status: Mapped[Optional[str]] = mapped_column(String(20))
    
    author_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DefectHistory(Base):
    """缺陷历史记录"""
    __tablename__ = "defect_history"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    defect_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("defects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 变更字段
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text)
    new_value: Mapped[Optional[str]] = mapped_column(Text)
    
    changed_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExternalSystemConfig(Base):
    """外部系统配置"""
    __tablename__ = "external_system_configs"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    system_type: Mapped[ExternalSystem] = mapped_column(SQLEnum(ExternalSystem), nullable=False)
    
    # 连接配置（加密存储）
    api_url: Mapped[str] = mapped_column(String(500), nullable=False)
    api_key: Mapped[Optional[str]] = mapped_column(String(500))  # 加密
    username: Mapped[Optional[str]] = mapped_column(String(100))
    password: Mapped[Optional[str]] = mapped_column(String(500))  # 加密
    
    # 项目映射
    project_key: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 字段映射
    field_mapping: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # 同步配置
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_interval: Mapped[int] = mapped_column(Integer, default=300)  # 秒
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())