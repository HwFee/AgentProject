import pytest

from pipeline.skill_pool import SkillPool
from pipeline.errors import SkillNotFoundError
from pipeline.types import PipelineContext, PipelineStep, SkillResult


class FakeSkill:
    def __init__(self, skill_id: str, name: str = "Fake", description: str = "Fake skill"):
        self.skill_id = skill_id
        self.name = name
        self.description = description

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        return SkillResult(output=f"output_from_{self.skill_id}")


class TestSkillPool:
    def test_register_and_get(self):
        pool = SkillPool()
        skill = FakeSkill("test.skill")
        pool.register(skill)
        assert pool.get("test.skill") is skill

    def test_get_not_found_raises(self):
        pool = SkillPool()
        with pytest.raises(SkillNotFoundError) as exc_info:
            pool.get("nonexistent.skill")
        assert exc_info.value.skill_id == "nonexistent.skill"

    def test_list_returns_metadata(self):
        pool = SkillPool()
        pool.register(FakeSkill("a.skill", "A", "Skill A"))
        pool.register(FakeSkill("b.skill", "B", "Skill B"))
        metadata = pool.list()
        assert len(metadata) == 2
        ids = {m.skill_id for m in metadata}
        assert ids == {"a.skill", "b.skill"}

    def test_register_overwrites_same_id(self):
        pool = SkillPool()
        skill1 = FakeSkill("test.skill", "First")
        skill2 = FakeSkill("test.skill", "Second")
        pool.register(skill1)
        pool.register(skill2)
        assert pool.get("test.skill").name == "Second"

    def test_list_empty_pool(self):
        pool = SkillPool()
        assert pool.list() == []
