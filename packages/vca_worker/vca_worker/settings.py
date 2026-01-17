from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    """Celery設定."""

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = {"env_prefix": ""}


class WhisperSettings(BaseSettings):
    """Whisperモデル設定."""

    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_LANGUAGE: str = "ja"

    model_config = {"env_prefix": ""}


celery_settings = CelerySettings()
whisper_settings = WhisperSettings()
