import base64
import logging
from uuid import uuid4

from vca_core.constants import MAX_AUDIO_SIZE
from vca_core.interfaces.storage import StorageProtocol
from vca_core.interfaces.voice_repository import VoiceRepositoryProtocol
from vca_core.models import Voice

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(
        self,
        voice_repository: VoiceRepositoryProtocol,
        storage: StorageProtocol,
    ):
        self.voice_repository = voice_repository
        self.storage = storage
        logger.info(f"VoiceService initialized with storage: {type(storage).__name__}")

    def register_voice(
        self,
        speaker_id: int,
        audio_data: str,
        audio_format: str,
        sample_rate: int | None = None,
        channels: int | None = None,
    ) -> Voice:
        logger.info(
            f"Registering voice for speaker_id={speaker_id}, format={audio_format}"
        )

        # Base64デコード（Data URL形式にも対応）
        if audio_data.startswith("data:"):
            audio_data = audio_data.split(",", 1)[1]

        audio_bytes = base64.b64decode(audio_data)
        logger.info(f"Decoded audio: {len(audio_bytes)} bytes")

        # サイズチェック
        if len(audio_bytes) > MAX_AUDIO_SIZE:
            raise ValueError(
                f"Audio size {len(audio_bytes)} bytes exceeds "
                f"maximum {MAX_AUDIO_SIZE} bytes"
            )

        # ストレージに保存
        file_path = f"voices/{speaker_id}/{uuid4()}.{audio_format}"
        logger.info(
            f"Uploading to storage: {file_path} using {type(self.storage).__name__}"
        )

        try:
            storage_path = self.storage.upload(
                data=audio_bytes,
                path=file_path,
                content_type=f"audio/{audio_format}",
            )
            logger.info(f"Upload successful: {storage_path}")
        except Exception as e:
            logger.error(f"Upload failed: {type(e).__name__}: {e}")
            raise

        # データベースに登録
        logger.info(f"Saving to database: audio_file_path={storage_path}")
        voice = self.voice_repository.create(
            speaker_id=speaker_id,
            audio_file_path=storage_path,
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
        )
        logger.info(f"Voice registered: public_id={voice.public_id}")

        return voice
