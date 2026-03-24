"""
Configuration loader using pydantic-settings.

Loads secrets from .env.bot.secret file. This pattern:
- Keeps secrets out of code (security)
- Uses environment variables for configuration
- Validates required fields at startup
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to .env.bot.secret relative to this config.py file
ENV_FILE = Path(__file__).parent.parent / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = ""  # Optional for --test mode

    # LMS Backend API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API (for Task 3)
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"


# Global settings instance — load once at startup
settings = BotSettings()
