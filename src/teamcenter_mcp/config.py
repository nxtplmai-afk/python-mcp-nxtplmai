"""Application settings, loaded from environment variables and an optional ``.env`` file."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Teamcenter MCP server."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Teamcenter REST backend
    teamcenter_api_url: AnyHttpUrl = Field(description="Base URL of the Teamcenter REST backend.")
    teamcenter_http_timeout: float = Field(default=60.0, gt=0, description="Backend request timeout in seconds.")

    # MCP transport. "http" is FastMCP's Streamable HTTP transport.
    mcp_transport: Literal["http", "stdio"] = "http"
    # 0.0.0.0 accepts connections from other machines; use 127.0.0.1 for local-only access.
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000
    mcp_path: str = "/mcp"

    log_level: str = "INFO"

    @property
    def api_base_url(self) -> str:
        """Backend base URL without a trailing slash, ready for path joining."""
        return str(self.teamcenter_api_url).rstrip("/")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (read once, then cached)."""
    return Settings()
