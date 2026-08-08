"""Validated domain models without infrastructure dependencies."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Severity(StrEnum):
    """Review finding severity."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class FileChange(BaseModel):
    """A file changed in the repository."""

    model_config = ConfigDict(frozen=True)
    path: str
    status: str
    language: str = "unknown"


class DiffStats(BaseModel):
    """Summary of a Git diff."""

    model_config = ConfigDict(frozen=True)
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


class Finding(BaseModel):
    """A redacted, actionable review finding."""

    model_config = ConfigDict(frozen=True)
    rule_id: str
    severity: Severity
    message: str
    file: str | None = None
    line: int | None = None
    blocking: bool = False


class CheckResult(BaseModel):
    """Result of a configured quality command."""

    model_config = ConfigDict(frozen=True)
    name: str
    status: str
    exit_code: int | None = None
    output: str = ""


class ReviewReport(BaseModel):
    """Complete deterministic repository review."""

    model_config = ConfigDict(frozen=True)
    repository: str
    branch: str
    fingerprint: str
    files: list[FileChange] = Field(default_factory=list)
    stats: DiffStats = Field(default_factory=DiffStats)
    findings: list[Finding] = Field(default_factory=list)
    checks: list[CheckResult] = Field(default_factory=list)
    ai_review: str = "disabled (local deterministic review)"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def blocked(self) -> bool:
        """Return whether any result prevents commit."""
        return any(x.blocking for x in self.findings) or any(
            x.status == "failed" for x in self.checks
        )


class ApprovalSession(BaseModel):
    """Immutable snapshot used to verify an approved commit."""

    model_config = ConfigDict(frozen=True)
    session_id: str
    repository: str
    branch: str
    fingerprint: str
    message: str
    files: list[str]
    created_at: datetime
    expires_at: datetime
    planned_commands: list[list[str]]
    report: ReviewReport
