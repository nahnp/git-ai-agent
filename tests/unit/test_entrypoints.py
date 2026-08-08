"""Contract tests for thin CLI and MCP entrypoints."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from git_ai_agent.cli.app import app
from git_ai_agent.mcp import server


def test_cli_read_commands(git_repo: Path) -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["status", "--repo", str(git_repo)]).exit_code == 0
    assert runner.invoke(app, ["branch", "--repo", str(git_repo)]).stdout.strip() == "main"
    assert runner.invoke(app, ["log", "--repo", str(git_repo)]).exit_code == 0
    assert runner.invoke(app, ["diff", "--repo", str(git_repo)]).exit_code == 0


def test_cli_review_prepare_and_required_approval(
    git_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_AI_AGENT_SESSION_DIR", str(tmp_path / "sessions"))
    (git_repo / "app.py").write_text("value = 2\n", encoding="utf-8")
    runner = CliRunner()
    assert runner.invoke(app, ["review", "--repo", str(git_repo), "--json"]).exit_code == 0
    prepared = runner.invoke(app, ["prepare-commit", "--repo", str(git_repo)])
    assert prepared.exit_code == 0 and "session_id" in prepared.stdout
    assert runner.invoke(app, ["commit", "fake", "--repo", str(git_repo)]).exit_code != 0
    assert runner.invoke(app, ["push", "--repo", str(git_repo)]).exit_code != 0


def test_cli_config_check(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("push_enabled: false\n", encoding="utf-8")
    result = CliRunner().invoke(app, ["config-check", "--config", str(config)])
    assert result.exit_code == 0 and '"push_enabled": false' in result.stdout


def test_mcp_read_tools(git_repo: Path) -> None:
    repo = str(git_repo)
    assert server.git_status(repo)["repository"] == repo
    assert server.git_branch(repo)["branch"] == "main"
    assert "feat: baseline" in str(server.git_log(repo))
    assert "fingerprint" in server.git_diff(repo)


def test_mcp_review_prepare_and_commit(
    git_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_AI_AGENT_SESSION_DIR", str(tmp_path / "sessions"))
    (git_repo / "app.py").write_text("value = 4\n", encoding="utf-8")
    repo = str(git_repo)
    assert server.git_review(repo)["blocked"] is False
    session = server.prepare_commit(repo, "fix(app): update value")
    with pytest.raises(ValueError, match="approved=true"):
        server.execute_commit(str(session["session_id"]), repo, False)
    result = server.execute_commit(str(session["session_id"]), repo, True)
    assert "fix(app): update value" in str(result)


def test_mcp_push_approval_and_configured_block(git_repo: Path) -> None:
    with pytest.raises(ValueError, match="approved=true"):
        server.execute_push(str(git_repo), False)
