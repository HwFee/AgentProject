import pytest
from unittest.mock import MagicMock, patch
from tools.db_query import DBQueryTool


class TestDBQueryTool:
    def test_init(self):
        tool = DBQueryTool("sqlite:///:memory:")
        assert tool.connection_string == "sqlite:///:memory:"
