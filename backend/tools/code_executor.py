import os
import subprocess
import tempfile
from typing import Dict


class CodeExecutor:
    """
    Python 代码沙箱执行器
    注意：当前使用受限子进程，生产环境建议用 Docker 沙箱
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run(self, code: str) -> Dict:
        """执行 Python 代码，返回输出或错误信息"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            # 修复：先恢复 stdout/stderr，再打印捕获的内容
            wrapped_code = (
                "import sys\n"
                "from io import StringIO\n"
                "_stdout = StringIO()\n"
                "_stderr = StringIO()\n"
                "_old_stdout = sys.stdout\n"
                "_old_stderr = sys.stderr\n"
                "sys.stdout = _stdout\n"
                "sys.stderr = _stderr\n"
                f"{code}\n"
                "sys.stdout = _old_stdout\n"  # 先恢复
                "sys.stderr = _old_stderr\n"
                "print('__EXEC_RESULT__')\n"
                "print(_stdout.getvalue(), end='')\n"
                "print(_stderr.getvalue(), end='')\n"
            )
            f.write(wrapped_code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            stdout = result.stdout
            stderr = result.stderr

            if result.returncode != 0:
                # 提取错误信息中的有用部分
                error_msg = stderr or stdout or "Execution failed"
                # 去掉临时文件路径，避免泄露
                error_msg = error_msg.replace(temp_path, "<script>")
                return {
                    "success": False,
                    "output": "",
                    "error": error_msg,
                }

            # 提取实际输出（__EXEC_RESULT__ 之前的内容）
            if "__EXEC_RESULT__" in stdout:
                parts = stdout.split("__EXEC_RESULT__")
                actual_output = parts[0].strip() if parts else stdout.strip()
            else:
                actual_output = stdout.strip()

            return {
                "success": True,
                "output": actual_output,
                "error": "",
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Code execution timed out after {self.timeout}s",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
            }
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
