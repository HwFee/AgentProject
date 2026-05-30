import asyncio
import traceback
import warnings
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import BaseAgent
from agents.data_analyst import DataAgent
from agents.research import ResearchAgent
from agents.reviewer import ReviewAgent
from agents.simple import SimpleAgent
from agents.writer import WriteAgent
from crud.report import ReportCRUD


class LangGraphExecutor:
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "LangGraphExecutor is deprecated. Use pipeline.executor.PipelineExecutor instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    AGENT_REGISTRY = {
        "research": ResearchAgent,
        "write": WriteAgent,
        "review": ReviewAgent,
        "data": DataAgent,
        "simple": SimpleAgent,
    }

    def __init__(self, dag: Dict[str, Any], task_id: int, db: AsyncSession):
        self.dag = dag
        self.nodes = dag.get("nodes", [])
        self.task_id = task_id
        self.db = db
        self._agent_map: Dict[str, BaseAgent] = {}
        self._node_db_ids: Dict[str, int] = {}
        self._results: Dict[str, Dict] = {}
        self._failed_nodes: set = set()
        self._completed_nodes: set = set()
        self._db_lock = asyncio.Lock()
        self._build_agents()

    def _build_agents(self):
        for node in self.nodes:
            agent_type = node.get("agent_type")
            node_id = node.get("id")
            agent_cls = self.AGENT_REGISTRY.get(agent_type)
            if agent_cls:
                self._agent_map[node_id] = agent_cls(node_id)

    async def execute(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """按层并行执行DAG"""
        # 计算每个节点的入度（依赖数量）
        in_degree = {n["id"]: 0 for n in self.nodes}
        adj = {n["id"]: [] for n in self.nodes}
        valid_ids = {n["id"] for n in self.nodes}

        for node in self.nodes:
            node_id = node["id"]
            for dep in node.get("depends_on", []):
                if dep in valid_ids:
                    adj[dep].append(node_id)
                    in_degree[node_id] += 1

        # 按层执行：每层是所有当前入度为0且未执行的节点
        remaining = set(valid_ids)
        while remaining:
            # 找出当前可以执行的节点（入度为0）
            ready = [
                n_id for n_id in remaining
                if in_degree.get(n_id, 0) == 0
            ]

            if not ready:
                # 死锁或循环依赖，跳出
                break

            # 并行执行当前层的所有节点
            await self._execute_layer(ready, initial_input)

            # 移除已执行的节点，更新后续节点的入度
            for n_id in ready:
                remaining.discard(n_id)
                for neighbor in adj.get(n_id, []):
                    in_degree[neighbor] -= 1

        return self._results

    async def _execute_layer(
        self, node_ids: List[str], initial_input: Dict[str, Any]
    ):
        """并行执行一层中的所有节点"""
        coros = [
            self._execute_single_node(node_id, initial_input)
            for node_id in node_ids
        ]
        await asyncio.gather(*coros, return_exceptions=True)

    async def _execute_single_node(
        self, node_id: str, initial_input: Dict[str, Any]
    ):
        """执行单个节点"""
        node = self._get_node(node_id)
        agent = self._agent_map.get(node_id)
        if not agent:
            return

        depends_on = node.get("depends_on", [])

        # 检查依赖是否全部成功
        failed_deps = [d for d in depends_on if d in self._failed_nodes]
        if failed_deps:
            await self._skip_node(node, agent, failed_deps)
            return

        agent_type = node.get("agent_type", "unknown")
        model = getattr(agent.client, "model", "deepseek-v4-pro")

        # 创建DB记录并更新为 running（串行保护，避免并发 session 冲突）
        async with self._db_lock:
            db_node = await ReportCRUD.create_agent_node(
                self.db, self.task_id, node_id, agent_type, model
            )
            self._node_db_ids[node_id] = db_node.id
            await ReportCRUD.update_node_status(
                self.db, db_node.id, "running"
            )
            await self.db.commit()

        try:
            node_input = self._build_node_input(initial_input, depends_on)
            # 为 write 节点添加撰写角度信息
            if agent_type == "write":
                node_input["writing_angle"] = node.get("description", "")
            # 为 review 节点收集所有报告
            if agent_type == "review":
                node_input["competing_reports"] = self._collect_reports()

            result = await asyncio.to_thread(agent.run, node_input)
            self._results[node_id] = result
            self._completed_nodes.add(node_id)

            output_for_db = {
                "content": result.get("content", ""),
                "sources": result.get("sources", []),
            }
            # review 节点额外保存评审结果
            if agent_type == "review":
                output_for_db["winner"] = result.get("winner")
                output_for_db["scores"] = result.get("scores")

            async with self._db_lock:
                await ReportCRUD.update_node_status(
                    self.db, db_node.id, "completed",
                    output_data=output_for_db,
                    token_usage=result.get("usage"),
                )
                await self.db.commit()

        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            async with self._db_lock:
                await ReportCRUD.update_node_status(
                    self.db, db_node.id, "failed",
                    output_data={"error": error_msg, "traceback": tb},
                )
                await self.db.commit()
            self._failed_nodes.add(node_id)
            self._results[node_id] = {
                "content": f"执行失败：{error_msg}",
                "agent_type": agent_type,
            }

    async def _skip_node(self, node: Dict, agent: BaseAgent, failed_deps: List[str]):
        """跳过因依赖失败而无法执行的节点"""
        node_id = node["id"]
        agent_type = node.get("agent_type", "unknown")
        model = getattr(agent.client, "model", "deepseek-v4-pro")

        async with self._db_lock:
            db_node = await ReportCRUD.create_agent_node(
                self.db, self.task_id, node_id, agent_type, model
            )
            self._node_db_ids[node_id] = db_node.id

            skip_msg = f"跳过执行：前置节点 {', '.join(failed_deps)} 失败"
            await ReportCRUD.update_node_status(
                self.db, db_node.id, "failed",
                output_data={"error": skip_msg},
            )
            await self.db.commit()
        self._failed_nodes.add(node_id)
        self._results[node_id] = {
            "content": skip_msg,
            "agent_type": agent_type,
        }

    def _collect_reports(self) -> List[Dict[str, Any]]:
        """收集所有撰写节点产生的报告，供评审使用"""
        reports = []
        for node_id, result in self._results.items():
            node = self._get_node(node_id)
            if node.get("agent_type") == "write":
                reports.append({
                    "node_id": node_id,
                    "content": result.get("content", ""),
                    "angle": node.get("description", ""),
                })
        return reports

    def _get_node(self, node_id: str) -> Dict:
        for node in self.nodes:
            if node["id"] == node_id:
                return node
        return {}

    def _get_node_label(self, node_id: str) -> str:
        node = self._get_node(node_id)
        desc = node.get("description", "")
        if desc:
            return desc.split("：")[0] if "：" in desc else desc
        return node_id

    def _build_node_input(self, initial_input: Dict, depends_on: List[str]) -> Dict:
        node_input = dict(initial_input)
        contexts = []
        all_sources = []

        for dep_id in depends_on:
            dep_result = self._results.get(dep_id, {})
            dep_content = dep_result.get("content", "")
            label = self._get_node_label(dep_id)
            if dep_id in self._failed_nodes:
                contexts.append(f"## {label}\n[该节点执行失败，无可用输出]")
            elif dep_content:
                contexts.append(f"## {label}\n{dep_content}")

            # 收集来源
            dep_sources = dep_result.get("sources", [])
            if dep_sources:
                all_sources.extend(dep_sources)

        if contexts:
            node_input["context"] = "\n\n".join(contexts)

        # 去重来源
        if all_sources:
            seen = set()
            unique_sources = []
            for s in all_sources:
                key = s.get("link", s.get("title", ""))
                if key and key not in seen:
                    seen.add(key)
                    unique_sources.append(s)
            node_input["sources"] = unique_sources

        return node_input

    def get_final_report(self) -> str:
        """获取最终报告：优先使用评审节点选出的最佳报告"""
        # 1. 先看评审节点的结果
        review_result = self._results.get("review", {})
        winner_id = review_result.get("winner")
        if winner_id and winner_id in self._results:
            return self._results[winner_id].get("content", "")

        # 2. 没有评审结果，找第一个成功的 write 节点
        for node_id, result in self._results.items():
            node = self._get_node(node_id)
            if node.get("agent_type") == "write" and node_id not in self._failed_nodes:
                return result.get("content", "")

        # 3. 兜底：返回任意结果
        if self._results:
            for result in self._results.values():
                content = result.get("content", "")
                if content:
                    return content

        return ""
