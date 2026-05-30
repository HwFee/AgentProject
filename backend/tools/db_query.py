from typing import Any, Dict


class DBQueryTool:
    """数据库查询工具，支持任意 SQLAlchemy 兼容的数据库"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def query(self, sql: str) -> Dict[str, Any]:
        """执行 SQL 查询并返回结果"""
        try:
            from sqlalchemy import create_engine
            import pandas as pd

            engine = create_engine(self.connection_string)
            df = pd.read_sql(sql, engine)

            return {
                "success": True,
                "data": df.to_dict(orient="records"),
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "error": "",
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "columns": [],
                "row_count": 0,
                "error": str(e),
            }
