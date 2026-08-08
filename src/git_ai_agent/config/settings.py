"""YAML and environment-backed configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """Validated runtime settings."""

    default_repository: Path = Path(".")
    protected_branches: list[str] = Field(default_factory=lambda: ["main", "master"])
    command_timeout_seconds: int = Field(default=120, ge=1, le=3600)
    lint_commands: list[list[str]] = Field(default_factory=list)
    test_commands: list[list[str]] = Field(default_factory=list)
    minimum_coverage: int = Field(default=0, ge=0, le=100)
    blocking_severity: Literal["warning", "error", "critical"] = "critical"
    max_diff_bytes: int = Field(default=1_000_000, ge=1024)
    approval_ttl_seconds: int = Field(default=900, ge=30, le=86400)
    push_enabled: bool = True
    ai_provider: str = "local"
    allowed_repository_roots: list[Path] = Field(default_factory=list)

    @field_validator("lint_commands", "test_commands")
    @classmethod
    def valid_commands(cls, value: list[list[str]]) -> list[list[str]]:
        """Reject shell strings and empty commands."""
        if any(not cmd or any(not part for part in cmd) for cmd in value):
            raise ValueError("commands must be non-empty argument lists")
        return value


def load_settings(path: Path | None = None) -> Settings:
    """Load YAML and supported environment overrides."""
    data: dict[str, Any] = {}
    if path:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise ValueError("configuration root must be a mapping")
        data.update(loaded)
    if value := os.getenv("GIT_AI_AGENT_DEFAULT_REPOSITORY"):
        data["default_repository"] = value
    if value := os.getenv("GIT_AI_AGENT_AI_PROVIDER"):
        data["ai_provider"] = value
    if value := os.getenv("GIT_AI_AGENT_PUSH_ENABLED"):
        data["push_enabled"] = value.lower() == "true"
    return Settings.model_validate(data)
