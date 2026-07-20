"""Unit tests for the decision engine."""

import unittest

from watchllm_kernel.engine import (
    ENFORCE_MODE,
    SHADOW_MODE,
    collect_violations,
    evaluate_source,
    has_blocking_failure,
    reduce_decision,
)
from watchllm_kernel.models import (
    Decision,
    Rule,
    RuleDecision,
    RuleResult,
    Severity,
    SourceLocation,
    Violation,
)


# ---------------------------------------------------------------------------
# Stub rules for testing
# ---------------------------------------------------------------------------


class PassingRule(Rule):
    def __init__(self):
        super().__init__(rule_id="PASSING_RULE", name="Passing rule")

    def evaluate(self, source: str, file_path: str | None = None, **kwargs) -> RuleResult:
        return RuleResult(rule_id=self.rule_id, status=RuleDecision.PASS)


class FailingRule(Rule):
    def __init__(self):
        super().__init__(rule_id="FAILING_RULE", name="Failing rule")

    def evaluate(self, source: str, file_path: str | None = None, **kwargs) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            status=RuleDecision.FAIL,
            violations=[
                Violation(
                    rule_id=self.rule_id,
                    message="sample failure",
                    location=SourceLocation(line=1, column=1),
                    severity=Severity.HIGH,
                    evidence="sample",
                )
            ],
        )


class InconclusiveRule(Rule):
    def __init__(self):
        super().__init__(rule_id="INCONCLUSIVE_RULE", name="Inconclusive rule")

    def evaluate(self, source: str, file_path: str | None = None, **kwargs) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            status=RuleDecision.INCONCLUSIVE,
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEngine(unittest.TestCase):
    def test_multiple_rules_run_on_one_source(self):
        result = evaluate_source(
            "const x = 1;",
            rules=[PassingRule(), FailingRule()],
        )
        self.assertEqual(len(result.rule_results), 2)
        self.assertEqual(result.rule_results[0].status, RuleDecision.PASS)
        self.assertEqual(result.rule_results[1].status, RuleDecision.FAIL)

    def test_enforce_blocks_if_any_rule_fails(self):
        result = evaluate_source(
            "const x = 1;",
            rules=[PassingRule(), FailingRule()],
            mode=ENFORCE_MODE,
        )
        self.assertEqual(result.decision, Decision.BLOCK)

    def test_enforce_allows_when_all_rules_pass(self):
        result = evaluate_source(
            "const x = 1;",
            rules=[PassingRule(), PassingRule()],
            mode=ENFORCE_MODE,
        )
        self.assertEqual(result.decision, Decision.ALLOW)

    def test_shadow_allows_even_when_rule_fails(self):
        result = evaluate_source(
            "const x = 1;",
            rules=[FailingRule()],
            mode=SHADOW_MODE,
        )
        self.assertEqual(result.decision, Decision.ALLOW)
        self.assertTrue(
            any(rr.status == RuleDecision.FAIL for rr in result.rule_results)
        )

    def test_collect_violations_preserves_order(self):
        rr1 = RuleResult(
            rule_id="R1",
            status=RuleDecision.FAIL,
            violations=[
                Violation(rule_id="R1", message="first"),
                Violation(rule_id="R1", message="second"),
            ],
        )
        rr2 = RuleResult(
            rule_id="R2",
            status=RuleDecision.FAIL,
            violations=[Violation(rule_id="R2", message="third")],
        )
        violations = collect_violations([rr1, rr2])
        self.assertEqual(len(violations), 3)
        self.assertEqual(violations[0].message, "first")
        self.assertEqual(violations[1].message, "second")
        self.assertEqual(violations[2].message, "third")

    def test_inconclusive_does_not_block_for_task_10(self):
        rr = [InconclusiveRule().evaluate("source")]
        self.assertFalse(has_blocking_failure(rr))
        self.assertEqual(reduce_decision(rr, mode=ENFORCE_MODE), Decision.ALLOW)

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            evaluate_source("x", rules=[PassingRule()], mode="invalid")

    def test_kernel_result_contains_file_language_and_mode(self):
        result = evaluate_source(
            "const x = 1;",
            file_path="example.ts",
            language="typescript",
            rules=[PassingRule()],
            mode=ENFORCE_MODE,
        )
        self.assertEqual(result.file_path, "example.ts")
        self.assertEqual(result.language, "typescript")
        self.assertEqual(result.mode, ENFORCE_MODE)


if __name__ == "__main__":
    unittest.main()
