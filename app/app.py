"""FastAPI application factory and router configuration."""

from fastapi import FastAPI

from app.middleware import RequestLoggingMiddleware
from app.routers import audit, encounters, health

app = FastAPI(title="Patient Encounter API")

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(encounters.router)
app.include_router(audit.router)
