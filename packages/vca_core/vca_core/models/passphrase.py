from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from vca_core.shared import model_fields

if TYPE_CHECKING:
    from vca_core.models.speaker import Speaker
    from vca_core.models.voice_sample import VoiceSample


class Passphrase(SQLModel, table=True):
    """パスフレーズモデル."""

    __tablename__ = "passphrase"  # type: ignore[assignment]

    id: int | None = model_fields.primary_key_field()
    public_id: str = model_fields.public_id_field()
    created_at: datetime = model_fields.created_at_field()
    updated_at: datetime = model_fields.updated_at_field()
    speaker_id: int = Field(foreign_key="speaker.id", index=True)
    voice_sample_id: int = Field(foreign_key="voice_sample.id", index=True)
    phrase: str = Field(max_length=500, description="正規化済みパスフレーズ")

    # Relationships
    speaker: "Speaker" = Relationship(back_populates="passphrases")
    voice_sample: "VoiceSample" = Relationship(back_populates="passphrase")
