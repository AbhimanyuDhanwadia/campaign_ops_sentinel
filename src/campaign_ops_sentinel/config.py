from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    app_env: str
    shadow_mode: bool
    database_url: str
    api_key: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        app_env = getenv("APP_ENV", "development").lower()
        api_key = getenv("API_KEY") or None
        if app_env not in {"development", "test", "production"}:
            raise RuntimeError("APP_ENV must be development, test, or production")
        if app_env == "production" and not api_key:
            raise RuntimeError("API_KEY must be set when APP_ENV=production")
        return cls(
            app_env=app_env,
            shadow_mode=getenv("SHADOW_MODE", "true").lower() == "true",
            database_url=getenv("DATABASE_URL", "sqlite:///./data/campaign_ops.db"),
            api_key=api_key,
        )


settings = Settings.from_env()
