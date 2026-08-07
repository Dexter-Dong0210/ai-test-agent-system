"""
测试报告模型

存储测试报告的元数据和配置信息
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

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
import enum

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ReportType(str, enum.Enum):
    """报告类型"""
    SUMMARY = "summary"          # 汇总报告
    DETAIL = "detail"            # 详细报告
    DASHBOARD = "dashboard"      # 看板报告
    TREND = "trend"              # 趋势报告
    DEFECT = "defect"            # 缺陷报告


class ReportFormat(str, enum.Enum):
    """报告格式"""
    HTML = "html"
    PDF = "pdf"
    WORD = "word"
    MARKDOWN = "markdown"


class ReportStatus(str, enum.Enum):
    """报告状态"""
    GENERATING = "generating"    # 生成中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败


class TestReport(Base):
    """测试报告"""
    __tablename__ = "test_reports"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 基本信息
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 报告配置
    report_type: Mapped[ReportType] = mapped_column(
        SQLEnum(ReportType),
        default=ReportType.SUMMARY,
        nullable=False
    )
    report_format: Mapped[ReportFormat] = mapped_column(
        SQLEnum(ReportFormat),
        default=ReportFormat.HTML,
        nullable=False
    )
    
    # 数据范围
    test_run_ids: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    test_plan_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    
    # 时间范围
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # 生成配置
    include_details: Mapped[bool] = mapped_column(Boolean, default=True)
    include_screenshots: Mapped[bool] = mapped_column(Boolean, default=False)
    include_defects: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 文件信息
    file_path: Mapped[Optional[str]] = mapped_column(String(1000))
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64))
    
    # 状态
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus),
        default=ReportStatus.GENERATING,
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # 统计数据（预计算的指标）
    statistics: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # {
    #   "total_cases": 100,
    #   "passed": 85,
    #   "failed": 10,
    #   "blocked": 5,
    #   "pass_rate": 85.0,
    #   "avg_duration": 120.5,
    #   "total_defects": 8
    # }
    
    # 模板配置
    template_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    template_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    
    # 定时生成配置
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(100))
    
    # 访问控制
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    access_token: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    
    # 时间戳
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="reports")


class ReportTemplate(Base):
    """报告模板"""
    __tablename__ = "report_templates"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    
    # 模板信息
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 模板类型
    report_type: Mapped[ReportType] = mapped_column(SQLEnum(ReportType))
    
    # 模板配置
    sections: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    # ["summary", "trend", "defects", "details"]
    
    style_config: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # {
    #   "theme": "light",
    #   "primary_color": "#1890ff",
    #   "font_family": "Arial"
    # }
    
    # 是否为系统模板
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 使用统计
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))