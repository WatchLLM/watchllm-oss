"""Unit tests for the core data model."""

import unittest

from watchllm_kernel.models import (
    Decision,
    KernelResult,
    Rule,
    RuleDecision,
    RuleResult,
    Severity,
    SourceLocation,
    Violation,
)


class TestModels(unittest.TestCase):
    def test_decision_enum_values(self):
        self.assertEqual(Decision.ALLOW.value, "ALLOW")
        self.assertEqual(Decision.BLOCK.value, "BLOCK")

    def test_rule_decision_enum_values(self):
        self.assertEqual(RuleDecision.PASS.value, "PASS")
        self.assertEqual(RuleDecision.FAIL.value, "FAIL")
        self.assertEqual(RuleDecision.INCONCLUSIVE.value, "INCONCLUSIVE")

    def test_severity_enum_values(self):
        self.assertEqual(Severity.CRITICAL.value, "CRITICAL")
        self.assertEqual(Severity.HIGH.value, "HIGH")
        self.assertEqual(Severity.MEDIUM.value, "MEDIUM")
        self.assertEqual(Severity.LOW.value, "LOW")
        self.assertEqual(Severity.INFO.value, "INFO")

    def test_source_location_defaults(self):
        loc = SourceLocation(line=10, column=5)
        self.assertEqual(loc.line, 10)
        self.assertEqual(loc.column, 5)
        self.assertIsNone(loc.end_line)
        self.assertIsNone(loc.end_column)

    def test_source_location_full(self):
        loc = SourceLocation(line=1, column=2, end_line=3, end_column=4)
        self.assertEqual(loc.end_line, 3)
        self.assertEqual(loc.end_column, 4)

    def test_violation_creation(self):
        v = Violation(
            rule_id="SECRET-001",
            message="Hardcoded secret found",
            location=SourceLocation(line=5, column=10),
            severity=Severity.CRITICAL,
            evidence='const key = "sk_live_123"',
        )
        self.assertEqual(v.rule_id, "SECRET-001")
        self.assertEqual(v.message, "Hardcoded secret found")
        self.assertEqual(v.location.line, 5)
        self.assertEqual(v.severity, Severity.CRITICAL)
        self.assertEqual(v.evidence, 'const key = "sk_live_123"')

    def test_violation_defaults(self):
        v = Violation(rule_id="R1", message="test")
        self.assertIsNone(v.location)
        self.assertEqual(v.severity, Severity.HIGH)
        self.assertIsNone(v.evidence)

    def test_rule_result_pass(self):
        rr = RuleResult(rule_id="R1", status=RuleDecision.PASS)
        self.assertEqual(rr.rule_id, "R1")
        self.assertEqual(rr.status, RuleDecision.PASS)
        self.assertEqual(rr.violations, [])

    def test_rule_result_fail_with_violations(self):
        v = Violation(rule_id="R1", message="fail")
        rr = RuleResult(rule_id="R1", status=RuleDecision.FAIL, violations=[v])
        self.assertEqual(rr.status, RuleDecision.FAIL)
        self.assertEqual(len(rr.violations), 1)
        self.assertEqual(rr.violations[0].message, "fail")

    def test_kernel_result_allow(self):
        kr = KernelResult(decision=Decision.ALLOW)
        self.assertEqual(kr.decision, Decision.ALLOW)
        self.assertEqual(kr.rule_results, [])
        self.assertIsNone(kr.file_path)
        self.assertIsNone(kr.language)
        self.assertEqual(kr.mode, "enforce")

    def test_kernel_result_block(self):
        kr = KernelResult(
            decision=Decision.BLOCK,
            file_path="/tmp/test.js",
            language="javascript",
            mode="shadow",
        )
        self.assertEqual(kr.decision, Decision.BLOCK)
        self.assertEqual(kr.file_path, "/tmp/test.js")
        self.assertEqual(kr.language, "javascript")
        self.assertEqual(kr.mode, "shadow")

    def test_rule_abstract_evaluate_raises(self):
        class DummyRule(Rule):
            pass

        r = DummyRule(rule_id="R1", name="dummy")
        with self.assertRaises(NotImplementedError):
            r.evaluate("source")

    def test_rule_attributes(self):
        r = Rule(rule_id="R1", name="Test Rule", description="A test rule")
        self.assertEqual(r.rule_id, "R1")
        self.assertEqual(r.name, "Test Rule")
        self.assertEqual(r.description, "A test rule")


if __name__ == "__main__":
    unittest.main()
