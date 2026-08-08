"""Human-oriented command line interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from git_ai_agent.bootstrap import build
from git_ai_agent.config import load_settings
from git_ai_agent.engines.review_engine import render_markdown

app = typer.Typer(no_args_is_help=True, help="Review and approve Git changes safely.")
console = Console(stderr=True)


def _emit(value: object, json_output: bool) -> None:
    text = value.model_dump_json(indent=2) if hasattr(value, "model_dump_json") else str(value)
    if json_output:
        typer.echo(text)
    else:
        console.print(text)


@app.command()
def status(repo: Path = Path("."), json_output: bool = typer.Option(False, "--json")) -> None:
    """Show repository status without modifying it."""
    repository, _, _ = build(repo)
    _emit(repository.status(), json_output)


@app.command()
def diff(repo: Path = Path("."), json_output: bool = typer.Option(False, "--json")) -> None:
    """Show complete staged, unstaged, and textual untracked diff."""
    repository, _, _ = build(repo)
    _emit(repository.diff(), json_output)


@app.command()
def branch(repo: Path = Path(".")) -> None:
    """Show current branch."""
    repository, _, _ = build(repo)
    typer.echo(repository.branch())


@app.command()
def log(repo: Path = Path("."), limit: int = 10) -> None:
    """Show abbreviated history."""
    repository, _, _ = build(repo)
    typer.echo(repository.log(limit))


@app.command()
def review(
    repo: Path = Path("."),
    config: Path | None = None,
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Run read-only local review."""
    repository, _, workflow = build(repo, config)
    report = workflow.reviewer.review(repository)
    if json_output:
        _emit(report, True)
    else:
        console.print(render_markdown(report))


@app.command("prepare-commit")
def prepare_commit(
    repo: Path = Path("."), message: str | None = None, config: Path | None = None
) -> None:
    """Prepare an immutable approval session without modifying Git state."""
    repository, _, workflow = build(repo, config)
    _emit(workflow.prepare(repository, message), True)


@app.command("commit")
def commit(
    session_id: str,
    approve: bool = typer.Option(False, "--approve"),
    repo: Path = Path("."),
    message: str | None = None,
    config: Path | None = None,
) -> None:
    """Execute a prepared commit after explicit approval and revalidation."""
    if not approve:
        raise typer.BadParameter("--approve is required")
    repository, _, workflow = build(repo, config)
    typer.echo(workflow.execute(repository, session_id, message))


@app.command("push")
def push(
    repo: Path = Path("."),
    approve: bool = typer.Option(False, "--approve"),
    config: Path | None = None,
) -> None:
    """Push separately after explicit confirmation."""
    if not approve:
        raise typer.BadParameter("--approve is required")
    repository, settings, _ = build(repo, config)
    if not settings.push_enabled:
        raise typer.BadParameter("push is disabled by configuration")
    typer.echo(repository.push())


@app.command("config-check")
def config_check(config: Path = Path("config/default.yaml")) -> None:
    """Validate and print effective configuration."""
    typer.echo(load_settings(config).model_dump_json(indent=2))
