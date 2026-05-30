from typing import Any, Dict

from agents.base import BaseAgent
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter
from tools.web_search import WebSearchTool


class ResearchAgent(BaseAgent):
    agent_type = "research"

    SYSTEM_PROMPT = """你是一个专业的研究分析师。根据用户需求进行深度调研并撰写结构化研究摘要。

# 工作流程
1. 分析用户需求的各个维度（主题、时间范围、关键指标等）
2. 生成3-5个针对性的搜索查询词
3. 执行搜索并收集结果
4. 基于搜索结果撰写结构化研究摘要
5. 标注所有引用来源

# 搜索策略
- 使用具体、明确的关键词，避免过于宽泛的查询
- 中英文混合搜索以获得更全面的结果
- 如果搜索结果为空或不足，扩大关键词范围再试一次

# 输出格式
按主题分节撰写，每个观点标注来源编号 [1]、[2] 等。
包含关键数据、事实和趋势判断。
如果搜索结果不足，明确说明数据缺失的局限性。

# 注意事项
- 不要编造数据，所有结论必须基于搜索结果
- 如果搜索工具不可用，基于你的知识提供分析，并注明"基于已有知识"
- 摘要控制在800-1500字"""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.client = DeepSeekClient()
        self.search_tool = WebSearchTool()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        title = input_data.get("title", "")
        requirement = input_data.get("requirement", "")
        context = self._format_context(input_data)

        # 生成搜索查询
        search_queries = self._generate_search_queries(title, requirement)

        # 执行搜索
        all_results = []
        for query in search_queries:
            results = self.search_tool.search(query, num_results=5)
            all_results.extend(results)

        # 去重（按链接）
        seen_links = set()
        unique_results = []
        for r in all_results:
            link = r.get("link", "")
            if link and link not in seen_links and "error" not in r:
                seen_links.add(link)
                unique_results.append(r)
            elif "error" in r:
                # 保留错误信息但不加入最终结果
                pass

        search_context = self._format_search_results(unique_results)

        # 如果没有搜索结果，给LLM一个提示
        if not unique_results:
            search_context = "（未获取到搜索结果，请基于已有知识进行分析，并明确说明数据来源的局限性）"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""{context}

搜索结果：
{search_context}

请撰写研究摘要："""},
        ]

        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model)

        return {
            "content": response.get("content", ""),
            "sources": [{"title": r.get("title"), "link": r.get("link")} for r in unique_results],
            "search_queries": search_queries,
            "result_count": len(unique_results),
            "usage": response.get("usage", {}),
            "agent_type": self.agent_type,
        }

    def _generate_search_queries(self, title: str, requirement: str) -> list:
        messages = [
            {"role": "system", "content": "根据报告需求，生成3-5个精准的中文搜索查询词。每个查询词一行，不要编号。考虑用户可能需要的数据维度（市场规模、趋势、竞争格局、政策等）。"},
            {"role": "user", "content": f"标题：{title}\n需求：{requirement}"},
        ]
        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model, temperature=0.5)
        queries = [q.strip("- ").strip() for q in response.get("content", "").split("\n") if q.strip()]
        if not queries:
            queries = [title]
            if requirement and requirement != title:
                queries.append(requirement[:80])
        return queries[:5]

    def _format_search_results(self, results: list) -> str:
        if not results:
            return "无搜索结果"
        parts = []
        for i, r in enumerate(results[:15], 1):
            parts.append(f"""[{i}] {r.get('title', '无标题')}
{r.get('snippet', '无摘要')}
来源：{r.get('link', '')}""")
        return "\n\n".join(parts)
