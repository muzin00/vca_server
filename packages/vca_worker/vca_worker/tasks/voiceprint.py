"""声紋抽出タスク."""

import logging

from vca_worker.celery_app import celery_app, get_speaker_model
from vca_worker.services.voiceprint_service import VoiceprintService

logger = logging.getLogger(__name__)


@celery_app.task(name="extract_voiceprint")
def extract_voiceprint(audio_bytes: bytes) -> bytes:
    """声紋を抽出するCeleryタスク.

    Args:
        audio_bytes: 音声データ

    Returns:
        声紋ベクトル（256次元のfloat32、1024バイト）
    """
    logger.info(f"Starting voiceprint extraction: {len(audio_bytes)} bytes")

    speaker = get_speaker_model()
    service = VoiceprintService(speaker)
    embedding = service.extract(audio_bytes)

    logger.info(f"Voiceprint extraction complete: {len(embedding)} bytes")
    return embedding
