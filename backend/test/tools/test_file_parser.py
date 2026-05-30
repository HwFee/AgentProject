import os
import tempfile

import pytest
from tools.file_parser import FileParser


class TestFileParser:
    def test_parse_txt(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello World")
            path = f.name
        try:
            result = FileParser.parse(path)
            assert result == "Hello World"
        finally:
            os.unlink(path)

    def test_parse_unsupported(self):
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            path = f.name
        try:
            result = FileParser.parse(path)
            assert "不支持的文件类型" in result
        finally:
            os.unlink(path)
