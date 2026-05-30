from typing import Any, Dict

from agents.base import BaseAgent
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class SimpleAgent(BaseAgent):
    """简单 Agent：负责摘要、格式化"""

    agent_type = "simple"

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.client = DeepSeekClient()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        context = self._format_context(input_data)
        messages = [
            {"role": "system", "content": "你是一个文本处理助手。请简洁地完成用户要求的任务。"},
            {"role": "user", "content": context},
        ]

        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model, max_tokens=2048)

        return {
            "content": response.get("content", ""),
            "usage": response.get("usage", {}),
            "agent_type": self.agent_type,
        }
