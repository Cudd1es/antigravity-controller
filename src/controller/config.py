"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application settings for Discord Bot, Gemini AI, and security."""

    # Discord
    discord_token: str = ""
    discord_guild_id: str = ""

    # Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Security
    allowed_directories: list[str] = field(default_factory=list)
    allowed_user_ids: list[str] = field(default_factory=list)
    max_file_size_kb: int = 500
    command_timeout_seconds: int = 30
    require_confirmation: bool = True

    @classmethod
    def from_env(cls) -> "Config":
        """Create Config from environment variables."""
        return cls(
            discord_token=os.getenv("DISCORD_TOKEN", ""),
            discord_guild_id=os.getenv("DISCORD_GUILD_ID", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            allowed_directories=[
                d.strip()
                for d in os.getenv("ALLOWED_DIRECTORIES", "").split(",")
                if d.strip()
            ],
            allowed_user_ids=[
                u.strip()
                for u in os.getenv("ALLOWED_USER_IDS", "").split(",")
                if u.strip()
            ],
            max_file_size_kb=int(os.getenv("MAX_FILE_SIZE_KB", "500")),
            command_timeout_seconds=int(os.getenv("COMMAND_TIMEOUT_SECONDS", "30")),
            require_confirmation=os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true",
        )

    def validate(self) -> list[str]:
        """Validate required configuration. Returns list of error messages."""
        errors = []
        if not self.discord_token:
            errors.append("DISCORD_TOKEN is required")
        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY is required")
        if not self.allowed_directories:
            errors.append("ALLOWED_DIRECTORIES must contain at least one path")
        return errors
