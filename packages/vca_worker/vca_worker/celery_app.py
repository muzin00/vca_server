import logging
from typing import Any

from celery import Celery
from celery.signals import worker_process_init
from vca_infra.model_loader import load_models
from vca_infra.settings import celery_settings

logger = logging.getLogger(__name__)

# Celeryアプリ
celery_app = Celery(
    "vca_worker",
    broker=celery_settings.CELERY_BROKER_URL,
    backend=celery_settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="pickle",
    accept_content=["pickle"],
    result_serializer="pickle",
    task_track_started=True,
    task_time_limit=60,  # 1分でタイムアウト
)

# タスクモジュールを自動検出
celery_app.autodiscover_tasks(["vca_worker.tasks"])


@worker_process_init.connect
def init_worker(**kwargs: Any):
    """Workerプロセス起動時にモデルをロード."""
    load_models()
