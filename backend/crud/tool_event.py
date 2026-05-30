from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.report import ReportToolEvent


class ToolEventCRUD:
    @staticmethod
    async def get_events_by_report(
        db: AsyncSession, report_id: int
    ) -> List[ReportToolEvent]:
        result = await db.execute(
            select(ReportToolEvent)
            .where(ReportToolEvent.report_id == report_id)
            .order_by(ReportToolEvent.sort_order)
        )
        return result.scalars().all()

    @staticmethod
    async def get_events_by_step(
        db: AsyncSession, report_id: int, step_id: str
    ) -> List[ReportToolEvent]:
        result = await db.execute(
            select(ReportToolEvent)
            .where(ReportToolEvent.report_id == report_id)
            .where(ReportToolEvent.step_id == step_id)
            .order_by(ReportToolEvent.sort_order)
        )
        return result.scalars().all()
