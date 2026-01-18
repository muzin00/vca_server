import logging

from celery import Celery
from vca_core.interfaces.worker_client import WorkerClientProtocol

from vca_infra.settings import celery_settings

logger = logging.getLogger(__name__)

# タイムアウト設定（秒）
TRANSCRIBE_TIMEOUT = 60
VOICEPRINT_TIMEOUT = 30


class CeleryWorkerClient(WorkerClientProtocol):
    """Celery経由でWorkerを呼び出すクライアント."""

    def __init__(self) -> None:
        """Celeryアプリを初期化."""
        self._app = Celery(
            broker=celery_settings.CELERY_BROKER_URL,
            backend=celery_settings.CELERY_RESULT_BACKEND,
        )
        self._app.conf.update(
            task_serializer="pickle",
            result_serializer="pickle",
            accept_content=["pickle"],
        )

    def transcribe(self, audio_bytes: bytes) -> str:
        """音声を文字起こし.

        Args:
            audio_bytes: 音声データ

        Returns:
            文字起こしテキスト（正規化済み）
        """
        logger.info(f"Sending transcribe task: {len(audio_bytes)} bytes")
        result = self._app.send_task("transcribe", args=[audio_bytes])
        text: str = result.get(timeout=TRANSCRIBE_TIMEOUT)
        logger.info(f"Transcription complete: '{text}'")
        return text

    def extract_voiceprint(self, audio_bytes: bytes) -> bytes:
        """声紋を抽出.

        Args:
            audio_bytes: 音声データ

        Returns:
            声紋ベクトル（256次元のfloat32、1024バイト）
        """
        logger.info(f"Sending extract_voiceprint task: {len(audio_bytes)} bytes")
        result = self._app.send_task("extract_voiceprint", args=[audio_bytes])
        embedding: bytes = result.get(timeout=VOICEPRINT_TIMEOUT)
        logger.info(f"Voiceprint extraction complete: {len(embedding)} bytes")
        return embedding
