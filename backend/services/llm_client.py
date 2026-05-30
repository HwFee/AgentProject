from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from config.settings import settings


class DeepSeekClient:
    """DeepSeek API 客户端（兼容 OpenAI API 格式）"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """异步调用 DeepSeek Chat API"""
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        if tools:
            params["tools"] = tools

        response = await self.client.chat.completions.create(**params)

        return {
            "content": response.choices[0].message.content or "",
            "tool_calls": response.choices[0].message.tool_calls,
            "usage": response.usage.model_dump() if response.usage else {},
            "model": model,
        }

    def chat_sync(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """同步调用（供非异步上下文使用）"""
        import asyncio
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(self.chat(messages, model, temperature, max_tokens))
