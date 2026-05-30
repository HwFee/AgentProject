import re
from typing import Any, Dict, List

from agents.base import BaseAgent
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter


class ReviewAgent(BaseAgent):
    """评审 Agent：负责多报告竞争评审，选出最佳报告"""

    agent_type = "review"

    SYSTEM_PROMPT = """你是一个严格的质量评审专家，需要对多份竞争报告进行评审并选出最佳报告。

# 评审维度（每项满分10分）
1. **准确性**：数据、事实是否有依据，引用是否规范
2. **深度**：分析是否深入，是否有独到见解
3. **结构**：逻辑是否清晰，章节安排是否合理
4. **实用性**：建议是否 actionable，对决策是否有价值
5. **表达**：语言是否专业流畅，格式是否规范

# 输出格式
```
## 评审结果

### 报告A评分
- 准确性：X/10
- 深度：X/10
- 结构：X/10
- 实用性：X/10
- 表达：X/10
- 总分：XX/50

### 报告B评分
...

### 报告C评分
...

## 综合排名
1. 第一名：[报告ID] - [总分]分
2. 第二名：[报告ID] - [总分]分
3. 第三名：[报告ID] - [总分]分

## 最佳报告
winner: [报告ID]

## 选择理由
[详细说明为什么这份报告最好，以及其他报告的不足之处]

## 改进建议
[对最佳报告还可以如何改进]
```

# 要求
- 客观公正，不因报告长短而偏见
- 明确指出每份报告的优势和劣势
- 必须选出唯一的winner
- 用中文撰写"""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.client = DeepSeekClient()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        requirement = input_data.get("requirement", "")
        reports = input_data.get("competing_reports", [])

        if not reports:
            return {
                "content": "没有可供评审的报告",
                "winner": None,
                "scores": {},
                "usage": {},
                "agent_type": self.agent_type,
            }

        # 构建评审材料
        reports_text = self._format_reports(reports)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"用户需求：{requirement}\n\n{reports_text}\n\n请对以上报告进行评审并选出最佳报告："},
        ]

        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model)

        content = response.get("content", "")

        winner = self._extract_winner(content, reports)
        scores = self._extract_scores(content)

        best_report_content = self._get_best_report_content(reports, winner)
        final_content = self._build_final_content(content, best_report_content, winner, reports)

        return {
            "content": final_content,
            "winner": winner,
            "scores": scores,
            "full_review": content,
            "usage": response.get("usage", {}),
            "agent_type": self.agent_type,
        }

    def _format_reports(self, reports: List[Dict]) -> str:
        parts = []
        for i, report in enumerate(reports, 1):
            angle = report.get("angle", "")
            content = report.get("content", "")
            label = angle.split("：")[0] if "：" in angle else (angle or f"报告{i}")
            if len(content) > 3000:
                content = content[:3000] + "\n\n[报告内容过长，已截断...]"
            parts.append(f"""---
### 报告 {label}
**撰写角度**：{angle}

{content}
---""")
        return "\n\n".join(parts)

    def _extract_winner(self, content: str, reports: List[Dict] = None) -> str:
        patterns = [
            r"winner[:：]\s*(.+?)(?:\n|$)",
            r"最佳报告[:：]\s*(.+?)(?:\n|$)",
            r"第一名[:：]\s*(.+?)(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                winner_text = match.group(1).strip()
                if reports:
                    for report in reports:
                        node_id = report.get("node_id", "")
                        angle = report.get("angle", "")
                        label = angle.split("：")[0] if "：" in angle else angle
                        if winner_text in label or winner_text in node_id or label in winner_text:
                            return node_id
                return winner_text
        return ""

    def _extract_scores(self, content: str) -> Dict[str, Dict[str, int]]:
        """提取评分，返回 {report_id: {dimension: score}}"""
        scores = {}
        # 匹配 "报告A评分" 或 "write_1评分" 等格式
        sections = re.split(r"###\s+报告\s+(\w+)", content)
        for i in range(1, len(sections), 2):
            report_id = sections[i].strip()
            section = sections[i + 1] if i + 1 < len(sections) else ""
            report_scores = {}
            for dim in ["准确性", "深度", "结构", "实用性", "表达"]:
                match = re.search(rf"{dim}[：:]\s*(\d+)/10", section)
                if match:
                    report_scores[dim] = int(match.group(1))
            if report_scores:
                scores[report_id] = report_scores
        return scores

    def _get_best_report_content(self, reports: List[Dict], winner: str) -> str:
        for report in reports:
            if report.get("node_id") == winner:
                return report.get("content", "")
        # 如果没找到winner，返回第一个
        if reports:
            return reports[0].get("content", "")
        return ""

    def _build_final_content(self, review_content: str, best_report: str, winner: str, reports: List[Dict] = None) -> str:
        winner_label = winner
        if reports:
            for report in reports:
                if report.get("node_id") == winner:
                    angle = report.get("angle", "")
                    winner_label = angle.split("：")[0] if "：" in angle else (angle or winner)
                    break
        parts = [
            "# 评审总结",
            "",
            review_content,
            "",
            "---",
            "",
            f"# 最佳报告（{winner_label}）",
            "",
            best_report,
        ]
        return "\n".join(parts)
