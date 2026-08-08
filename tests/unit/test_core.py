"""Unit tests for core rules."""

from pathlib import Path

import pytest

from git_ai_agent.application.workflow import (
    ApprovalError,
    CommitWorkflow,
    SessionStore,
    suggest_commit,
)
from git_ai_agent.config import Settings
from git_ai_agent.domain.models import FileChange, ReviewReport
from git_ai_agent.engines.review_engine import LocalReviewer, render_markdown
from git_ai_agent.engines.security_engine import SecretScanner
from git_ai_agent.infrastructure.git_repository import GitRepository


def test_config_rejects_empty_command() -> None:
    with pytest.raises(ValueError):
        Settings(lint_commands=[[]])


def test_secret_is_blocking_and_redacted() -> None:
    findings = SecretScanner().scan('+api_key = "abcdefghijk"')
    assert findings[0].blocking and "abcdefghijk" not in findings[0].message


def test_suggest_conventional_commit() -> None:
    report = ReviewReport(
        repository="x",
        branch="main",
        fingerprint="f",
        files=[FileChange(path="docs/guide.md", status="M")],
    )
    assert suggest_commit(report).startswith("docs(")
    assert "Git review report" in render_markdown(report)


def test_warning_does_not_block(git_repo: Path) -> None:
    (git_repo / "app.py").write_text("value = 2  # TODO improve\n", encoding="utf-8")
    report = LocalReviewer(Settings()).review(GitRepository(git_repo))
    assert report.findings and not report.blocked


def test_prepare_blocks_secret(git_repo: Path, tmp_path: Path) -> None:
    (git_repo / "app.py").write_text('token = "abcdefghijk"\n', encoding="utf-8")
    settings = Settings()
    repo = GitRepository(git_repo)
    workflow = CommitWorkflow(
        settings, LocalReviewer(settings), SessionStore(tmp_path / "sessions")
    )
    with pytest.raises(ApprovalError, match="blocking"):
        workflow.prepare(repo)
