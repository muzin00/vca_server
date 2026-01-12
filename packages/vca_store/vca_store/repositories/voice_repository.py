from sqlmodel import Session
from vca_core.models import Voice


class VoiceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        speaker_id: int,
        audio_file_path: str,
        audio_format: str,
        sample_rate: int | None = None,
        channels: int | None = None,
    ) -> Voice:
        voice = Voice(
            speaker_id=speaker_id,
            audio_file_path=audio_file_path,
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
        )
        self.session.add(voice)
        self.session.commit()
        self.session.refresh(voice)
        return voice
