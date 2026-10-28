

from typing import Any

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Flash Ticket"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    IS_DEV: bool = False  # Indique l'environnement de développement

    # Base de données & Sécurité
    DATABASE_URL: PostgresDsn
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CORS & Hôtes Autorisés
    BACKEND_CORS_ORIGINS: list[str] | str = ["*"]
    ALLOWED_HOSTS: list[str] | str = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", "ALLOWED_HOSTS", mode="after")
    @classmethod
    def assemble_list_field(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instance unique des configurations
settings = Settings()
