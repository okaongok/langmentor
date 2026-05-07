import os
from celery import Celery

# 配置 Celery
celery_app = Celery(
    "langmentor",
    broker=os.getenv("CELERY_BROKER_URL", "amqp://admin:admin123@localhost:5672/"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["celery-worker.tasks"]
)

# 可选配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
)
