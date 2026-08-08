"""Application composition root."""

from pathlib import Path

from git_ai_agent.application.workflow import CommitWorkflow, SessionStore
from git_ai_agent.config import Settings, load_settings
from git_ai_agent.engines.review_engine import LocalReviewer
from git_ai_agent.infrastructure.git_repository import GitRepository


def build(repo: Path, config: Path | None = None) -> tuple[GitRepository, Settings, CommitWorkflow]:
    """Build adapters and application workflow."""
    settings = load_settings(config)
    repository = GitRepository(
        repo, settings.command_timeout_seconds, settings.allowed_repository_roots
    )
    reviewer = LocalReviewer(settings)
    return repository, settings, CommitWorkflow(settings, reviewer, SessionStore())
