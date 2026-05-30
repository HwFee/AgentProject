import os
from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.export import ExportService


class ExportReportSkill:
    skill_id = "export.report_files"
    name = "导出文件"
    description = "将报告导出为 DOCX 和 PDF 格式"

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        report = context.artifacts.get("polished_report", "")
        task_id = context.task_id

        exported = {}

        pdf_started = datetime.utcnow()
        pdf_filename = f"report_{task_id}_{int(datetime.now().timestamp())}.pdf"
        pdf_full_path = "/".join(["images", "reports", pdf_filename])
        os.makedirs(os.path.dirname(pdf_full_path), exist_ok=True)
        pdf_result = ExportService.export_pdf(report, pdf_full_path)
        if pdf_result:
            exported["pdf_path"] = "/".join(["reports", pdf_filename])
            context.tool_events.append({
                "event_type": "export_pdf",
                "title": "导出 报告.pdf",
                "description": f"生成 PDF 文件: {pdf_filename}",
                "status": "completed",
                "input_data": {"report_length": len(report)},
                "output_data": {"filename": pdf_filename, "path": exported["pdf_path"]},
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
        docx_result = ExportService.export_docx(report, docx_full_path)
        if docx_result:
            exported["docx_path"] = "/".join(["reports", docx_filename])
            context.tool_events.append({
                "event_type": "export_docx",
                "title": "导出 报告.docx",
                "description": f"生成 DOCX 文件: {docx_filename}",
                "status": "completed",
                "input_data": {"report_length": len(report)},
                "output_data": {"filename": docx_filename, "path": exported["docx_path"]},
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
            output=exported,
            artifacts=exported,
        )
