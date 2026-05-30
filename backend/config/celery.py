import logging

logger = logging.getLogger(__name__)

try:
    from celery import Celery
    from config.settings import settings

    celery_app = Celery(
        "report_worker",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=["workers.report_worker"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=600,
        worker_prefetch_multiplier=1,
    )

    def is_celery_available() -> bool:
        """检查 Celery broker (Redis) 是否可连接"""
        try:
            conn = celery_app.connection()
            conn.connect()
            conn.release()
            return True
        except Exception as e:
            logger.debug(f"Celery broker 连接失败: {e}")
            return False

except ImportError:
    # Celery not installed - create a mock for development
    from uuid import uuid4

    class MockAsyncResult:
        def __init__(self):
            self.id = f"mock-{uuid4()}"

    class MockCelery:
        is_mock = True

        def send_task(self, name, args=None, kwargs=None):
            return MockAsyncResult()

    def is_celery_available() -> bool:
        return False

    celery_app = MockCelery()
    logger.warning("Celery 未安装，使用 mock 模式")
