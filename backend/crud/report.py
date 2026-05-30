from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.report import AgentNode, ReportAttachment, ReportTask
from schemas.report import ReportGenerateRequest


class ReportCRUD:
    """报告任务 CRUD 操作"""

    @staticmethod
    async def create_task(
        db: AsyncSession, user_id: int, title: str, requirement: str, mode: str = "generate"
    ) -> ReportTask:
        """创建报告任务"""
        task = ReportTask(
            user_id=user_id,
            title=title,
            requirement=requirement,
            status="pending",
            mode=mode,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[ReportTask]:
        """获取单个任务"""
        result = await db.execute(select(ReportTask).where(ReportTask.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_task_with_attachments(
        db: AsyncSession, task_id: int
    ) -> Optional[ReportTask]:
        """获取单个任务，包含节点和附件"""
        result = await db.execute(
            select(ReportTask)
            .where(ReportTask.id == task_id)
            .options(
                selectinload(ReportTask.nodes),
                selectinload(ReportTask.attachments),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_attachment(
        db: AsyncSession,
        task_id: int,
        filename: str,
        file_path: str,
        file_type: str,
    ) -> ReportAttachment:
        """创建附件记录"""
        attachment = ReportAttachment(
            task_id=task_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
        )
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment

    @staticmethod
    async def get_user_tasks(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20,
        search: str = None, status: str = None
    ) -> List[ReportTask]:
        """获取用户的任务列表"""
        query = select(ReportTask).where(ReportTask.user_id == user_id)
        if search:
            query = query.where(ReportTask.title.ilike(f"%{search}%"))
        if status:
            query = query.where(ReportTask.status == status)
        query = query.order_by(ReportTask.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count_user_tasks(
        db: AsyncSession, user_id: int, search: str = None, status: str = None
    ) -> int:
        """统计用户的任务数量"""
        query = select(func.count(ReportTask.id)).where(ReportTask.user_id == user_id)
        if search:
            query = query.where(ReportTask.title.ilike(f"%{search}%"))
        if status:
            query = query.where(ReportTask.status == status)
        result = await db.execute(query)
        return result.scalar()

    @staticmethod
    async def update_task_status(
        db: AsyncSession, task_id: int, status: str, error_msg: str = None
    ):
        """更新任务状态"""
        task = await ReportCRUD.get_task(db, task_id)
        if task:
            task.status = status
            if error_msg:
                task.error_msg = error_msg
            await db.commit()

    @staticmethod
    async def update_task_result(
        db: AsyncSession,
        task_id: int,
        markdown: str,
        pdf_path: str = None,
        docx_path: str = None,
    ):
        """更新任务结果"""
        task = await ReportCRUD.get_task(db, task_id)
        if task:
            task.final_report_md = markdown
            task.pdf_path = pdf_path
            task.docx_path = docx_path
            task.status = "completed"
            await db.commit()

    @staticmethod
    async def create_agent_node(
        db: AsyncSession, task_id: int, node_id: str, agent_type: str, model: str
    ) -> AgentNode:
        """创建 Agent 执行节点记录"""
        node = AgentNode(
            task_id=task_id,
            node_id=node_id,
            agent_type=agent_type,
            model_used=model,
            status="pending",
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def update_node_status(
        db: AsyncSession,
        node_id: int,
        status: str,
        output_data: dict = None,
        token_usage: dict = None,
    ):
        """更新节点执行状态"""
        from sqlalchemy import select

        result = await db.execute(select(AgentNode).where(AgentNode.id == node_id))
        node = result.scalar_one_or_none()
        if node:
            node.status = status
            if status == "running" and node.started_at is None:
                node.started_at = datetime.now(timezone.utc)
            if status in ("completed", "failed"):
                node.completed_at = datetime.now(timezone.utc)
            if output_data is not None:
                node.output_data = output_data
            if token_usage is not None:
                node.token_usage = token_usage
            await db.commit()

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        """删除任务（级联删除节点和附件）"""
        task = await ReportCRUD.get_task(db, task_id)
        if task:
            await db.delete(task)
            await db.commit()
            return True
        return False
