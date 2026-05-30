# Backend

AI 报告系统后端服务，基于 FastAPI 构建。

## 技术栈

- **FastAPI** —— Web 框架
- **SQLAlchemy 2.0** —— 异步 ORM
- **PostgreSQL** —— 数据库
- **Celery + Redis** —— 异步任务队列
- **LangGraph / LangChain** —— Agent 编排

## 目录说明

```
backend/
├── agents/        # Agent 定义（research、writer、reviewer 等）
├── config/        # 配置文件（database.py、celery.py、settings.py）
├── crud/          # 数据库 CRUD 封装
├── models/        # SQLAlchemy 数据模型
├── pipeline/      # 任务流水线（planner.py、executor.py、skill_pool.py）
├── routers/       # FastAPI 路由
├── schemas/       # Pydantic 请求/响应模型
├── scripts/       # 脚本（seed_dev_user.py 等）
├── services/      # 业务逻辑层
├── skills/        # 技能适配器（对接 skills/ 目录）
├── test/          # 测试用例
├── tools/         # 工具函数（代码执行、数据库查询、网页搜索）
├── utils/         # 通用工具（安全、异常、依赖注入）
└── workers/       # Celery 异步任务
```

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000

# 启动 Celery Worker
celery -A config.celery:celery_app worker --loglevel=info

# 运行测试
pytest
```

## API 文档

服务启动后访问：http://localhost:8000/docs
