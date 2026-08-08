"""Local deterministic review and report construction."""

from __future__ import annotations

import re
from pathlib import Path

from git_ai_agent.config.settings import Settings
from git_ai_agent.domain.models import (
    DiffStats,
    FileChange,
    Finding,
    ReviewReport,
    Severity,
)
from git_ai_agent.domain.ports import RepositoryPort
from git_ai_agent.engines.security_engine import SecretScanner
from git_ai_agent.engines.testing_engine.runner import CommandRunner

_LANG = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".md": "Markdown",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
}


class LocalReviewer:
    """Review a diff locally without sending source code anywhere."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def review(self, repository: RepositoryPort) -> ReviewReport:
        """Build a structured deterministic review."""
        diff = repository.diff()
        if len(diff.encode()) > self.settings.max_diff_bytes:
            raise ValueError("diff exceeds configured maximum size")
        files = [
            FileChange(path=p, status=s, language=_LANG.get(Path(p).suffix.lower(), "unknown"))
            for s, p in repository.changed_files()
        ]
        findings = SecretScanner().scan(diff)
        current = None
        for line_no, line in enumerate(diff.splitlines(), 1):
            if line.startswith("+++ b/"):
                current = line[6:]
            if line.startswith("+") and not line.startswith("+++"):
                text = line[1:]
                if re.search(r"\b(?:TODO|FIXME)\b", text):
                    findings.append(
                        Finding(
                            rule_id="quality.marker",
                            severity=Severity.WARNING,
                            message="TODO/FIXME added",
                            file=current,
                            line=line_no,
                        )
                    )
                if current and current.endswith(".py") and re.search(r"\bprint\s*\(", text):
                    findings.append(
                        Finding(
                            rule_id="quality.print",
                            severity=Severity.WARNING,
                            message="print() added to Python production code",
                            file=current,
                            line=line_no,
                        )
                    )
        checks = CommandRunner(self.settings.command_timeout_seconds).run_all(
            Path(repository.root), self.settings.lint_commands, self.settings.test_commands
        )
        return ReviewReport(
            repository=repository.root,
            branch=repository.branch(),
            fingerprint=repository.fingerprint(),
            files=files,
            stats=DiffStats(
                files_changed=len(files),
                insertions=sum(
                    1 for x in diff.splitlines() if x.startswith("+") and not x.startswith("+++")
                ),
                deletions=sum(
                    1 for x in diff.splitlines() if x.startswith("-") and not x.startswith("---")
                ),
            ),
            findings=findings,
            checks=checks,
        )


def render_markdown(report: ReviewReport) -> str:
    """Render a review report as portable Markdown."""
    outcome = "BLOCKED" if report.blocked else "APPROVED"
    lines = [
        "# Git review report",
        "",
        f"- Outcome: **{outcome}**",
        f"- Repository: `{report.repository}`",
        f"- Branch: `{report.branch}`",
        f"- Fingerprint: `{report.fingerprint}`",
        f"- Files: {report.stats.files_changed}",
        f"- Diff: +{report.stats.insertions} / -{report.stats.deletions}",
        f"- AI review: {report.ai_review}",
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        lines.extend(
            f"- [{item.severity.value}] `{item.rule_id}` — {item.message}"
            for item in report.findings
        )
    else:
        lines.append("No findings.")
    lines.extend(["", "## Checks", ""])
    lines.extend(f"- `{item.name}`: {item.status}" for item in report.checks)
    return "\n".join(lines) + "\n"
