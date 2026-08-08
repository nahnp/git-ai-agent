"""Run configured commands without invoking a shell."""

import subprocess
from pathlib import Path

from git_ai_agent.domain.models import CheckResult


class CommandRunner:
    """Bounded lint and test execution."""

    def __init__(self, timeout: int) -> None:
        self.timeout = timeout

    def run_all(
        self, cwd: Path, lint: list[list[str]], tests: list[list[str]]
    ) -> list[CheckResult]:
        """Run configured commands, marking absent stages as skipped."""
        results = []
        for name, commands in (("lint", lint), ("tests", tests)):
            if not commands:
                results.append(CheckResult(name=name, status="skipped (config)"))
                continue
            for command in commands:
                try:
                    r = subprocess.run(
                        command,
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        shell=False,
                        check=False,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    results.append(
                        CheckResult(name=name, status="failed", output=type(exc).__name__)
                    )
                    continue
                results.append(
                    CheckResult(
                        name=name,
                        status="passed" if r.returncode == 0 else "failed",
                        exit_code=r.returncode,
                        output=(r.stdout + r.stderr)[-4000:],
                    )
                )
        return results
