from typing import Any, Dict

from agents.base import BaseAgent
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class WriteAgent(BaseAgent):
    """撰写 Agent：负责报告撰写"""

    agent_type = "write"

    SYSTEM_PROMPT = """你是一个专业的报告撰写专家，擅长将研究素材转化为结构清晰、内容详实的分析报告。

# 撰写规范
1. 使用 Markdown 格式输出
2. 结构清晰：标题、摘要、目录、正文、结论、参考来源
3. 语言专业、流畅，避免口语化表达
4. 基于提供的素材撰写，不要编造未提及的事实
5. 适当使用列表、表格增强可读性
6. 用中文撰写

# 内容要求
- 摘要：200-300字，概括报告核心发现
- 正文：按逻辑分节，每节有明确的小标题
- 数据：引用素材中的具体数据，标注来源
- 结论：总结核心观点，给出建议或展望
- 如果某些素材缺失或为空，注明"该部分数据暂缺"

# 注意事项
- 不要输出 "```markdown" 代码块标记，直接输出 Markdown 内容
- 不要在报告中解释你的写作过程
- 保持客观中立 tone"""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.client = DeepSeekClient()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        context = self._format_context(input_data)
        writing_angle = input_data.get("writing_angle", "")

        # 检查上下文是否为空或不足
        has_content = bool(context.strip()) and len(context) > 50
        if not has_content:
            context = "（未获取到有效的研究素材，请基于报告标题和需求撰写一份框架性报告，并说明数据缺失的局限性）"

        # 构建用户提示，包含撰写角度
        user_prompt = "请基于以下素材撰写报告"
        if writing_angle:
            user_prompt += f"，注意以下撰写角度：{writing_angle}"
        user_prompt += f"\n\n{context}"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model)

        content = response.get("content", "")
        # 去除可能的 markdown 代码块包裹
        content = self._strip_markdown_fences(content)

        return {
            "content": content,
            "usage": response.get("usage", {}),
            "agent_type": self.agent_type,
        }

    def _strip_markdown_fences(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```markdown"):
            content = content[len("```markdown"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
        return content
