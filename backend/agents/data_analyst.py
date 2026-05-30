import os
import re
from typing import Any, Dict

from agents.base import BaseAgent
from services.llm_client import DeepSeekClient
from services.model_router import ModelRouter
from tools.code_executor import CodeExecutor


class DataAgent(BaseAgent):
    """数据分析 Agent：负责数据计算、图表生成"""

    agent_type = "data"

    SYSTEM_PROMPT = """你是一个专业的数据分析师，擅长用 Python 进行数据处理和可视化分析。

# 工作流程
1. 仔细阅读用户的需求和提供的上下文
2. 检查是否有附件数据文件（CSV、Excel、JSON 等）
3. 编写完整、可运行的 Python 代码
4. 代码执行后，解释分析结果

# 编码规范
- 代码必须完整可运行，使用 print() 输出关键结果
- 如果需要图表，保存为 PNG 文件到当前目录，并用 print 输出文件路径
- 必须处理异常和空数据情况
- 代码块用 ```python 包裹

# 可用库
pandas, numpy, matplotlib, seaborn, json, csv, os, sys

# 附件数据处理
如果用户上传了附件，文件路径会在输入数据的 attachments 字段中提供。
读取附件的示例代码：
```python
import pandas as pd
# 假设附件是 CSV
df = pd.read_csv("/path/to/file.csv")
print(df.head())
```

# 图表保存
```python
import matplotlib.pyplot as plt
plt.savefig("chart.png")
print("chart.png")  # 输出文件路径
```

# 错误处理
如果代码执行失败，请分析错误原因并在下一次尝试中修复。
不要猜测数据内容，必须基于实际代码执行结果进行解释。"""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.client = DeepSeekClient()
        self.executor = CodeExecutor(timeout=60)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        context = self._format_context(input_data)

        # 构建附件文件路径信息
        attachments_info = self._build_attachments_info(input_data)
        if attachments_info:
            context += f"\n\n{attachments_info}"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"请编写 Python 代码完成以下分析：\n\n{context}"},
        ]

        model = ModelRouter.select(self.agent_type)
        response = self.client.chat_sync(messages=messages, model=model)

        code = response.get("content", "")
        extracted_code = self._extract_code(code)

        if extracted_code:
            exec_result = self.executor.run(extracted_code)
        else:
            exec_result = {"success": False, "output": "", "error": "未能从 LLM 响应中提取有效代码"}

        explanation = self._explain_results(code, exec_result, input_data.get("requirement", ""))

        return {
            "content": explanation,
            "code": extracted_code,
            "code_result": exec_result,
            "usage": response.get("usage", {}),
            "agent_type": self.agent_type,
        }

    def _build_attachments_info(self, input_data: Dict) -> str:
        """构建附件文件路径信息供 LLM 使用"""
        attachments = input_data.get("attachments")
        if not attachments:
            return ""

        if isinstance(attachments, list):
            lines = ["# 附件文件"]
            for i, att in enumerate(attachments, 1):
                if isinstance(att, dict):
                    path = att.get("local_path") or att.get("file_path") or att.get("path", "")
                    fname = att.get("filename", "")
                    if path:
                        lines.append(f"{i}. {fname}: {path}")
                elif isinstance(att, str):
                    lines.append(f"{i}. {att}")
            return "\n".join(lines)
        elif isinstance(attachments, str):
            return f"# 附件内容\n{attachments}"
        return ""

    def _extract_code(self, content: str) -> str:
        match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r"```\n(.*?)```", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content.strip()

    def _explain_results(self, code: str, exec_result: Dict, requirement: str) -> str:
        if not exec_result["success"]:
            return f"代码执行失败：{exec_result['error']}"

        output = exec_result.get("output", "")
        if not output.strip():
            return "代码执行成功，但没有输出内容。"

        # 收集生成的图表文件
        chart_files = []
        for line in output.split("\n"):
            line = line.strip()
            if line.endswith((".png", ".jpg", ".svg")) and os.path.exists(line):
                chart_files.append(line)

        parts = ["## 分析结果", "", f"```\n{output}\n```"]
        if chart_files:
            parts.extend(["", "## 生成的图表", ""])
            for f in chart_files:
                parts.append(f"- {f}")

        return "\n".join(parts)
