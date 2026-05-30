from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class DeAiPolishSkill:
    skill_id = "writing.de_ai_polish"
    name = "去 AI 化润色"
    description = "将 AI 生成的报告改写为更自然的人类写作风格"

    SYSTEM_PROMPT = """你是一个资深的文字编辑，擅长将 AI 生成的文本改写为自然、专业的人类写作风格。

# 改写原则
1. 消除 AI 痕迹：去掉"首先...其次...最后"等机械连接词
2. 增加变化：句式长短交替，避免每段都是相同结构
3. 增强观点性：适当加入判断性语言，不要每句都是中性描述
4. 口语化专业表达：用行业人士的自然表达方式替代 AI 套话
5. 去掉冗余：删除不必要的过渡句和总结句
6. 保持专业性：改写不等于口语化，仍需保持报告的专业水准

# 需要消除的 AI 特征
- "值得注意的是"、"需要指出的是"
- "综上所述"、"总而言之"
- "在当今...的背景下"
- "随着...的发展"
- 过度使用"此外"、"同时"、"另外"
- 每段开头都用连接词
- 过于工整的并列结构

# 要求
- 保持原文的信息量不减少
- 保持 Markdown 格式不变
- 不要添加原文没有的数据或事实
- 直接输出改写后的完整报告，不要解释改写过程"""

    def __init__(self):
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        draft = context.artifacts.get("draft_report", "")

        if not draft or len(draft) < 100:
            context.tool_events.append({
                "event_type": "edit_file",
                "title": "更新 润色稿.md",
                "description": "初稿过短，跳过润色",
                "status": "completed",
                "input_data": {},
                "output_data": {"skipped": True},
                "started_at": None,
                "completed_at": datetime.utcnow(),
            })
            return SkillResult(output=draft, token_usage={})

        started = datetime.utcnow()
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"请改写以下报告，使其更像人类专业写手的作品：\n\n{draft}"},
        ]

        model = ModelRouter.select("write")
        response = self.client.chat_sync(messages=messages, model=model)

        content = response.get("content", draft)
        content = self._strip_markdown_fences(content)

        context.tool_events.append({
            "event_type": "edit_file",
            "title": "更新 润色稿.md",
            "description": f"去 AI 化润色完成，{len(draft)} → {len(content)} 字",
            "status": "completed",
            "input_data": {"original_length": len(draft)},
            "output_data": {"filename": "润色稿.md", "length": len(content)},
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
