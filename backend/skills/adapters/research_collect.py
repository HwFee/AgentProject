from datetime import datetime

from pipeline.types import PipelineContext, PipelineStep, SkillResult
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter
from tools.web_search import WebSearchTool


class ResearchCollectSkill:
    skill_id = "research.collect"
    name = "资料收集"
    description = "网络搜索和附件摘要，收集研究资料"

    SYSTEM_PROMPT = """你是一个专业的研究分析师。根据用户需求和搜索结果，撰写结构化研究摘要。

# 输出格式
按主题分节撰写，每个观点标注来源编号 [1]、[2] 等。
包含关键数据、事实和趋势判断。
如果搜索结果不足，明确说明数据缺失的局限性。

# 注意事项
- 不要编造数据，所有结论必须基于搜索结果或附件内容
- 摘要控制在800-1500字
- 用中文撰写"""

    def __init__(self):
        self.client = DeepSeekClient()
        self.search_tool = WebSearchTool()

    def execute(self, context: PipelineContext, step: PipelineStep) -> SkillResult:
        normalized_req = context.artifacts.get("normalized_requirement", context.requirement)
        attachments = context.artifacts.get("attachments", [])

        search_queries = self._generate_search_queries(normalized_req)

        all_results = []
        for query in search_queries:
            search_started = datetime.utcnow()
            results = self.search_tool.search(query, num_results=5)
            all_results.extend(results)
            valid = [r for r in results if r.get("link") and "error" not in r]
            context.tool_events.append({
                "event_type": "search",
                "title": f"搜索 \"{query}\"",
                "description": f"找到 {len(valid)} 条结果",
                "status": "completed",
                "input_data": {"query": query},
                "output_data": {
                    "result_count": len(valid),
                    "results": [{"title": r.get("title", ""), "link": r.get("link", ""), "snippet": r.get("snippet", "")[:150]} for r in valid[:5]],
                },
                "started_at": search_started,
                "completed_at": datetime.utcnow(),
            })

        seen_links = set()
        unique_results = []
        for r in all_results:
            link = r.get("link", "")
            if link and link not in seen_links and "error" not in r:
                seen_links.add(link)
                unique_results.append(r)

        for r in unique_results[:5]:
            context.tool_events.append({
                "event_type": "read_url",
                "title": f"读取 \"{r.get('title', '无标题')}\"",
                "description": r.get("link", ""),
                "status": "completed",
                "input_data": {"url": r.get("link", "")},
                "output_data": {"title": r.get("title", ""), "snippet": r.get("snippet", "")[:200]},
                "started_at": None,
                "completed_at": datetime.utcnow(),
            })

        search_context = self._format_search_results(unique_results)
        if not unique_results:
            search_context = "（未获取到搜索结果，请基于已有知识进行分析）"

        attachment_context = self._format_attachments(attachments)

        for att in attachments:
            if isinstance(att, dict) and att.get("content"):
                context.tool_events.append({
                    "event_type": "read_file",
                    "title": f"读取附件 \"{att.get('filename', '')}\"",
                    "description": f"读取 {len(att.get('content', ''))} 字符",
                    "status": "completed",
                    "input_data": {"filename": att.get("filename", "")},
                    "output_data": {"length": len(att.get("content", ""))},
                    "started_at": None,
                    "completed_at": datetime.utcnow(),
                })

        write_started = datetime.utcnow()
        user_content = f"需求：\n{normalized_req}\n\n搜索结果：\n{search_context}"
        if attachment_context:
            user_content += f"\n\n附件内容：\n{attachment_context}"
        user_content += "\n\n请撰写研究摘要："

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        model = ModelRouter.select("research")
        response = self.client.chat_sync(messages=messages, model=model)

        sources = [{"title": r.get("title"), "link": r.get("link")} for r in unique_results]
        content = response.get("content", "")

        context.tool_events.append({
            "event_type": "create_file",
            "title": "创建 资料摘要.md",
            "description": f"生成研究摘要，引用 {len(sources)} 个来源",
            "status": "completed",
            "input_data": {"source_count": len(sources)},
            "output_data": {"filename": "资料摘要.md", "length": len(content)},
            "started_at": write_started,
            "completed_at": datetime.utcnow(),
        })

        return SkillResult(
            output=content,
            artifacts={"sources": sources, "search_queries": search_queries},
            token_usage=response.get("usage", {}),
        )

    def _generate_search_queries(self, requirement: str) -> list:
        messages = [
            {"role": "system", "content": "根据报告需求，生成3-5个精准的中文搜索查询词。每个查询词一行，不要编号。"},
            {"role": "user", "content": requirement},
        ]
        model = ModelRouter.select("research")
        response = self.client.chat_sync(messages=messages, model=model, temperature=0.5)
        queries = [q.strip("- ").strip() for q in response.get("content", "").split("\n") if q.strip()]
        if not queries:
            queries = [requirement[:80]]
        return queries[:5]

    def _format_search_results(self, results: list) -> str:
        if not results:
            return "无搜索结果"
        parts = []
        for i, r in enumerate(results[:15], 1):
            parts.append(f"[{i}] {r.get('title', '无标题')}\n{r.get('snippet', '无摘要')}\n来源：{r.get('link', '')}")
        return "\n\n".join(parts)

    def _format_attachments(self, attachments) -> str:
        if not attachments:
            return ""
        parts = []
        for att in attachments:
            if isinstance(att, dict):
                fname = att.get("filename", "")
                content = att.get("content", "")
                if content:
                    parts.append(f"### {fname}\n{content[:2000]}")
        return "\n\n".join(parts)
