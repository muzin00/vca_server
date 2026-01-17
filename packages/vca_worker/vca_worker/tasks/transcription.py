import logging

from vca_worker.celery_app import celery_app, get_whisper_model
from vca_worker.services.transcription_service import TranscriptionService
from vca_worker.utils.text_normalizer import normalize_text

logger = logging.getLogger(__name__)


@celery_app.task(name="transcribe")
def transcribe(audio_bytes: bytes) -> str:
    """文字起こしタスク.

    Args:
        audio_bytes: 音声データ（WAV, MP3等）

    Returns:
        正規化された文字起こしテキスト
    """
    model = get_whisper_model()
    service = TranscriptionService(model)
    text = service.transcribe(audio_bytes)

    # テキスト正規化
    normalized = normalize_text(text)
    logger.info(f"Normalized text: '{normalized}'")

    return normalized
