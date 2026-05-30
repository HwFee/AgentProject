import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from models.base import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, enum.Enum):
    RESEARCH = "research"
    WRITE = "write"
    REVIEW = "review"
    DATA = "data"
    SIMPLE = "simple"


class NodeStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportTask(Base):
    __tablename__ = "report_tasks"

    user_id: Mapped[int] = mapped_column(nullable=False, comment="用户ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="报告标题")
    requirement: Mapped[str] = mapped_column(Text, nullable=False, comment="报告需求")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=TaskStatus.PENDING.value, comment="任务状态"
    )
    dag_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="DAG执行计划")
    model_routing: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="模型路由配置")
    final_report_md: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="最终报告Markdown内容")
    pdf_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="PDF文件路径")
    docx_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="DOCX文件路径")
    error_msg: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="错误信息")
    mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="generate", comment="报告生成模式: generate/template/reference/edit"
    )
    template_file_id: Mapped[Optional[int]] = mapped_column(
        nullable=True, comment="模板/编辑模式源文件ID"
    )

    # Relationships
    nodes: Mapped[list["AgentNode"]] = relationship(
        "AgentNode", back_populates="task", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["ReportAttachment"]] = relationship(
        "ReportAttachment", back_populates="task", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["ReportArtifact"]] = relationship(
        "ReportArtifact", back_populates="report", cascade="all, delete-orphan"
    )
    tool_events: Mapped[list["ReportToolEvent"]] = relationship(
        "ReportToolEvent", back_populates="report", cascade="all, delete-orphan"
    )


class AgentNode(Base):
    __tablename__ = "agent_nodes"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("report_tasks.id", ondelete="CASCADE", name="fk_report_attachments_task"), nullable=False, comment="任务ID"
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="节点ID")
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="Agent类型")
    model_used: Mapped[str] = mapped_column(String(100), nullable=False, comment="使用的模型")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=NodeStatus.PENDING.value, comment="节点状态"
    )
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="输入数据")
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="输出数据")
    token_usage: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="Token使用量")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="开始时间")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="完成时间")
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="重试次数")

    # Relationships
    task: Mapped["ReportTask"] = relationship("ReportTask", back_populates="nodes")


class ReportAttachment(Base):
    __tablename__ = "report_attachments"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("report_tasks.id", ondelete="CASCADE"), nullable=False, comment="任务ID"
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="文件路径")
    file_type: Mapped[str] = mapped_column(String(100), nullable=False, comment="文件类型")
    parsed_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="解析后的内容")

    # Relationships
    task: Mapped["ReportTask"] = relationship("ReportTask", back_populates="attachments")


class ReportArtifact(Base):
    __tablename__ = "report_artifacts"

    report_id: Mapped[int] = mapped_column(
        ForeignKey("report_tasks.id", ondelete="CASCADE"), nullable=False, comment="报告ID"
    )
    step_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="Pipeline步骤ID")
    skill_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="Skill ID")
    logical_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="逻辑名称(稳定标识)")
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="显示文件名")
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="产物类型: markdown/json/text/binary")
    current_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("artifact_versions.id", ondelete="SET NULL"), nullable=True, comment="当前版本ID"
    )

    # Relationships
    report: Mapped["ReportTask"] = relationship("ReportTask", back_populates="artifacts")
    versions: Mapped[list["ArtifactVersion"]] = relationship(
        "ArtifactVersion", back_populates="artifact", cascade="all, delete-orphan",
        foreign_keys="ArtifactVersion.artifact_id"
    )
    current_version: Mapped[Optional["ArtifactVersion"]] = relationship(
        "ArtifactVersion", foreign_keys=[current_version_id], post_update=True
    )


class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"

    artifact_id: Mapped[int] = mapped_column(
        ForeignKey("report_artifacts.id", ondelete="CASCADE"), nullable=False, comment="产物ID"
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, comment="版本号(从1递增)")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="产物内容")
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="内容哈希")
    change_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="变更原因")
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="创建者: system/user")
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="initial_generation",
        comment="来源类型: initial_generation/skill_rerun/user_edit/chat_edit/export"
    )
    source_step_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="来源步骤ID")
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="额外元数据")

    # Relationships
    artifact: Mapped["ReportArtifact"] = relationship(
        "ReportArtifact", back_populates="versions", foreign_keys=[artifact_id]
    )


class ReportToolEvent(Base):
    __tablename__ = "report_tool_events"

    report_id: Mapped[int] = mapped_column(
        ForeignKey("report_tasks.id", ondelete="CASCADE"), nullable=False, comment="报告ID"
    )
    step_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="Pipeline步骤ID")
    skill_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="Skill ID")
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="事件类型: search/read_url/read_file/create_file/edit_file/analyze_data/generate_chart/review/export_pdf/export_docx"
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="事件标题")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="一句话描述")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed", comment="状态")
    input_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="工具输入")
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="工具输出")
    artifact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("report_artifacts.id", ondelete="SET NULL"), nullable=True, comment="关联产物ID"
    )
    artifact_version_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("artifact_versions.id", ondelete="SET NULL"), nullable=True, comment="关联版本ID"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="开始时间")
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="完成时间")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序序号")

    # Relationships
    report: Mapped["ReportTask"] = relationship("ReportTask", back_populates="tool_events")
