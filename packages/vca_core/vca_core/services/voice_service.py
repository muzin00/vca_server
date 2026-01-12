import base64
from pathlib import Path

from vca_core.interfaces.voice_repository import VoiceRepositoryProtocol
from vca_core.models import Voice


class VoiceService:
    def __init__(
        self,
        voice_repository: VoiceRepositoryProtocol,
        storage_path: str = "/tmp/voices",
    ) -> None:
        self.voice_repository = voice_repository
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def register_voice(
        self,
        speaker_id: int,
        audio_data: str,
        audio_format: str,
        sample_rate: int | None = None,
        channels: int | None = None,
    ) -> Voice:
        # Base64デコード（Data URL形式にも対応）
        if audio_data.startswith("data:"):
            audio_data = audio_data.split(",", 1)[1]

        audio_bytes = base64.b64decode(audio_data)

        # ファイル保存
        file_name = f"voice_{speaker_id}_{len(audio_bytes)}.{audio_format}"
        file_path = self.storage_path / file_name

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # データベースに登録
        voice = self.voice_repository.create(
            speaker_id=speaker_id,
            audio_file_path=str(file_path),
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
        )

        return voice
