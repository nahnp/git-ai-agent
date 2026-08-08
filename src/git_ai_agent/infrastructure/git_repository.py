"""Safe subprocess-backed Git repository adapter."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    """Actionable Git operation failure."""


class GitRepository:
    """Operate on one validated local Git repository."""

    def __init__(
        self, path: Path, timeout: int = 120, allowed_roots: list[Path] | None = None
    ) -> None:
        candidate = path.expanduser().resolve(strict=True)
        if allowed_roots and not any(
            candidate.is_relative_to(root.expanduser().resolve()) for root in allowed_roots
        ):
            raise GitError("repository is outside allowed roots")
        self._timeout = timeout
        self._root = self._run_at(candidate, ["rev-parse", "--show-toplevel"]).strip()
        root = Path(self._root).resolve(strict=True)
        if root != candidate and not candidate.is_relative_to(root):
            raise GitError("invalid repository path")
        self._path = root

    @property
    def root(self) -> str:
        return str(self._path)

    def _run_at(self, cwd: Path, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self._timeout,
                check=False,
                shell=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitError(f"git command failed: {type(exc).__name__}") from exc
        if result.returncode:
            raise GitError((result.stderr or result.stdout).strip()[:2000])
        return result.stdout[:2_000_000]

    def _run(self, args: list[str]) -> str:
        return self._run_at(self._path, args)

    def branch(self) -> str:
        return self._run(["branch", "--show-current"]).strip()

    def remote(self) -> str:
        return self._run(["remote", "-v"])

    def log(self, limit: int = 10) -> str:
        return self._run(["log", f"-{max(1, min(limit, 100))}", "--oneline"])

    def status(self) -> str:
        return self._run(["status", "--short", "--branch"])

    def diff(self) -> str:
        unstaged = self._run(["diff", "--no-ext-diff", "--binary"])
        staged = self._run(["diff", "--cached", "--no-ext-diff", "--binary"])
        untracked = []
        for _, name in self.changed_files():
            path = self._path / name
            if path.is_file() and "??" in self._status_for(name):
                try:
                    untracked.append(
                        f"diff --git a/{name} b/{name}\n"
                        f"new file mode 100644\n--- /dev/null\n+++ b/{name}\n"
                        + "".join(
                            f"+{line}"
                            for line in path.read_text(
                                encoding="utf-8", errors="replace"
                            ).splitlines(keepends=True)
                        )
                    )
                except OSError:
                    continue
        return unstaged + staged + "".join(untracked)

    def _status_for(self, name: str) -> str:
        for status, path in self.changed_files():
            if path == name:
                return status
        return ""

    def fingerprint(self) -> str:
        return hashlib.sha256(self.diff().encode()).hexdigest()

    def changed_files(self) -> list[tuple[str, str]]:
        output = self._run(["status", "--porcelain=v1", "-z"])
        entries = [x for x in output.split("\0") if x]
        result = []
        index = 0
        while index < len(entries):
            entry = entries[index]
            status = entry[:2]
            name = entry[3:]
            if status.startswith(("R", "C")) and index + 1 < len(entries):
                index += 1
                name = entries[index]
            result.append((status, name))
            index += 1
        return result

    def add(self, files: list[str]) -> None:
        if not files:
            raise GitError("no files selected")
        known = {name for _, name in self.changed_files()}
        if not set(files) <= known:
            raise GitError("selected files are not in the analyzed change set")
        self._run(["add", "--", *files])

    def commit(self, message: str) -> str:
        return self._run(["commit", "-m", message]).strip()

    def push(self) -> str:
        return self._run(["push"]).strip()
