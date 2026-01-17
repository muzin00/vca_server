from fastapi import APIRouter

from vca_api.schemas.auth import AuthRegisterRequest, AuthRegisterResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=AuthRegisterResponse)
async def register(
    request: AuthRegisterRequest,
) -> AuthRegisterResponse:
    """話者登録（音声ファイル + パスフレーズ + 声紋）."""
    # Phase 1: スタブ実装（固定値を返す）
    return AuthRegisterResponse(
        speaker_id=request.speaker_id,
        speaker_name=request.speaker_name,
        voice_sample_id="vs_stub123",
        voiceprint_id="vp_stub456",
        passphrase="スタブパスフレーズ",
        status="registered",
    )
