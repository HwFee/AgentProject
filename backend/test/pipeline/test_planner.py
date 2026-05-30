from unittest.mock import MagicMock

import pytest

from pipeline.planner import PipelinePlanner
from pipeline.types import PipelinePlan


class TestPipelinePlanner:
    def _make_task(self, has_attachments=False):
        task = MagicMock()
        task.id = 42
        task.requirement = "分析 AI 行业趋势"
        task.title = "AI 行业报告"
        if has_attachments:
            att = MagicMock()
            att.filename = "data.csv"
            task.attachments = [att]
        else:
            task.attachments = []
        return task

    def test_plan_returns_pipeline_plan(self):
        planner = PipelinePlanner()
        task = self._make_task()
        plan = planner.plan(task)
        assert isinstance(plan, PipelinePlan)
        assert plan.task_id == 42
        assert plan.id == "pipeline_42"

    def test_plan_has_correct_step_order_without_attachments(self):
        planner = PipelinePlanner()
        task = self._make_task(has_attachments=False)
        plan = planner.plan(task)
        step_ids = [s.id for s in plan.steps]
        assert step_ids == [
            "requirement_intake",
            "outline_plan",
            "research_collect",
            "draft_report",
            "de_ai_polish",
            "quality_check",
            "export_files",
        ]

    def test_plan_includes_data_analyze_with_attachments(self):
        planner = PipelinePlanner()
        task = self._make_task(has_attachments=True)
        plan = planner.plan(task)
        step_ids = [s.id for s in plan.steps]
        assert "data_analyze" in step_ids
        data_idx = step_ids.index("data_analyze")
        draft_idx = step_ids.index("draft_report")
        assert data_idx < draft_idx

    def test_each_step_has_required_fields(self):
        planner = PipelinePlanner()
        task = self._make_task()
        plan = planner.plan(task)
        for step in plan.steps:
            assert step.id
            assert step.name
            assert step.skill_id
            assert isinstance(step.input_keys, list)
            assert step.output_key

    def test_step_dependencies_are_valid(self):
        planner = PipelinePlanner()
        task = self._make_task(has_attachments=True)
        plan = planner.plan(task)
        step_ids = {s.id for s in plan.steps}
        for step in plan.steps:
            for dep in step.depends_on:
                assert dep in step_ids, f"Step {step.id} depends on unknown step {dep}"

    def test_no_circular_dependencies(self):
        planner = PipelinePlanner()
        task = self._make_task(has_attachments=True)
        plan = planner.plan(task)
        step_map = {s.id: s for s in plan.steps}
        visited = set()
        in_stack = set()

        def dfs(step_id):
            if step_id in in_stack:
                return False
            if step_id in visited:
                return True
            in_stack.add(step_id)
            for dep in step_map[step_id].depends_on:
                if not dfs(dep):
                    return False
            in_stack.discard(step_id)
            visited.add(step_id)
            return True

        for step in plan.steps:
            assert dfs(step.id), f"Circular dependency detected involving {step.id}"
