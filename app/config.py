"""Application configuration loaded from YAML."""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from config.yml."""

    model_config = ConfigDict(extra="ignore")

    encounter_types: frozenset[str] = Field(
        default=frozenset(
            {
                "initial_assessment",
                "follow_up",
                "treatment_session",
                "crisis_intervention",
                "discharge",
            }
        )
    )

    @classmethod
    def from_yaml(cls, path: Path | str = "config.yml") -> "Settings":
        """Load settings from a YAML configuration file."""
        config_path = Path(path)
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        if "encounter_types" in data:
            data["encounter_types"] = frozenset(data["encounter_types"])

        return cls(**data)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings.from_yaml()
