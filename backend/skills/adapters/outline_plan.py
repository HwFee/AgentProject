from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class OutlinePlanSkill:
    skill_id = "planning.outline"
    name = "生成大纲"
    description = "根据需求生成报告大纲结构"

    SYSTEM_PROMPT = """你是一个报告结构规划专家。请根据需求分析结果，生成一份详细的报告大纲。

输出 Markdown 格式的大纲，包含：
1. 报告标题
2. 摘要要点（3-5个）
3. 正文章节结构（含二级、三级标题）
4. 每个章节的要点提示
5. 结论方向

要求：
- 结构清晰，逻辑递进
- 章节数量适中（5-8个主章节）
- 用中文输出
- 直接输出 Markdown 大纲，不要解释"""

    def __init__(self):
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        normalized_req = context.artifacts.get("normalized_requirement", context.requirement)
        started = datetime.utcnow()

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"需求分析：\n\n{normalized_req}\n\n请生成报告大纲："},
        ]

        model = ModelRouter.select("planning")
        response = self.client.chat_sync(messages=messages, model=model, temperature=0.5)

        content = response.get("content", "")
        content = self._strip_markdown_fences(content)

        context.tool_events.append({
            "event_type": "create_file",
            "title": "创建 报告大纲.md",
            "description": f"生成报告大纲，包含多个章节结构",
            "status": "completed",
            "input_data": {"requirement_summary": normalized_req[:200]},
            "output_data": {"filename": "报告大纲.md", "length": len(content)},
            "started_at": started,
            "completed_at": datetime.utcnow(),
        })

        return SkillResult(
            output=content,
            token_usage=response.get("usage", {}),
        )

    def _strip_markdown_fences(self, content: str) -> str:
        content = content.strip()
        if content.startswith("```markdown"):
            content = content[len("```markdown"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
        return content
