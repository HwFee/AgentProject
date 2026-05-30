# Agent 工作指南

## 项目结构

前后端分离的 AI 报告生成系统：

- `backend/` — Python FastAPI + SQLAlchemy (async) + LangGraph/LangChain + Celery
  - 入口：`main.py`
  - 数据库：PostgreSQL (asyncpg)，Celery 用 Redis
  - 模型：`models/`，路由：`routers/`，服务：`services/`
  - 静态文件挂载在 `/static`，对应 `images/` 目录
- `frontend/` — React 19 + Vite + TypeScript + Tailwind CSS
  - 入口：`src/main.tsx`，路由：`src/App.tsx`
  - 状态管理：Zustand，数据获取：TanStack Query
  - 路径别名：`@/` 映射到 `src/`
- `skills/` — Agent 技能库（docx/pdf/pptx/xlsx 等文档处理）

## CodeGraph

项目已安装 CodeGraph v0.9.6，索引位于 `.codegraph/codegraph.db`。
**查看代码结构、符号关系、调用链时，优先使用 CodeGraph 而不是手动 grep。**
初始化/同步：`codegraph init -i`（在项目根目录）

## 开发命令

### 后端
```bash
cd backend
# 安装依赖
pip install -r requirements.txt
# 启动服务
uvicorn main:app --reload --port 8000
# 启动 Celery worker
celery -A config.celery worker --loglevel=info
```

### 前端
```bash
cd frontend
# 安装依赖
npm install
# 开发服务器
npm run dev        # 默认端口 5173
# 构建
npm run build
# 检查
npm run lint
```

## 搜索规范

1. **默认搜索工具**：使用 anysearch（已配置为远程 MCP）
2. **涉及具体时间时**：先用 Python `datetime.now()` 查看当前时间，再进行搜索
3. **遇到具体技术文档/库问题时**：调用 Context7 MCP 获取最新文档

## 数据库

- 使用 SQLAlchemy 2.0 async ORM
- 数据库 URL 从环境变量读取（`DATABASE_URL`）
- Web 服务用连接池引擎，`max_overflow=20, pool_size=10`
- Celery Worker 用 `NullPool` 避免并发问题
- 启动时自动建表：`Base.metadata.create_all`

## 注意事项

- 后端 CORS 已配置允许 `localhost:5173`
- 前端 TypeScript 严格模式开启，`noUnusedLocals` 和 `noUnusedParameters` 为 true
- `.log` 文件已加入 `.gitignore`，不要追踪日志
- `skills/` 下部分目录是独立 git 仓库（如 `academic-deep-research`, `csv-data-summarizer` 等）

## 变更同步规范

**任何代码修改、新增功能、配置变更或新约定，都必须同步更新 `AGENTS.md`。**

- 添加新依赖 → 更新开发命令或项目结构章节
- 修改目录结构 → 更新项目结构章节
- 新增代码规范或约束 → 追加到对应章节或新建章节
- 变更数据库配置 → 更新数据库章节
- **原则：`AGENTS.md` 必须始终准确反映项目的当前状态**，不能与实际代码脱节
