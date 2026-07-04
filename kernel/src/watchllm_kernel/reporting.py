"""Local violation reporting and JSONL blocked-event logging.

Provides structured violation report dictionaries, human-readable CLI
output, and append-only JSONL logging for blocked evaluations.

This module is intentionally separate from enforcement: it records
deterministic rule outcomes after evaluation and does not participate
in allow/block decisions.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from watchllm_kernel.models import KernelResult, SourceLocation, Violation

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPORT_SCHEMA_VERSION = "watchllm.kernel.violation_report.v1"
DEFAULT_PARSE_STATUS = "not_recorded"
LOG_PATH_ENV = "WATCHLLM_LOG_PATH"
DEFAULT_LOG_PATH = Path(".watchllm") / "logs" / "violations.jsonl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def location_to_dict(
    location: SourceLocation | None,
) -> dict[str, int | None] | None:
    """Convert a SourceLocation to a plain dict, or None."""
    if location is None:
        return None
    return {
        "line": location.line,
        "column": location.column,
        "end_line": location.end_line,
        "end_column": location.end_column,
    }


def violation_to_dict(violation: Violation) -> dict[str, Any]:
    """Convert a Violation to a JSON-serialisable dict."""
    return {
        "rule_id": violation.rule_id,
        "message": violation.message,
        "severity": violation.severity.value,
        "evidence": violation.evidence,
        "location": location_to_dict(violation.location),
    }


# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------


def build_violation_report(
    result: KernelResult,
    *,
    timestamp: str | None = None,
    parse_status: str = DEFAULT_PARSE_STATUS,
) -> dict[str, Any]:
    """Build a structured violation report dictionary from a KernelResult.

    The report preserves rule result order and per-rule violation order.
    It does not recompute decisions.
    """
    if timestamp is None:
        timestamp = utc_now_iso()

    violations: list[dict[str, Any]] = []
    for rule_result in result.rule_results:
        for violation in rule_result.violations:
            violations.append(violation_to_dict(violation))

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "timestamp": timestamp,
        "decision": result.decision.value,
        "file_path": result.file_path,
        "language": result.language,
        "mode": result.mode,
        "parse_status": parse_status,
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# Log path resolution
# ---------------------------------------------------------------------------


def resolve_log_path(log_path: str | Path | None = None) -> Path:
    """Return the resolved log file path.

    Resolution order:
    1. Explicit *log_path* argument.
    2. ``WATCHLLM_LOG_PATH`` environment variable.
    3. Default ``.watchllm/logs/violations.jsonl`` relative to CWD.
    """
    if log_path is not None:
        return Path(log_path)
    env_path = os.environ.get(LOG_PATH_ENV)
    if env_path:
        return Path(env_path)
    return DEFAULT_LOG_PATH


# ---------------------------------------------------------------------------
# Log writing
# ---------------------------------------------------------------------------


def write_block_log(
    result: KernelResult,
    *,
    log_path: str | Path | None = None,
    parse_status: str = DEFAULT_PARSE_STATUS,
    timestamp: str | None = None,
) -> Path | None:
    """Write a JSONL entry for a blocked evaluation.

    Returns the resolved log path if a log entry was written, or ``None``
    when the decision is not ``BLOCK``.
    """
    from watchllm_kernel.models import Decision

    if result.decision != Decision.BLOCK:
        return None

    resolved = resolve_log_path(log_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)

    report = build_violation_report(
        result, timestamp=timestamp, parse_status=parse_status
    )
    line = json.dumps(report, sort_keys=True)

    with resolved.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    return resolved


# ---------------------------------------------------------------------------
# Human-readable formatting
# ---------------------------------------------------------------------------


def format_human_report(result: KernelResult) -> str:
    """Return a stable human-readable violation report string."""
    lines: list[str] = []

    lines.append(f"Decision: {result.decision.value}")
    lines.append(f"File: {result.file_path or '<stdin>'}")
    lines.append(f"Language: {result.language or '<unknown>'}")
    lines.append(f"Mode: {result.mode}")

    violations: list[Violation] = []
    for rule_result in result.rule_results:
        violations.extend(rule_result.violations)

    if not violations:
        lines.append("Violations: none")
    else:
        for v in violations:
            loc = "at <unknown location>"
            if v.location:
                loc = f"at line {v.location.line}, col {v.location.column}"
            lines.append(f"  - {v.message} {loc}")

    return "\n".join(lines)
