"""
Configuration Settings.

Loads environment variables such as the Google API Key.
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = "" # Default to empty string for testing without key if needed
    LLM_MODEL: str = "gemini-1.5-pro"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
