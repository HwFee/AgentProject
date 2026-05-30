from config.settings import settings


class ModelRouter:
    """
    模型路由器：根据 Agent 类型和任务复杂度选择模型
    V4 Pro: 规划、研究、评审、数据分析（需要强推理）
    V4 Flash: 撰写、摘要、格式化（需要性价比）
    """

    PRO_MODELS = {
        "research", "review", "data", "planning",
        "requirement.intake", "planning.outline",
        "research.collect", "data.analyze",
        "review.quality_check",
    }

    @classmethod
    def select(cls, agent_type: str) -> str:
        """根据 Agent 类型选择模型"""
        if agent_type in cls.PRO_MODELS:
            return settings.deepseek_model_pro
        return settings.deepseek_model_flash

    @classmethod
    def select_by_complexity(cls, complexity: str) -> str:
        """根据复杂度标签选择模型（备用策略）"""
        if complexity == "high":
            return settings.deepseek_model_pro
        return settings.deepseek_model_flash
