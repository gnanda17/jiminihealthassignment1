"""Audit log endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.db import InMemoryDB, get_db
from app.models import AuditLogEntry, AuditLogFilter, User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/encounters", response_model=list[AuditLogEntry])
async def list_audit_logs(
    user: User = Depends(get_current_user),
    db: InMemoryDB = Depends(get_db),
    encounter_id: str | None = Query(None, alias="encounterId"),
    user_id: str | None = Query(None, alias="userId"),
    date_from: datetime | None = Query(None, alias="dateFrom"),
    date_to: datetime | None = Query(None, alias="dateTo"),
) -> list[AuditLogEntry]:
    """List audit logs for PHI access.

    Filters:
    - encounterId: Filter by encounter
    - userId: Filter by user who accessed
    - dateFrom: Filter logs on or after this date
    - dateTo: Filter logs on or before this date
    """
    filter = AuditLogFilter(
        encounter_id=encounter_id,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    return await db.list_audit_logs(filter)
