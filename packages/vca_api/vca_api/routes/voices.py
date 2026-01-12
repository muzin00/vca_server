from fastapi import APIRouter, Depends
from vca_core.services.speaker_service import SpeakerService
from vca_core.services.voice_service import VoiceService

from vca_api.dependencies.speaker import get_speaker_service
from vca_api.dependencies.voice import get_voice_service
from vca_api.schemas.voices import VoiceRegistrationRequest, VoiceRegistrationResponse

router = APIRouter(prefix="/api/v1/voices", tags=["voices"])


@router.post("/register", status_code=201, response_model=VoiceRegistrationResponse)
async def register_voice(
    request: VoiceRegistrationRequest,
    speaker_service: SpeakerService = Depends(get_speaker_service),
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceRegistrationResponse:
    # Speaker を登録または取得
    speaker = speaker_service.register_speaker(
        speaker_id=request.speaker_id,
        speaker_name=request.speaker_name,
    )

    assert speaker.id is not None

    # 音声データを登録
    voice = voice_service.register_voice(
        speaker_id=speaker.id,
        audio_data=request.audio_data,
        audio_format=request.audio_format or "wav",
        sample_rate=request.sample_rate,
        channels=request.channels,
    )

    return VoiceRegistrationResponse(
        voice_id=voice.public_id,
        speaker_id=speaker.speaker_id,
        speaker_name=speaker.speaker_name,
        status="registered",
    )
