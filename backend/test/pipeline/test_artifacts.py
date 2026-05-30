import hashlib

import pytest

from crud.artifact import ArtifactCRUD


class TestArtifactCRUDHash:
    def test_hash_content(self):
        content = "Hello World"
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert ArtifactCRUD._hash_content(content) == expected

    def test_hash_empty_content(self):
        assert ArtifactCRUD._hash_content("") == ""

    def test_hash_none_content(self):
        assert ArtifactCRUD._hash_content(None) == ""


class TestArtifactConfig:
    def test_artifact_config_has_all_steps(self):
        from pipeline.executor import ARTIFACT_CONFIG
        expected_steps = [
            "requirement_intake",
            "outline_plan",
            "research_collect",
            "data_analyze",
            "draft_report",
            "de_ai_polish",
            "quality_check",
            "export_files",
        ]
        for step in expected_steps:
            assert step in ARTIFACT_CONFIG, f"Missing artifact config for step: {step}"

    def test_artifact_config_has_required_fields(self):
        from pipeline.executor import ARTIFACT_CONFIG
        for step_id, config in ARTIFACT_CONFIG.items():
            assert "logical_name" in config, f"Missing logical_name for {step_id}"
            assert "filename" in config, f"Missing filename for {step_id}"
            assert "artifact_type" in config, f"Missing artifact_type for {step_id}"
            assert config["artifact_type"] in ("markdown", "json", "text", "binary")


class TestChatOrchestratorInfer:
    def test_infer_research_step(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("重新搜索资料") == "research_collect"
        assert orch._infer_target_step("补充一些数据") == "research_collect"

    def test_infer_outline_step(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("修改大纲结构") == "outline_plan"

    def test_infer_draft_step(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("重写初稿") == "draft_report"

    def test_infer_polish_step(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("润色一下") == "de_ai_polish"

    def test_infer_export_step(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("重新导出 PDF") == "export_files"

    def test_infer_unknown_returns_none(self):
        from services.chat_orchestrator import ChatOrchestrator
        orch = ChatOrchestrator(db=None)
        assert orch._infer_target_step("今天天气不错") is None


class TestStepDependencyMap:
    def test_downstream_map_covers_all_steps(self):
        from services.chat_orchestrator import STEP_DOWNSTREAM_MAP, STEP_DEPENDENCY_MAP
        all_steps = set(STEP_DEPENDENCY_MAP.keys())
        for step in all_steps:
            assert step in STEP_DOWNSTREAM_MAP

    def test_no_circular_downstream(self):
        from services.chat_orchestrator import STEP_DOWNSTREAM_MAP
        for step, downstream in STEP_DOWNSTREAM_MAP.items():
            assert step not in downstream, f"Step {step} is in its own downstream"

    def test_dependency_consistency(self):
        from services.chat_orchestrator import STEP_DOWNSTREAM_MAP, STEP_DEPENDENCY_MAP
        for step, deps in STEP_DEPENDENCY_MAP.items():
            for dep in deps:
                assert step in STEP_DOWNSTREAM_MAP.get(dep, []), \
                    f"{step} depends on {dep}, but {dep}'s downstream doesn't include {step}"
