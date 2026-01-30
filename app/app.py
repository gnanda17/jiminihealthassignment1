"""FastAPI application factory and router configuration."""

from fastapi import FastAPI

from app.routers import encounters, health

app = FastAPI(title="Patient Encounter API")

app.include_router(health.router)
app.include_router(encounters.router)
