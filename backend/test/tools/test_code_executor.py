import pytest
from tools.code_executor import CodeExecutor


class TestCodeExecutor:
    def test_simple_execution(self):
        executor = CodeExecutor()
        result = executor.run("print(1 + 1)")
        assert result["success"] is True

    def test_execution_with_error(self):
        executor = CodeExecutor()
        result = executor.run("1/0")
        assert result["success"] is False
        assert "error" in result

    def test_timeout(self):
        executor = CodeExecutor(timeout=1)
        result = executor.run("import time; time.sleep(10)")
        assert result["success"] is False
