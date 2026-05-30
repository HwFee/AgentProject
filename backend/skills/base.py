from typing import Protocol, runtime_checkable

from pipeline.types import PipelineContext, PipelineStep, SkillResult, SkillMetadata


@runtime_checkable
class SkillAdapter(Protocol):
    skill_id: str
    name: str
    description: str

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        ...
