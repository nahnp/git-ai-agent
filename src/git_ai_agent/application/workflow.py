"""Fail-safe commit preparation and execution workflow."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from git_ai_agent.config.settings import Settings
from git_ai_agent.domain.models import ApprovalSession, ReviewReport
from git_ai_agent.domain.ports import RepositoryPort, ReviewerPort


class ApprovalError(RuntimeError):
    """Approval session failed closed."""


class SessionStore:
    """Persist non-secret approval snapshots outside target repositories."""

    def __init__(self, directory: Path | None = None) -> None:
        configured = os.getenv("GIT_AI_AGENT_SESSION_DIR")
        self.directory = directory or (
            Path(configured) if configured else Path.home() / ".git-ai-agent" / "sessions"
        )

    def save(self, session: ApprovalSession) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / f"{session.session_id}.json").write_text(
            session.model_dump_json(indent=2), encoding="utf-8"
        )

    def load(self, session_id: str) -> ApprovalSession:
        if not session_id.isalnum():
            raise ApprovalError("invalid session id")
        path = self.directory / f"{session_id}.json"
        if not path.is_file():
            raise ApprovalError("approval session does not exist")
        return ApprovalSession.model_validate_json(path.read_text(encoding="utf-8"))

    def delete(self, session_id: str) -> None:
        (self.directory / f"{session_id}.json").unlink(missing_ok=True)


def suggest_commit(report: ReviewReport) -> str:
    """Create a deterministic Conventional Commit message."""
    paths = [item.path.lower() for item in report.files]
    kind = (
        "docs"
        if paths and all(p.endswith((".md", ".rst")) for p in paths)
        else "test"
        if paths and all("test" in p for p in paths)
        else "feat"
    )
    scope = next(
        (part for p in paths for part in Path(p).parts if part not in {"src", "tests", "docs"}),
        "project",
    )
    scope = Path(scope).stem.replace("_", "-")[:20] or "project"
    return f"{kind}({scope}): update {len(paths)} file{'s' if len(paths) != 1 else ''}"


class CommitWorkflow:
    """Orchestrate analysis and state-changing Git operations."""

    def __init__(self, settings: Settings, reviewer: ReviewerPort, store: SessionStore) -> None:
        self.settings = settings
        self.reviewer = reviewer
        self.store = store

    def prepare(self, repo: RepositoryPort, message: str | None = None) -> ApprovalSession:
        """Analyze changes and store an immutable approval snapshot."""
        report = self.reviewer.review(repo)
        if not report.files:
            raise ApprovalError("repository has no changes")
        if report.blocked:
            raise ApprovalError("review contains blocking findings or failed checks")
        approved = message or suggest_commit(report)
        now = datetime.now(UTC)
        sid = uuid4().hex
        session = ApprovalSession(
            session_id=sid,
            repository=repo.root,
            branch=repo.branch(),
            fingerprint=repo.fingerprint(),
            message=approved,
            files=[x.path for x in report.files],
            created_at=now,
            expires_at=now + timedelta(seconds=self.settings.approval_ttl_seconds),
            planned_commands=[
                ["git", "add", "--", *[x.path for x in report.files]],
                ["git", "commit", "-m", approved],
            ],
            report=report,
        )
        self.store.save(session)
        return session

    def execute(self, repo: RepositoryPort, session_id: str, message: str | None = None) -> str:
        """Revalidate and execute an explicitly approved commit."""
        session = self.store.load(session_id)
        if datetime.now(UTC) > session.expires_at:
            raise ApprovalError("approval session expired")
        if Path(repo.root).resolve() != Path(session.repository).resolve():
            raise ApprovalError("repository changed")
        if repo.branch() != session.branch:
            raise ApprovalError("branch changed")
        if repo.fingerprint() != session.fingerprint:
            raise ApprovalError("diff changed after preparation")
        if message is not None and message != session.message:
            raise ApprovalError("approved message changed")
        report = self.reviewer.review(repo)
        if report.blocked:
            raise ApprovalError("fresh review blocks commit")
        repo.add(session.files)
        result = repo.commit(session.message)
        self.store.delete(session_id)
        return result
