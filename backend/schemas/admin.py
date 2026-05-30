from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_users: int
    total_reports: int
    today_reports: int
    running_tasks: int
    failed_tasks: int
    avg_duration: str
    pending_failures: int
    total_tokens: int
    trends: dict


class TokenTrendItem(BaseModel):
    date: str
    tokens: int


class TokenTrendResponse(BaseModel):
    data: List[TokenTrendItem]


class FailedTaskItem(BaseModel):
    id: int
    title: str
    failed_at: Optional[datetime]
    error_msg: Optional[str]


class AdminTaskItem(BaseModel):
    id: int
    title: str
    username: str
    status: str
    mode: str
    created_at: datetime
    updated_at: datetime
    error_msg: Optional[str] = None


class AdminUserItem(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
