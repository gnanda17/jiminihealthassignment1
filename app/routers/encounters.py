"""Encounter endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.db import InMemoryDB, get_db
from app.models import Encounter, EncounterCreate, EncounterFilter, User

router = APIRouter(prefix="/encounters", tags=["encounters"])


@router.post("", response_model=Encounter)
async def create_encounter(
    data: EncounterCreate,
    user: User = Depends(get_current_user),
    db: InMemoryDB = Depends(get_db),
) -> Encounter:
    """Create a new encounter record.

    Returns the created encounter with generated ID.
    """
    encounter = Encounter(**data.model_dump(), created_by=user.user_id)
    return await db.create_encounter(encounter)


@router.get("", response_model=list[Encounter])
async def list_encounters(
    user: User = Depends(get_current_user),
    db: InMemoryDB = Depends(get_db),
    patient_id: str | None = Query(None, alias="patientId"),
    provider_id: str | None = Query(None, alias="providerId"),
    encounter_type: str | None = Query(None, alias="encounterType"),
    date_from: datetime | None = Query(None, alias="dateFrom"),
    date_to: datetime | None = Query(None, alias="dateTo"),
) -> list[Encounter]:
    """List encounters with optional filters.

    Filters:
    - patientId: Filter by patient
    - providerId: Filter by provider
    - encounterType: Filter by type
    - dateFrom: Filter encounters on or after this date
    - dateTo: Filter encounters on or before this date
    """
    filter = EncounterFilter(
        patient_id=patient_id,
        provider_id=provider_id,
        encounter_type=encounter_type,
        date_from=date_from,
        date_to=date_to,
    )
    encounters = await db.list_encounters(filter)

    # Log access to PHI for each encounter returned
    for encounter in encounters:
        await db.create_audit_log(encounter.encounter_id, user.user_id)

    return encounters


@router.get("/{encounter_id}", response_model=Encounter)
async def get_encounter(
    encounter_id: str,
    user: User = Depends(get_current_user),
    db: InMemoryDB = Depends(get_db),
) -> Encounter:
    """Retrieve a specific encounter by ID."""
    encounter = await db.get_encounter(encounter_id)

    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )

    # Log access to PHI
    await db.create_audit_log(encounter.encounter_id, user.user_id)

    return encounter
