from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://crm:crm@db:5432/crm"
    cors_origins: str = "http://localhost:5173"
    app_now: str = ""  # optional ISO date to freeze "today" for the countdown
    data_file: str = "/data/Aus_Guest_List_Augmented_v3.xlsx"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
