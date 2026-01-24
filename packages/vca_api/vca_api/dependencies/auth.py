from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session
from vca_core.interfaces.storage import StorageProtocol
from vca_core.services.auth_service import AuthService
from vca_infra.model_loader import get_speaker_model, get_whisper_model
from vca_infra.repositories import (
    PassphraseRepository,
    SpeakerRepository,
    VoiceprintRepository,
    VoiceSampleRepository,
)
from vca_infra.services import TranscriptionService, VoiceprintService
from vca_infra.session import get_session
from vca_infra.settings import voiceprint_settings

from vca_api.dependencies.storage import get_storage


def get_auth_service(
    session: Session = Depends(get_session),
    storage: StorageProtocol = Depends(get_storage),
) -> Generator[AuthService, None, None]:
    """AuthServiceを提供する."""
    speaker_repository = SpeakerRepository(session)
    voice_sample_repository = VoiceSampleRepository(session)
    voiceprint_repository = VoiceprintRepository(session)
    passphrase_repository = PassphraseRepository(session)

    # サービスを直接生成
    whisper_model = get_whisper_model()
    speaker_model = get_speaker_model()
    transcription_service = TranscriptionService(whisper_model)
    voiceprint_service = VoiceprintService(speaker_model)

    service = AuthService(
        speaker_repository=speaker_repository,
        voice_sample_repository=voice_sample_repository,
        voiceprint_repository=voiceprint_repository,
        passphrase_repository=passphrase_repository,
        storage=storage,
        transcription_service=transcription_service,
        voiceprint_service=voiceprint_service,
        voice_similarity_threshold=voiceprint_settings.VOICEPRINT_SIMILARITY_THRESHOLD,
    )
    yield service
