from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class QualityReviewSkill:
    skill_id = "review.quality_check"
    name = "质量检查"
    description = "检查报告是否满足需求，给出质量评估和改进建议"

    SYSTEM_PROMPT = """你是一个严格的质量评审专家，请对报告进行质量检查。

# 检查维度（每项满分10分）
1. **需求匹配度**：报告是否覆盖了用户的核心需求
2. **内容深度**：分析是否深入，是否有独到见解
3. **结构质量**：逻辑是否清晰，章节安排是否合理
4. **数据准确性**：数据引用是否规范，来源是否可信
5. **表达质量**：语言是否专业自然，是否有 AI 痕迹

# 输出格式
```
## 质量检查报告

### 评分
- 需求匹配度：X/10
- 内容深度：X/10
- 结构质量：X/10
- 数据准确性：X/10
- 表达质量：X/10
- 总分：XX/50

### 优点
- ...

### 需要改进
- ...

### 结论
PASS / NEEDS_REVISION
```

# 要求
- 客观公正
- 如果总分 >= 35，结论为 PASS
- 如果总分 < 35，结论为 NEEDS_REVISION 并列出具体改进点
- 用中文撰写"""

    def __init__(self):
        self.client = DeepSeekClient()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        report = context.artifacts.get("polished_report", "")
        requirement = context.artifacts.get("normalized_requirement", context.requirement)

        started = datetime.utcnow()
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"用户需求：\n{requirement}\n\n报告内容：\n{report}\n\n请进行质量检查："},
        ]

        model = ModelRouter.select("review")
        response = self.client.chat_sync(messages=messages, model=model)

        content = response.get("content", "")
        quality_passed = self._parse_quality_result(content)

        context.tool_events.append({
            "event_type": "review",
            "title": "质量检查完成",
            "description": f"检查{'通过' if quality_passed else '未通过'}，详见评审意见",
            "status": "completed",
            "input_data": {"report_length": len(report)},
            "output_data": {"passed": quality_passed, "summary": content[:300]},
            "started_at": started,
            "completed_at": datetime.utcnow(),
        })

        return SkillResult(
            output=content,
            artifacts={
                "quality_passed": quality_passed,
                "quality_report": content,
            },
            token_usage=response.get("usage", {}),
        )

    def _parse_quality_result(self, content: str) -> bool:
        content_upper = content.upper()
        if "NEEDS_REVISION" in content_upper:
            return False
        if "PASS" in content_upper:
            return True
        return True
