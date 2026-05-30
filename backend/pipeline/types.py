from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineStep:
    id: str
    name: str
    skill_id: str
    input_keys: list[str]
    output_key: str
    depends_on: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelinePlan:
    id: str
    task_id: int
    steps: list[PipelineStep]


@dataclass
class PipelineContext:
    task_id: int
    requirement: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    tool_events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SkillResult:
    output: Any
    artifacts: dict[str, Any] = field(default_factory=dict)
    token_usage: dict[str, int] = field(default_factory=dict)


@dataclass
class SkillMetadata:
    skill_id: str
    name: str
    description: str
