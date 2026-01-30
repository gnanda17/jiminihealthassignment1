"""Encounter endpoints."""

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.db import InMemoryDB, get_db
from app.models import Encounter, EncounterCreate, User

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
