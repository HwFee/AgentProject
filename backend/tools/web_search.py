from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from config.settings import settings


class WebSearchTool:
    """网络搜索工具，支持 SerpAPI、Bing Search API 和 DuckDuckGo 免费搜索"""

    def __init__(self):
        self.serpapi_key: Optional[str] = getattr(settings, "serpapi_key", None) or None
        self.bing_api_key: Optional[str] = getattr(settings, "bing_api_key", None) or None
        self.has_paid_api = bool(self.serpapi_key or self.bing_api_key)

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """执行搜索并返回结果列表"""
        if self.serpapi_key:
            return self._search_serpapi(query, num_results)
        elif self.bing_api_key:
            return self._search_bing(query, num_results)
        else:
            # 免费 fallback: DuckDuckGo HTML 搜索
            return self._search_duckduckgo(query, num_results)

    def _search_serpapi(self, query: str, num_results: int) -> List[Dict]:
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "engine": "google",
            "num": num_results,
            "api_key": self.serpapi_key,
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": r.get("title", ""),
                    "link": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    def _search_bing(self, query: str, num_results: int) -> List[Dict]:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
        params = {"q": query, "count": num_results}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for r in data.get("webPages", {}).get("value", [])[:num_results]:
                results.append({
                    "title": r.get("name", ""),
                    "link": r.get("url", ""),
                    "snippet": r.get("snippet", ""),
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]

    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """DuckDuckGo HTML 搜索 — 无需 API key"""
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query, "kl": "zh-cn"}
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        try:
            resp = requests.post(url, data=params, headers=headers, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            # DuckDuckGo HTML 结果在 .result 类中
            for item in soup.select(".result")[:num_results]:
                title_tag = item.select_one(".result__title a") or item.select_one("a.result__a")
                snippet_tag = item.select_one(".result__snippet")

                title = title_tag.get_text(strip=True) if title_tag else ""
                link = title_tag.get("href", "") if title_tag else ""
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                # DuckDuckGo HTML 返回的是跳转链接，尝试提取真实 URL
                if link.startswith("/"):
                    link = f"https://html.duckduckgo.com{link}"

                if title:
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                    })

            if not results:
                # 尝试备用选择器
                for item in soup.select(".links_main")[:num_results]:
                    title_tag = item.select_one("a")
                    snippet_tag = item.select_one(".result__snippet")
                    title = title_tag.get_text(strip=True) if title_tag else ""
                    link = title_tag.get("href", "") if title_tag else ""
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    if title:
                        results.append({"title": title, "link": link, "snippet": snippet})

            return results
        except Exception as e:
            return [{"error": f"DuckDuckGo search failed: {e}"}]
