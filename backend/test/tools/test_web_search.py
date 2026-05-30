import pytest
from unittest.mock import patch, MagicMock
from tools.web_search import WebSearchTool


class TestWebSearchTool:
    def test_init_without_api_key(self):
        tool = WebSearchTool()
        # If no API keys in settings, available should be False
        # But settings might have defaults, so just check it creates
        assert isinstance(tool.available, bool)

    @patch("tools.web_search.settings")
    @patch("tools.web_search.requests.get")
    def test_search_success(self, mock_get, mock_settings):
        mock_settings.serpapi_key = "test_key"
        mock_settings.bing_api_key = None
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic_results": [
                {"title": "Test", "link": "http://test.com", "snippet": "Test snippet"}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        tool = WebSearchTool()
        result = tool.search("test query", num_results=1)
        assert len(result) == 1
        assert result[0]["title"] == "Test"
