import os
from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.export import ExportService
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter
from skills.package import SkillPackage


# Maps external skill names to internal pipeline skill_ids
SKILL_ID_MAP = {
    "outline-planning": "planning.outline",
    "data-analyst": "data.analyze",
    "humanizer": "writing.de_ai_polish",
    "ai-writing-detox": "writing.de_ai_polish",
    "factcheck": "review.quality_check",
    "content-research-writer": "writing.draft_report",
    "academic-deep-research": "research.collect",
    "csv-data-summarizer": "data.analyze",
    "chief-editor": "writing.de_ai_polish",
    "humanize-chinese": "writing.de_ai_polish",
    "ub2-markdown-report-generator": "export.report_files",
}


class PromptSkillAdapter:
    def __init__(self, package: SkillPackage):
        self.package = package
        raw_id = package.name.replace("-", ".")
        self.skill_id = SKILL_ID_MAP.get(package.name, raw_id)
        self.name = package.name
        self.description = package.description
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        started = datetime.utcnow()

        # Build user prompt from step input_keys
        sections = []
        for key in step.input_keys:
            if key == "requirement":
                val = context.requirement
            else:
                val = context.artifacts.get(key)
            if val is not None:
                display_key = key.replace("_", " ").title()
                if isinstance(val, list):
                    if val:
                        sections.append(f"## {display_key}\n{self._summarize_list(val)}")
                elif isinstance(val, str) and val.strip():
                    sections.append(f"## {display_key}\n{val}")
                elif val:
                    sections.append(f"## {display_key}\n{str(val)[:2000]}")

        user_content = "\n\n".join(sections) if sections else context.requirement

        system_content = (
            self.package.full_content
            + "\n\n---\n\n【自动执行模式】\n"
            "你是自动化报告生成流水线中的一个环节。\n"
            "- 用户已确认所有需求，请直接执行，不要提出澄清问题。\n"
            "- 不要输出'好的'、'以下是'、'按照您的要求'等客套话，直接给出实质内容。\n"
            "- 如果某个步骤需要用户确认才能继续，请直接基于已有信息做出最佳判断并继续执行。\n"
            "- 输出必须是可直接使用的最终成果，不需要额外的格式说明或执行建议。\n"
            "- 严禁使用'保留表格'、'保留图表'、'待补充'、'TODO'、'待填写'等占位符或提示文字。\n"
            "- 如果缺少具体数据，请基于已有信息和你的知识进行合理推断并填充内容，绝不允许留空或使用占位符。\n"
            "- 表格必须包含具体数据和内容，不能只是表头或空表格。"
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

        model = ModelRouter.select("write")
        response = self.client.chat_sync(messages=messages, model=model)
        content = response.get("content", "")

        context.tool_events.append({
            "event_type": "skill_execution",
            "title": f"执行 {self.name}",
            "description": f"外置 skill {self.name} 执行完成，输出 {len(content)} 字符",
            "status": "completed",
            "input_data": {"skill": self.name, "keys": step.input_keys},
            "output_data": {"length": len(content), "preview": content[:200]},
            "started_at": started,
            "completed_at": datetime.utcnow(),
        })

        # For export step, also generate PDF and DOCX
        artifacts = {}
        if self.skill_id == "export.report_files":
            task_id = context.task_id
            report = content

            pdf_started = datetime.utcnow()
            pdf_filename = f"report_{task_id}_{int(datetime.now().timestamp())}.pdf"
            pdf_full_path = "/".join(["images", "reports", pdf_filename])
            os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
            if ExportService.export_pdf(report, pdf_full_path):
                artifacts["pdf_path"] = "/".join(["reports", pdf_filename])
                context.tool_events.append({
                    "event_type": "export_pdf",
                    "title": "导出 报告.pdf",
                    "description": f"生成 PDF 文件: {pdf_filename}",
                    "status": "completed",
                    "input_data": {"report_length": len(report)},
                    "output_data": {"filename": pdf_filename, "path": artifacts["pdf_path"]},
                    "started_at": pdf_started,
                    "completed_at": datetime.utcnow(),
                })
            else:
                context.tool_events.append({
                    "event_type": "export_pdf",
                    "title": "导出 报告.pdf",
                    "description": "PDF 导出失败",
                    "status": "failed",
                    "input_data": {},
                    "output_data": {},
                    "started_at": pdf_started,
                    "completed_at": datetime.utcnow(),
                })

            docx_started = datetime.utcnow()
            docx_filename = f"report_{task_id}_{int(datetime.now().timestamp())}.docx"
            docx_full_path = "/".join(["images", "reports", docx_filename])
            os.makedirs(os.path.dirname(docx_full_path), exist_ok=True)
            if ExportService.export_docx(report, docx_full_path):
                artifacts["docx_path"] = "/".join(["reports", docx_filename])
                context.tool_events.append({
                    "event_type": "export_docx",
                    "title": "导出 报告.docx",
                    "description": f"生成 DOCX 文件: {docx_filename}",
                    "status": "completed",
                    "input_data": {"report_length": len(report)},
                    "output_data": {"filename": docx_filename, "path": artifacts["docx_path"]},
                    "started_at": docx_started,
                    "completed_at": datetime.utcnow(),
                })
            else:
                context.tool_events.append({
                    "event_type": "export_docx",
                    "title": "导出 报告.docx",
                    "description": "DOCX 导出失败",
                    "status": "failed",
                    "input_data": {},
                    "output_data": {},
                    "started_at": docx_started,
                    "completed_at": datetime.utcnow(),
                })

        return SkillResult(
            output=artifacts if artifacts else content,
            token_usage=response.get("usage", {}),
            artifacts=artifacts,
        )

    def _summarize_list(self, items: list) -> str:
        parts = []
        for i, item in enumerate(items[:10], 1):
            if isinstance(item, dict):
                title = item.get("filename", item.get("title", f"Item {i}"))
                content = item.get("content", item.get("parsed_content", ""))
                parts.append(f"### {title}\n{str(content)[:500]}")
            else:
                parts.append(f"- {str(item)[:200]}")
        if len(items) > 10:
            parts.append(f"\n... and {len(items) - 10} more items")
        return "\n\n".join(parts)
