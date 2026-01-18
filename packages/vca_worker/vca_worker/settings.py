from pydantic_settings import BaseSettings


class WhisperSettings(BaseSettings):
    """Whisperモデル設定."""

    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_LANGUAGE: str = "ja"
    WHISPER_LOCAL_FILES_ONLY: bool = True

    model_config = {"env_prefix": ""}


class WeSpeakerSettings(BaseSettings):
    """WeSpeaker設定."""

    WESPEAKER_LANG: str = "en"

    model_config = {"env_prefix": ""}


whisper_settings = WhisperSettings()
wespeaker_settings = WeSpeakerSettings()
