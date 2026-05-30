from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class ReportDraftSkill:
    skill_id = "writing.draft_report"
    name = "撰写初稿"
    description = "基于大纲、研究资料和数据分析生成报告初稿"

    SYSTEM_PROMPT = """你是一个专业的报告撰写专家，擅长将研究素材转化为结构清晰、内容详实的分析报告。

# 撰写规范
1. 使用 Markdown 格式输出
2. 结构清晰：标题、摘要、目录、正文、结论、参考来源
3. 语言专业、流畅，避免口语化表达
4. 基于提供的素材撰写，不要编造未提及的事实
5. 适当使用列表、表格增强可读性
6. 用中文撰写
7. 参考提供的大纲结构，但可根据素材适当调整

# 内容要求
- 摘要：200-300字，概括报告核心发现
- 正文：按逻辑分节，每节有明确的小标题
- 数据：引用素材中的具体数据，标注来源
- 结论：总结核心观点，给出建议或展望

# 注意事项
- 不要输出 "```markdown" 代码块标记，直接输出 Markdown 内容
- 不要在报告中解释你的写作过程
- 保持客观中立 tone"""

    def __init__(self):
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        outline = context.artifacts.get("report_outline", "")
        research_notes = context.artifacts.get("research_notes", "")
        data_insights = context.artifacts.get("data_insights", "")

        sections = []
        if outline:
            sections.append(f"## 报告大纲\n{outline}")
        if research_notes:
            sections.append(f"## 研究资料\n{research_notes}")
        if data_insights:
            sections.append(f"## 数据分析\n{data_insights}")

        material = "\n\n".join(sections)
        if not material.strip():
            material = "（未获取到有效的研究素材，请基于需求撰写框架性报告）"

        started = datetime.utcnow()
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"请基于以下素材撰写报告：\n\n{material}"},
        ]

        model = ModelRouter.select("write")
        response = self.client.chat_sync(messages=messages, model=model)

        content = response.get("content", "")
        content = self._strip_markdown_fences(content)

        context.tool_events.append({
            "event_type": "create_file",
            "title": "创建 初稿.md",
            "description": f"生成报告初稿，共 {len(content)} 字",
            "status": "completed",
            "input_data": {"has_outline": bool(outline), "has_research": bool(research_notes), "has_data": bool(data_insights)},
            "output_data": {"filename": "初稿.md", "length": len(content)},
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
