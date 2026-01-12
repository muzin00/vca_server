from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from vca_core.models.voice import Voice


class Speaker(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    speaker_id: str = Field(index=True, unique=True, max_length=100)
    speaker_name: str | None = Field(default=None, max_length=100)

    # Relationship
    voices: list["Voice"] = Relationship(back_populates="speaker")
