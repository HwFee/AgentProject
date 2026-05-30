import logging
import sys
from typing import Any


def setup_logging(level: int = logging.INFO) -> None:
    """配置统一的日志格式和输出。"""
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # 降低第三方库的日志噪音
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
