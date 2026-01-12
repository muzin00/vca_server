from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session
from vca_core.services.voice_service import VoiceService
from vca_store.repositories.voice_repository import VoiceRepository
from vca_store.session import get_session


def get_voice_service(
    session: Session = Depends(get_session),
) -> Generator[VoiceService, None, None]:
    repository = VoiceRepository(session)
    service = VoiceService(repository)
    yield service
