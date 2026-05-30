from skills.adapters.quality_review import QualityReviewSkill
from skills.adapters.de_ai_polish import DeAiPolishSkill
from skills.adapters.export_report import ExportReportSkill
from pipeline.types import PipelineContext, PipelineStep


class TestQualityReviewSkill:
    def test_parse_pass(self):
        skill = QualityReviewSkill()
        assert skill._parse_quality_result("### 结论\nPASS") is True

    def test_parse_needs_revision(self):
        skill = QualityReviewSkill()
        assert skill._parse_quality_result("### 结论\nNEEDS_REVISION\n需要改进...") is False

    def test_parse_default_pass(self):
        skill = QualityReviewSkill()
        assert skill._parse_quality_result("没有明确结论") is True

    def test_parse_case_insensitive(self):
        skill = QualityReviewSkill()
        assert skill._parse_quality_result("needs_revision") is False
        assert skill._parse_quality_result("pass") is True


class TestDeAiPolishSkill:
    def test_empty_text_skips_llm(self):
        skill = DeAiPolishSkill()
        context = PipelineContext(task_id=1, requirement="test", artifacts={"draft_report": ""})
        step = PipelineStep("test", "Test", "writing.de_ai_polish", ["draft_report"], "polished_report")
        result = skill.execute(context, step)
        assert result.output == ""
        assert result.token_usage == {}

    def test_short_text_skips_llm(self):
        skill = DeAiPolishSkill()
        context = PipelineContext(task_id=1, requirement="test", artifacts={"draft_report": "短文本"})
        step = PipelineStep("test", "Test", "writing.de_ai_polish", ["draft_report"], "polished_report")
        result = skill.execute(context, step)
        assert result.output == "短文本"
        assert result.token_usage == {}


class TestExportReportSkill:
    def test_export_empty_report(self):
        skill = ExportReportSkill()
        context = PipelineContext(task_id=99999, requirement="test", artifacts={"polished_report": ""})
        step = PipelineStep("test", "Test", "export.report_files", ["polished_report"], "exported_files")
        result = skill.execute(context, step)
        assert isinstance(result.output, dict)
        assert isinstance(result.artifacts, dict)
