"""In-memory database for encounters and audit logs."""

from asyncio import Lock
from datetime import datetime, timezone
from uuid import uuid4

from app.models import AuditLogEntry, Encounter, EncounterFilter, AuditLogFilter


class InMemoryDB:
    """Simple in-memory storage for the exercise."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._encounters: dict[str, Encounter] = {}
        self._audit_logs: dict[str, AuditLogEntry] = {}

    # Encounters

    async def create_encounter(self, encounter: Encounter) -> Encounter:
        async with self._lock:
            self._encounters[encounter.encounter_id] = encounter
        return encounter

    async def get_encounter(self, encounter_id: str) -> Encounter | None:
        async with self._lock:
            return self._encounters.get(encounter_id)

    async def list_encounters(
        self, filter: EncounterFilter | None = None
    ) -> list[Encounter]:
        async with self._lock:
            encounters = list(self._encounters.values())

        if filter:
            if filter.patient_id:
                encounters = [
                    e
                    for e in encounters
                    if e.patient_id.get_secret_value() == filter.patient_id
                ]
            if filter.provider_id:
                encounters = [
                    e for e in encounters if e.provider_id == filter.provider_id
                ]
            if filter.encounter_type:
                encounters = [
                    e for e in encounters if e.encounter_type == filter.encounter_type
                ]
            if filter.date_from:
                encounters = [
                    e for e in encounters if e.encounter_date >= filter.date_from
                ]
            if filter.date_to:
                encounters = [
                    e for e in encounters if e.encounter_date <= filter.date_to
                ]

        return encounters

    # Audit logs

    async def create_audit_log(self, encounter_id: str, user_id: str) -> AuditLogEntry:
        entry = AuditLogEntry(
            audit_id=str(uuid4()),
            encounter_id=encounter_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
        )
        async with self._lock:
            self._audit_logs[entry.audit_id] = entry
        return entry

    async def list_audit_logs(
        self, filter: AuditLogFilter | None = None
    ) -> list[AuditLogEntry]:
        async with self._lock:
            logs = list(self._audit_logs.values())

        if filter:
            if filter.encounter_id:
                logs = [log for log in logs if log.encounter_id == filter.encounter_id]
            if filter.user_id:
                logs = [log for log in logs if log.user_id == filter.user_id]
            if filter.date_from:
                logs = [log for log in logs if log.timestamp >= filter.date_from]
            if filter.date_to:
                logs = [log for log in logs if log.timestamp <= filter.date_to]

        return logs


_db = InMemoryDB()


def get_db() -> InMemoryDB:
    """Dependency for injecting the database into routes."""
    return _db
