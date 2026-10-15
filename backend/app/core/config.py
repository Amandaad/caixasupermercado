from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    access_token_minutes: int = 30
    cors_origins: str = "http://localhost:5173"
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

settings = Settings()
