from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from config.settings import settings

# 创建异步数据库引擎（用于 Web 服务，连接池模式）
async_engine = create_async_engine(
    settings.database_url, echo=False, max_overflow=20, pool_size=10
)
# 创建异步会话工厂
LocalSession = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

# Worker 使用独立引擎，禁用连接池，避免 Celery solo pool 复用进程时的并发问题
worker_engine = create_async_engine(
    settings.database_url, echo=False, poolclass=NullPool
)
WorkerSession = async_sessionmaker(
    bind=worker_engine, expire_on_commit=False, class_=AsyncSession
)
