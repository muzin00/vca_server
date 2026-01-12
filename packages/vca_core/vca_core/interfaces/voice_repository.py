from typing import Protocol

from vca_core.models import Voice


class VoiceRepositoryProtocol(Protocol):
    def create(
        self,
        speaker_id: int,
        audio_file_path: str,
        audio_format: str,
        sample_rate: int | None = None,
        channels: int | None = None,
    ) -> Voice: ...
