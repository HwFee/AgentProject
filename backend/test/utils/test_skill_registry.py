import pytest
from pathlib import Path
from services.skill_registry import SkillRegistry

SKILLS_DIR = str(Path(__file__).parent.parent.parent.parent / "skills")


def test_skill_registry_discovers_skills():
    registry = SkillRegistry(SKILLS_DIR)
    assert "docx" in registry.skills
    assert len(registry.metadata) > 0


def test_skill_metadata():
    registry = SkillRegistry(SKILLS_DIR)
    section = registry.get_system_prompt_section()
    assert "docx" in section or len(registry.metadata) == 0


def test_match_skills():
    registry = SkillRegistry(SKILLS_DIR)
    matched = registry.match_skills("帮我创建一个 Word 文档")
    names = [s.name for s in matched]
    assert "docx" in names
