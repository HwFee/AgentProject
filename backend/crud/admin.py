from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.report import ReportTask, AgentNode
from models.user import User


class AdminCRUD:
    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        total_users = await db.scalar(select(func.count(User.id)))
        total_reports = await db.scalar(select(func.count(ReportTask.id)))
        today_reports = await db.scalar(
            select(func.count(ReportTask.id)).where(ReportTask.created_at >= today)
        )
        running_tasks = await db.scalar(
            select(func.count(ReportTask.id)).where(ReportTask.status.in_(["running", "planning"]))
        )
        failed_tasks = await db.scalar(
            select(func.count(ReportTask.id)).where(ReportTask.status == "failed")
        )
        avg_duration = "8分32秒"  # Placeholder - calculate from node timings
        pending_failures = failed_tasks

        # Calculate total tokens from all nodes
        node_result = await db.execute(select(AgentNode.token_usage))
        all_tokens = node_result.scalars().all()
        total_tokens = sum(
            (t.get("total_tokens", 0) if isinstance(t, dict) else 0)
            for t in all_tokens
        )

        return {
            "total_users": total_users,
            "total_reports": total_reports,
            "today_reports": today_reports,
            "running_tasks": running_tasks,
            "failed_tasks": failed_tasks,
            "avg_duration": avg_duration,
            "pending_failures": pending_failures,
            "total_tokens": total_tokens,
            "trends": {k: 0 for k in ["total_users", "total_reports", "today_reports", "running_tasks", "failed_tasks"]},
        }

    @staticmethod
    async def get_token_trend(db: AsyncSession, days: int = 7) -> List[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(AgentNode).where(AgentNode.completed_at >= cutoff)
        )
        nodes = result.scalars().all()
        daily = {}
        for node in nodes:
            if node.completed_at and isinstance(node.token_usage, dict):
                day = node.completed_at.strftime("%m-%d")
                daily[day] = daily.get(day, 0) + node.token_usage.get("total_tokens", 0)
        return [{"date": d, "tokens": t} for d, t in sorted(daily.items())]

    @staticmethod
    async def get_failed_tasks(db: AsyncSession, limit: int = 5) -> List[ReportTask]:
        result = await db.execute(
            select(ReportTask)
            .where(ReportTask.status == "failed")
            .order_by(ReportTask.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_tasks(
        db: AsyncSession, skip: int = 0, limit: int = 10,
        status: str = None, mode: str = None, user_id: int = None,
        search: str = None, start_date: datetime = None, end_date: datetime = None
    ) -> List[dict]:
        query = select(ReportTask, User.username).join(User, ReportTask.user_id == User.id)
        if status:
            query = query.where(ReportTask.status == status)
        if mode:
            query = query.where(ReportTask.mode == mode)
        if user_id:
            query = query.where(ReportTask.user_id == user_id)
        if search:
            query = query.where(ReportTask.title.ilike(f"%{search}%"))
        if start_date:
            query = query.where(ReportTask.created_at >= start_date)
        if end_date:
            query = query.where(ReportTask.created_at <= end_date)
        query = query.order_by(ReportTask.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        rows = result.all()
        return [{"task": r[0], "username": r[1]} for r in rows]

    @staticmethod
    async def count_all_tasks(
        db: AsyncSession, status: str = None, mode: str = None, user_id: int = None,
        search: str = None, start_date: datetime = None, end_date: datetime = None
    ) -> int:
        query = select(func.count(ReportTask.id)).join(User, ReportTask.user_id == User.id)
        if status:
            query = query.where(ReportTask.status == status)
        if mode:
            query = query.where(ReportTask.mode == mode)
        if user_id:
            query = query.where(ReportTask.user_id == user_id)
        if search:
            query = query.where(ReportTask.title.ilike(f"%{search}%"))
        if start_date:
            query = query.where(ReportTask.created_at >= start_date)
        if end_date:
            query = query.where(ReportTask.created_at <= end_date)
        return await db.scalar(query) or 0

    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        result = await db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def count_users(db: AsyncSession) -> int:
        return await db.scalar(select(func.count(User.id))) or 0
