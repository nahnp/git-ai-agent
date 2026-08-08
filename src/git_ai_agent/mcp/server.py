"""FastMCP stdio server with structured tool results."""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from git_ai_agent.bootstrap import build

mcp = FastMCP("git-ai-agent", log_level="ERROR")


@mcp.tool()
def git_status(repo: str = ".") -> dict[str, object]:
    """Read the repository status without changing it."""
    r, _, _ = build(Path(repo))
    return {"repository": r.root, "status": r.status()}


@mcp.tool()
def git_diff(repo: str = ".") -> dict[str, object]:
    """Read staged, unstaged, and textual untracked changes."""
    r, _, _ = build(Path(repo))
    return {"repository": r.root, "diff": r.diff(), "fingerprint": r.fingerprint()}


@mcp.tool()
def git_review(repo: str = ".") -> dict[str, object]:
    """Run the local deterministic review without sending code externally."""
    r, _, w = build(Path(repo))
    return w.reviewer.review(r).model_dump(mode="json")


@mcp.tool()
def prepare_commit(repo: str = ".", message: str | None = None) -> dict[str, object]:
    """Create an approval session without modifying the repository."""
    r, _, w = build(Path(repo))
    return w.prepare(r, message).model_dump(mode="json")


@mcp.tool()
def execute_commit(
    session_id: str, repo: str = ".", approved: bool = False, message: str | None = None
) -> dict[str, object]:
    """Commit only when approved and the prepared snapshot is unchanged."""
    if not approved:
        raise ValueError("explicit approved=true is required")
    r, _, w = build(Path(repo))
    return {"result": w.execute(r, session_id, message)}


@mcp.tool()
def execute_push(repo: str = ".", approved: bool = False) -> dict[str, object]:
    """Push separately; requires explicit approval and enabled configuration."""
    if not approved:
        raise ValueError("explicit approved=true is required")
    r, s, _ = build(Path(repo))
    if not s.push_enabled:
        raise ValueError("push is disabled by configuration")
    return {"result": r.push()}


@mcp.tool()
def git_log(repo: str = ".", limit: int = 10) -> dict[str, object]:
    """Return abbreviated commit history."""
    r, _, _ = build(Path(repo))
    return {"log": r.log(limit)}


@mcp.tool()
def git_branch(repo: str = ".") -> dict[str, object]:
    """Return current branch and configured remotes."""
    r, _, _ = build(Path(repo))
    return {"branch": r.branch(), "remote": r.remote()}


def main() -> None:
    """Run MCP over stdio; protocol output remains isolated from logs."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
