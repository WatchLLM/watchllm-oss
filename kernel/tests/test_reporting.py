"""Unit tests for local violation reporting and JSONL logging."""

import json
import tempfile
import unittest
from pathlib import Path

from watchllm_kernel.models import (
    Decision,
    KernelResult,
    RuleDecision,
    RuleResult,
    Severity,
    SourceLocation,
    Violation,
)
from watchllm_kernel.reporting import (
    REPORT_SCHEMA_VERSION,
    build_violation_report,
    format_human_report,
    write_block_log,
)


def _make_blocked_result() -> KernelResult:
    """Return a synthetic blocked KernelResult with one violation."""
    violation = Violation(
        rule_id="RULE_ID",
        message="Blocked unsafe operation",
        severity=Severity.HIGH,
        evidence="dangerous_call()",
        location=SourceLocation(line=1, column=2, end_line=1, end_column=20),
    )
    rule_result = RuleResult(
        rule_id="RULE_ID",
        decision=RuleDecision.FAIL,
        violations=[violation],
    )
    return KernelResult(
        decision=Decision.BLOCK,
        rule_results=[rule_result],
        file_path="/tmp/test.js",
        language="javascript",
        mode="enforce",
    )


class TestReporting(unittest.TestCase):
    # ------------------------------------------------------------------
    # build_violation_report
    # ------------------------------------------------------------------

    def test_build_violation_report_contains_required_fields(self):
        result = _make_blocked_result()
        timestamp = "2026-06-02T00:00:00+00:00"
        report = build_violation_report(result, timestamp=timestamp)

        self.assertEqual(report["schema_version"], REPORT_SCHEMA_VERSION)
        self.assertEqual(report["timestamp"], timestamp)
        self.assertEqual(report["decision"], "BLOCK")
        self.assertEqual(report["file_path"], "/tmp/test.js")
        self.assertEqual(report["language"], "javascript")
        self.assertEqual(report["mode"], "enforce")
        self.assertEqual(report["parse_status"], "not_recorded")

        violations = report["violations"]
        self.assertIsInstance(violations, list)
        self.assertEqual(len(violations), 1)

        v = violations[0]
        self.assertEqual(v["rule_id"], "RULE_ID")
        self.assertEqual(v["message"], "Blocked unsafe operation")
        self.assertEqual(v["severity"], "HIGH")
        self.assertEqual(v["evidence"], "dangerous_call()")
        self.assertEqual(v["location"]["line"], 1)
        self.assertEqual(v["location"]["column"], 2)

    # ------------------------------------------------------------------
    # write_block_log
    # ------------------------------------------------------------------

    def test_write_block_log_writes_jsonl(self):
        result = _make_blocked_result()
        timestamp = "2026-06-02T00:00:00+00:00"

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "violations.jsonl"
            written = write_block_log(
                result, log_path=log_path, timestamp=timestamp
            )
            self.assertEqual(written, log_path)
            self.assertTrue(log_path.exists())

            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)

            payload = json.loads(lines[0])
            self.assertEqual(payload["schema_version"], REPORT_SCHEMA_VERSION)
            self.assertEqual(payload["decision"], "BLOCK")

    def test_allow_result_does_not_log(self):
        result = KernelResult(
            decision=Decision.ALLOW,
            rule_results=[],
            file_path="/tmp/test.js",
            language="javascript",
            mode="enforce",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "violations.jsonl"
            written = write_block_log(result, log_path=log_path)
            self.assertIsNone(written)
            self.assertFalse(log_path.exists())

    # ------------------------------------------------------------------
    # format_human_report
    # ------------------------------------------------------------------

    def test_format_human_report_is_clear(self):
        result = _make_blocked_result()
        text = format_human_report(result)

        self.assertIn("Decision: BLOCK", text)
        self.assertIn("File: /tmp/test.js", text)
        self.assertIn("Language: javascript", text)
        self.assertIn("Mode: enforce", text)
        self.assertIn("Blocked unsafe operation", text)
        self.assertIn("at line 1, col 2", text)


if __name__ == "__main__":
    unittest.main()
