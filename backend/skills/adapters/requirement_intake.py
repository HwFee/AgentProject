from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class RequirementIntakeSkill:
    skill_id = "requirement.intake"
    name = "需求理解"
    description = "清洗用户需求，提取目标、主题、格式、约束"

    SYSTEM_PROMPT = """你是一个需求分析专家。请分析用户的报告需求，提取以下信息并以JSON格式输出：

{
    "topic": "报告主题",
    "objectives": ["目标1", "目标2"],
    "scope": "范围描述",
    "format": "期望格式",
    "constraints": ["约束1", "约束2"],
    "keywords": ["关键词1", "关键词2"],
    "normalized_text": "整理后的完整需求描述"
}

要求：
1. 从用户输入中提取核心意图
2. 补充隐含的需求维度
3. 用中文输出
4. 只输出JSON，不要其他文本"""

    def __init__(self):
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        requirement = context.artifacts.get("requirement", context.requirement)
        started = datetime.utcnow()

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"报告需求：\n\n{requirement}"},
        ]

        model = ModelRouter.select("planning")
        response = self.client.chat_sync(messages=messages, model=model, temperature=0.3)
        content = response.get("content", requirement)

        context.tool_events.append({
            "event_type": "analyze_requirement",
            "title": "分析用户需求",
            "description": f"解析报告需求，提取主题、目标和约束",
            "status": "completed",
            "input_data": {"requirement": requirement[:500]},
            "output_data": {"parsed": content[:500]},
            "started_at": started,
            "completed_at": datetime.utcnow(),
        })

        return SkillResult(
            output=content,
            token_usage=response.get("usage", {}),
        )
