"""Conservative regex scanner for secrets added by a diff."""

from __future__ import annotations

import re

from git_ai_agent.domain.models import Finding, Severity


class SecretScanner:
    """Find and redact common credential patterns in added lines."""

    _patterns = {
        "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "credential-url": re.compile(r"https?://[^\s:/]+:[^\s@/]+@"),
        "api-token": re.compile(
            r"(?i)(?:api[_-]?key|token|secret|password|passwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
        ),
        "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
        "aws-key": re.compile(r"AKIA[0-9A-Z]{16}"),
    }

    def scan(self, diff: str) -> list[Finding]:
        """Return blocking findings without echoing matched values."""
        findings = []
        current = None
        added_line = 0
        for raw in diff.splitlines():
            if raw.startswith("+++ b/"):
                current = raw[6:]
            if raw.startswith("+") and not raw.startswith("+++"):
                added_line += 1
                for rule, pattern in self._patterns.items():
                    if pattern.search(raw[1:]):
                        findings.append(
                            Finding(
                                rule_id=f"secret.{rule}",
                                severity=Severity.CRITICAL,
                                message="Potential secret detected; value redacted",
                                file=current,
                                line=added_line,
                                blocking=True,
                            )
                        )
        return findings
