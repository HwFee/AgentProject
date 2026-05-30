# AgentProject

AI 报告生成系统 —— 基于多 Agent 协作的智能报告生成平台。

## 项目架构

前后端分离的 monorepo 项目：

| 目录 | 技术栈 | 说明 |
|------|--------|------|
| `backend/` | Python + FastAPI + SQLAlchemy + Celery | 后端 API 服务、异步任务队列 |
| `frontend/` | React 19 + Vite + TypeScript + Tailwind CSS | 前端 Web 应用 |
| `skills/` | Python 技能库 | 文档处理、数据分析等 Agent 技能 |

## 快速启动

使用一键启动脚本：

```bash
./start.sh
```

这会同时启动 Redis、后端服务、Celery Worker 和前端开发服务器：
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 手动启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
celery -A config.celery:celery_app worker --loglevel=info
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

## 核心功能

- 🤖 **多 Agent 协作** —— 需求理解、研究、写作、审核、导出等 Agent 协同工作
- 📄 **多格式导出** —— docx、pdf、pptx、xlsx
- 💬 **实时对话** —— 报告生成过程中可与 Agent 实时交互
- 📊 **Pipeline 编排** —— 基于 LangGraph 的任务流编排
- 🔐 **用户管理** —— 注册、登录、权限控制

## 环境依赖

- Python 3.10+
- Node.js 20+
- PostgreSQL
- Redis

## 环境变量

后端需要配置以下环境变量（在 `backend/.env` 中设置）：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串，如 `postgresql+asyncpg://user:pass@localhost:5432/dbname` |
| `REDIS_URL` | Redis 连接地址（Celery 使用） |

详细配置参见 `AGENTS.md`。

## 项目结构

```
.
├── backend/          # FastAPI 后端（详见 [backend/README.md](backend/README.md)）
│   ├── agents/       # Agent 定义
│   ├── config/       # 配置（数据库、Celery、日志）
│   ├── crud/         # 数据库 CRUD 操作
│   ├── models/       # SQLAlchemy 数据模型
│   ├── pipeline/     # 任务流水线（执行器、规划器）
│   ├── routers/      # API 路由
│   ├── schemas/      # Pydantic 请求/响应模型
│   ├── services/     # 业务逻辑
│   ├── skills/       # 技能适配器
│   ├── test/         # 测试用例
│   ├── tools/        # 工具函数（代码执行、数据库查询、网页搜索）
│   ├── utils/        # 通用工具（安全、异常、依赖注入）
│   └── workers/      # Celery 异步任务
├── frontend/         # React 前端（详见 [frontend/README.md](frontend/README.md)）
│   ├── src/
│   │   ├── app/      # 页面路由
│   │   ├── components/  # UI 组件
│   │   ├── stores/   # Zustand 状态管理
│   │   └── api/      # API 请求
│   └── ...
└── skills/           # 独立技能库
    ├── docx/         # Word 文档处理
    ├── pdf/          # PDF 处理
    ├── pptx/         # PPT 处理
    └── ...
```

## 开发规范

- 后端使用 SQLAlchemy 2.0 async ORM
- 前端开启 TypeScript 严格模式
- 任何代码变更需同步更新 `AGENTS.md`
- `.log` 文件不纳入版本控制

## 许可证

MIT
