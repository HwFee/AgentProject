import asyncio
import json
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from crud.artifact import ArtifactCRUD
from crud.report import ReportCRUD
from pipeline.executor import PipelineExecutor, ARTIFACT_CONFIG
from pipeline.planner import PipelinePlanner
from pipeline.skill_pool import SkillPool
from pipeline.types import PipelineContext, PipelinePlan, PipelineStep

logger = logging.getLogger(__name__)

STEP_DEPENDENCY_MAP = {
    "requirement_intake": [],
    "outline_plan": ["requirement_intake"],
    "research_collect": ["requirement_intake"],
    "data_analyze": ["research_collect"],
    "draft_report": ["outline_plan", "research_collect", "data_analyze"],
    "de_ai_polish": ["draft_report"],
    "quality_check": ["de_ai_polish", "requirement_intake"],
    "export_files": ["de_ai_polish"],
}

STEP_DOWNSTREAM_MAP = {
    "requirement_intake": ["outline_plan", "research_collect", "data_analyze", "draft_report", "de_ai_polish", "quality_check", "export_files"],
    "outline_plan": ["draft_report", "de_ai_polish", "quality_check", "export_files"],
    "research_collect": ["data_analyze", "draft_report", "de_ai_polish", "quality_check", "export_files"],
    "data_analyze": ["draft_report", "de_ai_polish", "quality_check", "export_files"],
    "draft_report": ["de_ai_polish", "quality_check", "export_files"],
    "de_ai_polish": ["quality_check", "export_files"],
    "quality_check": [],
    "export_files": [],
}

SKILL_ID_TO_STEP = {
    "requirement.intake": "requirement_intake",
    "planning.outline": "outline_plan",
    "research.collect": "research_collect",
    "data.analyze": "data_analyze",
    "writing.draft_report": "draft_report",
    "writing.de_ai_polish": "de_ai_polish",
    "review.quality_check": "quality_check",
    "export.report_files": "export_files",
}


class ChatOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_message(
        self,
        task_id: int,
        message: str,
        target_step_id: Optional[str] = None,
        target_artifact_id: Optional[int] = None,
        user_id: int = 0,
    ) -> dict:
        task = await ReportCRUD.get_task(db=self.db, task_id=task_id)
        if not task:
            return {"error": "Task not found", "action": "none"}

        mentioned_step_id = self._infer_mentioned_step(message)
        step_id = target_step_id or mentioned_step_id
        if step_id:
            return await self.rerun_from_step(
                task_id=task_id,
                step_id=step_id,
                user_id=user_id,
                change_reason=message,
            )

        if target_artifact_id:
            return await self._edit_artifact(
                task_id=task_id,
                artifact_id=target_artifact_id,
                message=message,
                user_id=user_id,
            )

        step_id = self._infer_target_step(message)
        if step_id:
            return await self.rerun_from_step(
                task_id=task_id,
                step_id=step_id,
                user_id=user_id,
                change_reason=message,
            )

        return await self._edit_final_report(
            task_id=task_id,
            message=message,
            user_id=user_id,
        )

    async def rerun_from_step(
        self,
        task_id: int,
        step_id: str,
        user_id: int = 0,
        change_reason: str = "User requested rerun",
    ) -> dict:
        task = await ReportCRUD.get_task(db=self.db, task_id=task_id)
        if not task:
            return {"error": "Task not found", "action": "none"}

        planner = PipelinePlanner()
        plan = planner.plan(task)

        step_map = {s.id: s for s in plan.steps}
        if step_id not in step_map:
            return {"error": f"Step {step_id} not found", "action": "none"}

        affected_steps = [step_id] + STEP_DOWNSTREAM_MAP.get(step_id, [])
        affected_steps = [s for s in affected_steps if s in step_map]

        context = await self._rebuild_context(task, plan)

        from workers.report_worker import _build_skill_pool
        skill_pool = _build_skill_pool()

        partial_plan = PipelinePlan(
            id=f"rerun_{plan.id}_{step_id}",
            task_id=task_id,
            steps=[step_map[s] for s in affected_steps],
        )

        executor = PipelineExecutor(partial_plan, skill_pool, self.db)
        executor._step_results = {
            sid: {"output": context.artifacts.get(step_map[sid].output_key, "")}
            for sid in step_map
            if sid not in affected_steps
        }

        await ReportCRUD.update_task_status(self.db, task_id, "running")

        try:
            context = await executor.execute(context)

            final_report = context.artifacts.get("polished_report") or context.artifacts.get("draft_report", "")
            exported = context.artifacts.get("exported_files", {})
            pdf_path = exported.get("pdf_path")
            docx_path = exported.get("docx_path")

            if not pdf_path or not docx_path:
                from services.export import ExportService
                import os
                from datetime import datetime
                if not pdf_path:
                    pdf_filename = f"report_{task_id}_{int(datetime.now().timestamp())}.pdf"
                    pdf_full_path = "/".join(["images", "reports", pdf_filename])
                    os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
                    if ExportService.export_pdf(final_report, pdf_full_path):
                        pdf_path = "/".join(["reports", pdf_filename])
                if not docx_path:
                    docx_filename = f"report_{task_id}_{int(datetime.now().timestamp())}.docx"
                    docx_full_path = "/".join(["images", "reports", docx_filename])
                    os.makedirs(os.path.dirname(docx_full_path), exist_ok=True)
                    if ExportService.export_docx(final_report, docx_full_path):
                        docx_path = "/".join(["reports", docx_filename])

            await ReportCRUD.update_task_result(
                self.db, task_id, final_report, pdf_path, docx_path
            )

            return {
                "action": "rerun",
                "step_id": step_id,
                "affected_steps": affected_steps,
                "change_reason": change_reason,
                "status": "completed",
            }
        except Exception as e:
            logger.exception(f"[ChatOrchestrator] Rerun failed: {e}")
            await ReportCRUD.update_task_status(
                self.db, task_id, "failed", error_msg=f"Rerun failed: {str(e)}"
            )
            return {
                "action": "rerun",
                "step_id": step_id,
                "affected_steps": affected_steps,
                "status": "failed",
                "error": str(e),
            }

    async def _edit_artifact(
        self,
        task_id: int,
        artifact_id: int,
        message: str,
        user_id: int = 0,
    ) -> dict:
        artifact = await ArtifactCRUD.get_artifact(self.db, artifact_id)
        if not artifact or artifact.report_id != task_id:
            return {"error": "Artifact not found", "action": "none"}

        current_content = ""
        if artifact.current_version:
            current_content = artifact.current_version.content or ""

        from services.llm_client import DeepSeekClient
        from services.model_router import ModelRouter

        client = DeepSeekClient()
        model = ModelRouter.select("write")

        messages = [
            {"role": "system", "content": "你是一个文档编辑助手。请根据用户的修改指令，修改以下文档内容。直接输出修改后的完整文档，不要解释修改过程。"},
            {"role": "user", "content": f"修改指令：{message}\n\n当前文档内容：\n{current_content}"},
        ]

        response = client.chat_sync(messages=messages, model=model)
        new_content = response.get("content", current_content)

        new_version = await ArtifactCRUD.create_version(
            db=self.db,
            artifact_id=artifact_id,
            content=new_content,
            source_type="chat_edit",
            change_reason=message,
            created_by=f"user_{user_id}",
        )

        if artifact.logical_name == "最终报告":
            task = await ReportCRUD.get_task(self.db, task_id)
            if task:
                task.final_report_md = new_content
                task.pdf_path = None
                task.docx_path = None
                await self.db.commit()

        return {
            "action": "edit_artifact",
            "artifact_id": artifact_id,
            "new_version": new_version.version,
            "status": "completed",
        }

    async def _edit_final_report(
        self,
        task_id: int,
        message: str,
        user_id: int = 0,
    ) -> dict:
        task = await ReportCRUD.get_task(self.db, task_id)
        if not task:
            return {"error": "Task not found", "action": "none"}

        current_content = task.final_report_md or ""

        from services.llm_client import DeepSeekClient
        from services.model_router import ModelRouter

        client = DeepSeekClient()
        model = ModelRouter.select("write")

        messages = [
            {"role": "system", "content": "你是一个文档编辑助手。请根据用户的修改指令，修改以下报告内容。直接输出修改后的完整报告，不要解释修改过程。保持 Markdown 格式。"},
            {"role": "user", "content": f"修改指令：{message}\n\n当前报告内容：\n{current_content}"},
        ]

        response = client.chat_sync(messages=messages, model=model)
        new_content = response.get("content", current_content)

        final_artifact = None
        artifacts = await ArtifactCRUD.get_report_artifacts(self.db, task_id)
        for art in artifacts:
            if art.logical_name == "最终报告":
                final_artifact = art
                break

        if final_artifact:
            await ArtifactCRUD.create_version(
                db=self.db,
                artifact_id=final_artifact.id,
                content=new_content,
                source_type="chat_edit",
                change_reason=message,
                created_by=f"user_{user_id}",
            )
        else:
            await ArtifactCRUD.create_artifact(
                db=self.db,
                report_id=task_id,
                step_id="export_files",
                skill_id="export.report_files",
                logical_name="最终报告",
                filename="最终报告.md",
                artifact_type="markdown",
                content=new_content,
                source_type="chat_edit",
                change_reason=message,
                created_by=f"user_{user_id}",
            )

        task.final_report_md = new_content
        task.pdf_path = None
        task.docx_path = None
        await self.db.commit()

        return {
            "action": "edit_final_report",
            "message": message,
            "status": "completed",
        }

    async def _rebuild_context(self, task, plan: PipelinePlan) -> PipelineContext:
        artifacts_dict = {}
        artifacts_dict["requirement"] = task.requirement
        artifacts_dict["title"] = task.title
        artifacts_dict["mode"] = task.mode

        attachments_data = []
        if hasattr(task, "attachments"):
            for att in task.attachments:
                attachments_data.append({
                    "filename": att.filename,
                    "content": att.parsed_content or "",
                    "file_path": att.file_path,
                })
        artifacts_dict["attachments"] = attachments_data

        db_artifacts = await ArtifactCRUD.get_report_artifacts(self.db, task.id)
        for art in db_artifacts:
            if art.current_version and art.current_version.content:
                step = next((s for s in plan.steps if s.id == art.step_id), None)
                if step:
                    artifacts_dict[step.output_key] = art.current_version.content

        return PipelineContext(
            task_id=task.id,
            requirement=task.requirement,
            artifacts=artifacts_dict,
        )

    def _infer_mentioned_step(self, message: str) -> Optional[str]:
        aliases = {
            "requirement_intake": ["需求理解", "需求解析", "需求"],
            "outline_plan": ["生成大纲", "报告大纲", "大纲"],
            "research_collect": ["资料收集", "调研", "搜索", "资料"],
            "data_analyze": ["数据分析", "数据", "图表"],
            "draft_report": ["撰写初稿", "初稿", "撰写"],
            "de_ai_polish": ["去 AI 化润色", "去AI化润色", "去AI", "润色"],
            "quality_check": ["质量检查", "质量", "评审", "检查"],
            "export_files": ["导出文件", "导出", "PDF", "DOCX"],
        }
        msg_lower = message.lower()
        for step_id, names in aliases.items():
            if f"@{step_id}".lower() in msg_lower:
                return step_id
            for name in names:
                if f"@{name}".lower() in msg_lower:
                    return step_id
        return None

    def _infer_target_step(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        keywords = {
            "research_collect": ["资料", "搜索", "调研", "收集", "补充", "research"],
            "outline_plan": ["大纲", "结构", "目录", "outline"],
            "draft_report": ["初稿", "撰写", "重写", "draft"],
            "de_ai_polish": ["润色", "去AI", "风格", "polish"],
            "quality_check": ["检查", "评审", "质量", "review", "quality"],
            "export_files": ["导出", "PDF", "DOCX", "export"],
            "data_analyze": ["数据", "分析", "图表", "data", "analyze"],
        }
        for step_id, kws in keywords.items():
            for kw in kws:
                if kw in message or kw.lower() in msg_lower:
                    return step_id
        return None
