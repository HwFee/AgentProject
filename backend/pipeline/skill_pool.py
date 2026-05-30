from pipeline.errors import SkillNotFoundError
from pipeline.types import SkillMetadata


class SkillPool:
    def __init__(self):
        self._skills: dict[str, object] = {}

    def register(self, adapter) -> None:
        self._skills[adapter.skill_id] = adapter

    def get(self, skill_id: str):
        skill = self._skills.get(skill_id)
        if skill is None:
            raise SkillNotFoundError(skill_id)
        return skill

    def list(self) -> list[SkillMetadata]:
        return [
            SkillMetadata(
                skill_id=s.skill_id,
                name=s.name,
                description=s.description,
            )
            for s in self._skills.values()
        ]
