"""Encounter models."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import (
    Field,
    SecretStr,
    field_serializer,
    field_validator,
    model_validator,
)

from app.config import get_settings
from app.models.base import CamelModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_id() -> str:
    return str(uuid4())


class EncounterCreate(CamelModel):
    """Input for creating an encounter - only client-provided fields."""

    patient_id: SecretStr = Field(..., min_length=1, max_length=50)
    provider_id: str = Field(..., min_length=1, max_length=50)
    encounter_date: datetime
    encounter_type: str
    clinical_data: dict[str, Any] = Field(default_factory=dict)

    @field_serializer("patient_id")
    def serialize_patient_id(self, v: SecretStr) -> str:
        return v.get_secret_value()

    @field_validator("encounter_type")
    @classmethod
    def validate_encounter_type(cls, v: str) -> str:
        allowed = get_settings().encounter_types
        if v not in allowed:
            raise ValueError(f"Must be one of: {', '.join(sorted(allowed))}")
        return v


class Encounter(CamelModel):
    """Patient encounter record."""

    encounter_id: str = Field(default_factory=_generate_id)

    # Metadata (server-controlled)
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    created_by: str = ""

    # PHI fields
    patient_id: SecretStr = Field(..., min_length=1, max_length=50)
    clinical_data: dict[str, Any] = Field(default_factory=dict)

    # Encounter details
    provider_id: str = Field(..., min_length=1, max_length=50)
    encounter_date: datetime
    encounter_type: str

    @field_serializer("patient_id")
    def serialize_patient_id(self, v: SecretStr) -> str:
        """Expose patient_id in API responses (but still redacted in logs)."""
        return v.get_secret_value()

    @field_validator("encounter_type")
    @classmethod
    def validate_encounter_type(cls, v: str) -> str:
        allowed = get_settings().encounter_types
        if v not in allowed:
            raise ValueError(f"Must be one of: {', '.join(sorted(allowed))}")
        return v


class EncounterFilter(CamelModel):
    """Query parameters for filtering encounters."""

    patient_id: str | None = None
    provider_id: str | None = None
    encounter_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "EncounterFilter":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from cannot be after date_to")
        return self
