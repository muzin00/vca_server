import logging
from typing import Any

from celery import Celery
from celery.signals import worker_process_init
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

# モデル（Worker起動時にロード）
_whisper_model = None
_speaker_model = None


def get_whisper_model():
    """Whisperモデルを取得.

    Raises:
        RuntimeError: モデルがロードされていない場合
    """
    if _whisper_model is None:
        raise RuntimeError("Whisper model not loaded. Worker may not be initialized.")
    return _whisper_model


def get_speaker_model():
    """WeSpeaker話者モデルを取得.

    Raises:
        RuntimeError: モデルがロードされていない場合
    """
    if _speaker_model is None:
        raise RuntimeError("Speaker model not loaded. Worker may not be initialized.")
    return _speaker_model


@worker_process_init.connect
def init_worker(**kwargs: Any):
    """Workerプロセス起動時にモデルをロード."""
    global _whisper_model, _speaker_model
    import wespeakerruntime as wespeaker
    from faster_whisper import WhisperModel

    from vca_worker.settings import wespeaker_settings, whisper_settings

    # Whisperモデルのロード
    logger.info(
        f"Loading Whisper model: {whisper_settings.WHISPER_MODEL_SIZE} "
        f"(device={whisper_settings.WHISPER_DEVICE}, "
        f"compute_type={whisper_settings.WHISPER_COMPUTE_TYPE})"
    )

    _whisper_model = WhisperModel(
        whisper_settings.WHISPER_MODEL_SIZE,
        device=whisper_settings.WHISPER_DEVICE,
        compute_type=whisper_settings.WHISPER_COMPUTE_TYPE,
    )

    logger.info("Whisper model loaded successfully")

    # WeSpeakerモデルのロード
    logger.info(f"Loading WeSpeaker model: lang={wespeaker_settings.WESPEAKER_LANG}")

    _speaker_model = wespeaker.Speaker(lang=wespeaker_settings.WESPEAKER_LANG)

    logger.info("WeSpeaker model loaded successfully")
