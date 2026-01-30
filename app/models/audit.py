"""Audit log models."""

from datetime import datetime

from pydantic import model_validator

from app.models.base import CamelModel


class AuditLogEntry(CamelModel):
    """Audit log entry tracking PHI access for HIPAA compliance."""

    audit_id: str
    encounter_id: str
    user_id: str
    timestamp: datetime


class AuditLogFilter(CamelModel):
    """Query parameters for filtering audit logs."""

    encounter_id: str | None = None
    user_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "AuditLogFilter":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from cannot be after date_to")
        return self
