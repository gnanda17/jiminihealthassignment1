"""Application configuration loaded from YAML and environment."""

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

load_dotenv()


def _parse_api_keys_from_env() -> dict[str, dict[str, str]]:
    """Parse API_KEYS env var format: key:user_id:name,key:user_id:name"""
    env_keys = os.getenv("API_KEYS", "")
    if not env_keys:
        return {}

    result = {}
    for entry in env_keys.split(","):
        parts = entry.strip().split(":")
        if len(parts) == 3:
            key, user_id, name = parts
            result[key] = {"user_id": user_id, "name": name}
    return result


class Settings(BaseSettings):
    """Application settings loaded from config.yml and environment."""

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

    api_keys: dict[str, dict[str, str]] = Field(
        default={
            "dev-api-key": {"user_id": "dev-user", "name": "Development User"},
        }
    )

    @classmethod
    def from_yaml(cls, path: Path | str = "config.yml") -> "Settings":
        """Load settings from YAML config file, with env overrides."""
        config_path = Path(path)
        data: dict = {}

        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}

        if "encounter_types" in data:
            data["encounter_types"] = frozenset(data["encounter_types"])

        # API keys from env take precedence
        env_keys = _parse_api_keys_from_env()
        if env_keys:
            data["api_keys"] = env_keys

        return cls(**data)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings.from_yaml()
