from abc import ABC, abstractmethod
from typing import Any, Dict, List
from services.llm_client import DeepSeekClient
from services.skill_registry import skill_registry
from services.skill_registry import Skill


class BaseAgent(ABC):
    """Agent 抽象基类"""

    agent_type: str = "base"
    SYSTEM_PROMPT: str = "You are a helpful assistant."

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.client = DeepSeekClient()
        self.activated_skills: List[Skill] = []
        self.messages: List[Dict[str, str]] = []

    def prepare_prompt(self, task_context: str) -> str:
        system_prompt = self.SYSTEM_PROMPT
        skills_section = skill_registry.get_system_prompt_section()
        if skills_section:
            system_prompt += f"\n\n{skills_section}"
        self.activated_skills = skill_registry.match_skills(task_context)
        for skill in self.activated_skills:
            system_prompt += f"\n\n=== {skill.name.upper()} SKILL (activated) ===\n{skill.full_content}"
        return system_prompt

    def build_messages(self, task_context: str, user_input: str) -> List[Dict[str, str]]:
        system_prompt = self.prepare_prompt(task_context)
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def _format_context(self, input_data: Dict) -> str:
        parts = []
        if "requirement" in input_data:
            parts.append(f"需求：{input_data['requirement']}")
        if "title" in input_data:
            parts.append(f"标题：{input_data['title']}")
        if "context" in input_data:
            parts.append(f"上下文：\n{input_data['context']}")
        if "attachments" in input_data:
            parts.append(f"附件内容：\n{input_data['attachments']}")
        return "\n\n".join(parts)
