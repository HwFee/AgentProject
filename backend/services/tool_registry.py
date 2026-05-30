from typing import Any, Dict, List


class ToolRegistry:
    """工具注册中心：统一管理所有 Agent 可调用的工具"""

    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, tool_instance: Any):
        """注册一个工具实例"""
        self._tools[name] = tool_instance

    def get(self, name: str) -> Any:
        """获取工具实例"""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """列出所有已注册的工具名"""
        return list(self._tools.keys())

    def has_tool(self, name: str) -> bool:
        """检查工具是否已注册"""
        return name in self._tools
