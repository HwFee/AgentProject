from typing import Dict, List


class TokenTracker:
    """追踪多 Agent 执行过程中的 Token 使用量"""

    def __init__(self):
        self._usages: List[Dict] = []

    def add(self, node_id: str, input_tokens: int, output_tokens: int):
        self._usages.append({
            "node_id": node_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        })

    @property
    def total_input(self) -> int:
        return sum(u["input_tokens"] for u in self._usages)

    @property
    def total_output(self) -> int:
        return sum(u["output_tokens"] for u in self._usages)

    def get_summary(self) -> Dict:
        return {
            "total_input": self.total_input,
            "total_output": self.total_output,
            "total": self.total_input + self.total_output,
            "nodes": self._usages,
        }
