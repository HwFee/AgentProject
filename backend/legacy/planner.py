import json
import warnings
from typing import Any, Dict, List

from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class WorkflowPlanner:
    def __init__(self):
        warnings.warn(
            "WorkflowPlanner is deprecated. Use pipeline.planner.PipelinePlanner instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    """工作流规划器：生成并行多Agent竞争的DAG工作流

    DAG 结构（固定）：
    Layer 1: research_1, research_2, research_3  (并行，分别研究不同维度)
    Layer 2: write_1, write_2, write_3          (并行，分别从不同角度撰写)
    Layer 3: review                             (串行，评审并选出最佳报告)
    """

    SYSTEM_PROMPT = """你是一个工作流规划专家。请根据用户的报告需求，设计3个研究维度和3个撰写角度。

输出严格的JSON格式：
{
    "research_dimensions": [
        {"name": "维度名称", "focus": "该维度重点关注什么"},
        {"name": "维度名称", "focus": "该维度重点关注什么"},
        {"name": "维度名称", "focus": "该维度重点关注什么"}
    ],
    "writing_angles": [
        {"name": "角度A名称", "style": "该角度的写作风格和侧重点"},
        {"name": "角度B名称", "style": "该角度的写作风格和侧重点"},
        {"name": "角度C名称", "style": "该角度的写作风格和侧重点"}
    ]
}

要求：
1. 3个研究维度要互补，覆盖用户需求的不同方面
2. 3个撰写角度要差异化，产生有竞争力的不同版本
3. 研究维度用中文，撰写角度用中文
4. 不要输出任何JSON之外的文本"""

    FALLBACK_PLAN = {
        "research_dimensions": [
            {"name": "市场现状与趋势", "focus": "行业整体规模、增长趋势、主要驱动因素"},
            {"name": "竞争格局分析", "focus": "主要参与者、市场份额、竞争策略"},
            {"name": "政策法规环境", "focus": "相关政策、监管动态、合规要求"},
        ],
        "writing_angles": [
            {"name": "全面分析型", "style": "结构完整，覆盖所有维度，适合决策参考"},
            {"name": "数据驱动型", "style": "强调数据和量化分析，适合专业读者"},
            {"name": "战略建议型", "style": "聚焦 actionable insights，适合管理层"},
        ],
    }

    def __init__(self):
        self.client = DeepSeekClient()

    def plan(self, requirement: str) -> Dict[str, Any]:
        """根据需求生成并行DAG规划"""
        # 1. 用LLM分析需求，获取研究维度和撰写角度
        plan = self._generate_plan(requirement)

        # 2. 构建固定结构的并行DAG
        dag = self._build_parallel_dag(plan)
        return dag

    def _generate_plan(self, requirement: str) -> Dict[str, Any]:
        """使用LLM生成研究维度和撰写角度"""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"报告需求：\n\n{requirement}"},
        ]

        model = ModelRouter.select("planning")
        response = self.client.chat_sync(
            messages=messages,
            model=model,
            temperature=0.5,
        )

        content = response.get("content", "")

        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            plan = json.loads(json_str)
            # 校验结构
            if (
                "research_dimensions" in plan
                and "writing_angles" in plan
                and len(plan["research_dimensions"]) >= 3
                and len(plan["writing_angles"]) >= 3
            ):
                return plan
        except (json.JSONDecodeError, IndexError, KeyError):
            pass

        return self.FALLBACK_PLAN

    def _build_parallel_dag(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """构建并行DAG结构"""
        research_dims = plan.get("research_dimensions", self.FALLBACK_PLAN["research_dimensions"])
        writing_angles = plan.get("writing_angles", self.FALLBACK_PLAN["writing_angles"])

        nodes = []
        research_node_ids = []
        write_node_ids = []

        # Layer 1: 3个研究员并行（不同维度）
        for i, dim in enumerate(research_dims[:3], 1):
            node_id = f"research_{i}"
            research_node_ids.append(node_id)
            nodes.append({
                "id": node_id,
                "agent_type": "research",
                "depends_on": [],
                "description": f"{dim['name']}：{dim['focus']}",
            })

        # Layer 2: 3个撰写员并行（不同角度，依赖所有研究员）
        for i, angle in enumerate(writing_angles[:3], 1):
            node_id = f"write_{i}"
            write_node_ids.append(node_id)
            nodes.append({
                "id": node_id,
                "agent_type": "write",
                "depends_on": research_node_ids.copy(),
                "description": f"{angle['name']}：{angle['style']}",
            })

        # Layer 3: 1个审核员（依赖所有撰写员）
        nodes.append({
            "id": "review",
            "agent_type": "review",
            "depends_on": write_node_ids.copy(),
            "description": "评审3个版本报告，选出最佳",
        })

        return {"nodes": nodes}
