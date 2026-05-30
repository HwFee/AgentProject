from models.report import ReportTask
from pipeline.types import PipelinePlan, PipelineStep


class PipelinePlanner:
    def plan(self, task: ReportTask) -> PipelinePlan:
        has_attachments = bool(getattr(task, "attachments", None))

        steps = [
            PipelineStep(
                id="requirement_intake",
                name="需求理解",
                skill_id="requirement.intake",
                input_keys=["requirement"],
                output_key="normalized_requirement",
            ),
            PipelineStep(
                id="outline_plan",
                name="生成大纲",
                skill_id="planning.outline",
                input_keys=["normalized_requirement"],
                output_key="report_outline",
                depends_on=["requirement_intake"],
            ),
            PipelineStep(
                id="research_collect",
                name="资料收集",
                skill_id="research.collect",
                input_keys=["normalized_requirement", "attachments"],
                output_key="research_notes",
                depends_on=["requirement_intake"],
            ),
        ]

        if has_attachments:
            steps.append(
                PipelineStep(
                    id="data_analyze",
                    name="数据分析",
                    skill_id="data.analyze",
                    input_keys=["attachments", "research_notes"],
                    output_key="data_insights",
                    depends_on=["research_collect"],
                )
            )

        data_deps = ["outline_plan", "research_collect"]
        data_input_keys = ["report_outline", "research_notes"]
        if has_attachments:
            data_deps.append("data_analyze")
            data_input_keys.append("data_insights")

        steps.extend([
            PipelineStep(
                id="draft_report",
                name="撰写初稿",
                skill_id="writing.draft_report",
                input_keys=data_input_keys,
                output_key="draft_report",
                depends_on=data_deps,
            ),
            PipelineStep(
                id="de_ai_polish",
                name="去 AI 化润色",
                skill_id="writing.de_ai_polish",
                input_keys=["draft_report"],
                output_key="polished_report",
                depends_on=["draft_report"],
            ),
            PipelineStep(
                id="quality_check",
                name="质量检查",
                skill_id="review.quality_check",
                input_keys=["polished_report", "normalized_requirement"],
                output_key="quality_report",
                depends_on=["de_ai_polish", "requirement_intake"],
            ),
            PipelineStep(
                id="export_files",
                name="导出文件",
                skill_id="export.report_files",
                input_keys=["polished_report"],
                output_key="exported_files",
                depends_on=["de_ai_polish"],
            ),
        ])

        return PipelinePlan(
            id=f"pipeline_{task.id}",
            task_id=task.id,
            steps=steps,
        )
