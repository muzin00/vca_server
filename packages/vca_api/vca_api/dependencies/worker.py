import logging

from vca_core.interfaces.worker_client import WorkerClientProtocol
from vca_worker.tasks import transcribe

logger = logging.getLogger(__name__)

# タイムアウト設定（秒）
TRANSCRIBE_TIMEOUT = 60
VOICEPRINT_TIMEOUT = 30


class CeleryWorkerClient(WorkerClientProtocol):
    """Celery経由でWorkerを呼び出すクライアント."""

    def transcribe(self, audio_bytes: bytes) -> str:
        """音声を文字起こし.

        Args:
            audio_bytes: 音声データ

        Returns:
            文字起こしテキスト（正規化済み）
        """
        logger.info(f"Sending transcribe task: {len(audio_bytes)} bytes")
        result = transcribe.delay(audio_bytes)
        text = result.get(timeout=TRANSCRIBE_TIMEOUT)
        logger.info(f"Transcription complete: '{text}'")
        return text

    def extract_voiceprint(self, audio_bytes: bytes) -> bytes:
        """声紋を抽出.

        Args:
            audio_bytes: 音声データ

        Returns:
            声紋ベクトル（256次元）
        """
        # TODO: Resemblyzer実装後に追加
        logger.warning("Voiceprint extraction not implemented, using stub")
        return b"\x00" * 256 * 4  # 256次元のfloat32のダミー


def get_worker_client() -> WorkerClientProtocol:
    """WorkerClientを提供する."""
    return CeleryWorkerClient()
