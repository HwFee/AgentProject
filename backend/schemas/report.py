from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OutputFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"


class ReportGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    requirement: str = Field(..., min_length=1)
    attachments: List[str] = Field(default=[])
    output_formats: List[OutputFormat] = Field(default=[OutputFormat.MARKDOWN])
    mode: str = Field(default="generate")


class ReportTaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    requirement: str
    status: str
    mode: Optional[str] = None
    final_report_md: Optional[str] = None
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None
    error_msg: Optional[str] = None
    dag_plan: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _ensure_utc_timezone(self) -> "ReportTaskResponse":
        for field in ("created_at", "updated_at"):
            val = getattr(self, field)
            if val and val.tzinfo is None:
                setattr(self, field, val.replace(tzinfo=timezone.utc))
        return self


class AttachmentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str  # "pending" | "parsing" | "parsed" | "failed"
    parsed_length: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class NodeResponse(BaseModel):
    node_id: str
    agent_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    output_summary: Optional[str] = None
    retry_count: int = 0
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _ensure_utc_timezone(self) -> "NodeResponse":
        for field in ("started_at", "completed_at"):
            val = getattr(self, field)
            if val and val.tzinfo is None:
                setattr(self, field, val.replace(tzinfo=timezone.utc))
        return self


class AgentNodeResponse(BaseModel):
    node_id: str
    agent_type: str
    model_used: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    retry_count: int
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _ensure_utc_timezone(self) -> "AgentNodeResponse":
        for field in ("started_at", "completed_at"):
            val = getattr(self, field)
            if val and val.tzinfo is None:
                setattr(self, field, val.replace(tzinfo=timezone.utc))
        return self


class ReportStatusResponse(BaseModel):
    id: int
    status: str
    mode: str
    progress: Optional[Dict[str, Any]] = None
    nodes: List[NodeResponse] = []
    attachments: List[AttachmentResponse] = []
    model_config = ConfigDict(from_attributes=True)


class ReportResultResponse(BaseModel):
    task_id: int
    status: str
    title: str
    markdown_content: Optional[str]
    pdf_url: Optional[str]
    docx_url: Optional[str]
    completed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _ensure_utc_timezone(self) -> "ReportResultResponse":
        if self.completed_at and self.completed_at.tzinfo is None:
            self.completed_at = self.completed_at.replace(tzinfo=timezone.utc)
        return self


class ReportGenerateResponse(BaseModel):
    task_id: int
    status: str
    message: str = "报告生成任务已提交"
    model_config = ConfigDict(from_attributes=True)


# Forward reference resolution
ReportStatusResponse.model_rebuild()
