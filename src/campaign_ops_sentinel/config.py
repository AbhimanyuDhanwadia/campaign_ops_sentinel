from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    shadow_mode: bool = getenv("SHADOW_MODE", "true").lower() == "true"
    app_env: str = getenv("APP_ENV", "development")


settings = Settings()
