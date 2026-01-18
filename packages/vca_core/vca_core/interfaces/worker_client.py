from typing import Protocol


class WorkerClientProtocol(Protocol):
    """Workerクライアントのプロトコル."""

    def transcribe(self, audio_bytes: bytes, audio_format: str = "wav") -> str:
        """音声を文字起こし.

        Args:
            audio_bytes: 音声データ
            audio_format: 音声フォーマット（wav, webm, mp3等）

        Returns:
            文字起こしテキスト（正規化済み）
        """
        ...

    def extract_voiceprint(
        self, audio_bytes: bytes, audio_format: str = "wav"
    ) -> bytes:
        """声紋を抽出.

        Args:
            audio_bytes: 音声データ
            audio_format: 音声フォーマット（wav, webm, mp3等）

        Returns:
            声紋ベクトル（256次元）
        """
        ...

    def compare_voiceprints(self, embedding1: bytes, embedding2: bytes) -> float:
        """2つの声紋を比較し類似度を返す.

        Args:
            embedding1: 声紋ベクトル1
            embedding2: 声紋ベクトル2

        Returns:
            コサイン類似度（0.0〜1.0）
        """
        ...
