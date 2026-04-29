from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from env vars or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = Field(default="openai", description="Current supports: openai")
    llm_model: str = Field(default="gpt-4.1-mini", description="Chat model name")
    openai_api_key: str | None = None

    # Ecosystem integration URLs / tokens
    prometheus_base_url: str | None = None
    grafana_base_url: str | None = None
    grafana_api_token: str | None = None

    kubernetes_namespace: str = "default"

    jira_base_url: str | None = None
    jira_email: str | None = None
    jira_api_token: str | None = None

    slack_bot_token: str | None = None
    slack_channel: str | None = None

    webhook_timeout_seconds: int = 20
