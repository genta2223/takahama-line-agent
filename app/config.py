import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LINE_CHANNEL_SECRET: str = ""
    LINE_CHANNEL_ACCESS_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    BASE_URL: str = "http://localhost:8000"
    LIFF_ID: str = ""
    GAS_WEBHOOK_URL: str = ""
    ADMIN_EMAIL: str = "genta2223@gmail.com"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
