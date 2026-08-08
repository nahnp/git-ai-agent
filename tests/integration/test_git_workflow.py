"""Integration tests using real Git repositories."""

import subprocess
from pathlib import Path

import pytest

from git_ai_agent.application.workflow import ApprovalError, CommitWorkflow, SessionStore
from git_ai_agent.config import Settings
from git_ai_agent.engines.review_engine import LocalReviewer
from git_ai_agent.infrastructure.git_repository import GitRepository


def make_flow(tmp_path: Path, settings: Settings | None = None) -> CommitWorkflow:
    configured = settings or Settings()
    return CommitWorkflow(
        configured, LocalReviewer(configured), SessionStore(tmp_path / "sessions")
    )


def test_status_diff_branch_and_commit(git_repo: Path, tmp_path: Path) -> None:
    (git_repo / "app.py").write_text("value = 2\n", encoding="utf-8")
    repo = GitRepository(git_repo)
    assert repo.branch() == "main" and "app.py" in repo.status() and "+value = 2" in repo.diff()
    session = make_flow(tmp_path).prepare(repo, "fix(app): update value")
    result = make_flow(tmp_path).execute(repo, session.session_id)
    assert "fix(app): update value" in result and not repo.changed_files()


def test_changed_diff_invalidates_session(git_repo: Path, tmp_path: Path) -> None:
    (git_repo / "app.py").write_text("value = 2\n", encoding="utf-8")
    repo = GitRepository(git_repo)
    workflow = make_flow(tmp_path)
    session = workflow.prepare(repo)
    (git_repo / "app.py").write_text("value = 3\n", encoding="utf-8")
    with pytest.raises(ApprovalError, match="diff changed"):
        workflow.execute(repo, session.session_id)


def test_push_to_local_remote(git_repo: Path, tmp_path: Path) -> None:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=git_repo, check=True)
    subprocess.run(
        ["git", "push", "-u", "origin", "main"], cwd=git_repo, check=True, capture_output=True
    )
    assert isinstance(GitRepository(git_repo).push(), str)


def test_failed_test_blocks_prepare(git_repo: Path, tmp_path: Path) -> None:
    (git_repo / "app.py").write_text("value=2\n", encoding="utf-8")
    settings = Settings(test_commands=[["git", "rev-parse", "--verify", "missing"]])
    with pytest.raises(ApprovalError, match="blocking"):
        make_flow(tmp_path, settings).prepare(GitRepository(git_repo))
