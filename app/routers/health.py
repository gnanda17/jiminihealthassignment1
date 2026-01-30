"""Health check endpoint for service monitoring."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Return service health status for load balancers and monitoring."""
    return {"status": "ok"}
