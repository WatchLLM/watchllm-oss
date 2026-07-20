"""Unit tests for the auth-flow rule."""

from pathlib import Path
import unittest

from watchllm_kernel.models import RuleDecision
from watchllm_kernel.rules.auth_flow import (
    AUTH_FLOW_INCONCLUSIVE_POLICY,
    AuthFlowRule,
    extract_call_events,
    is_auth_guard_call,
    is_protected_operation_call,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "rules" / "auth_flow"


def read_fixture(outcome: str, name: str) -> str:
    return (FIXTURE_DIR / outcome / name).read_text(encoding="utf-8")


class TestAuthFlowRule(unittest.TestCase):
    def test_protected_operation_helper(self):
        self.assertTrue(is_protected_operation_call("db.user.update"))
        self.assertTrue(is_protected_operation_call("db.query"))
        self.assertFalse(is_protected_operation_call("auth.verify"))
        self.assertFalse(is_protected_operation_call("logger.info"))

    def test_auth_guard_helper(self):
        self.assertTrue(is_auth_guard_call("auth.verify"))
        self.assertTrue(is_auth_guard_call("requireAuth"))
        self.assertFalse(is_auth_guard_call("db.user.update"))

    def test_extract_call_events_from_fail_fixture(self):
        source = read_fixture("fail", "mutation_before_auth.ts")
        events = extract_call_events(source, file_path="handler.ts")
        protected = [e for e in events if e.kind == "protected_operation"]
        guards = [e for e in events if e.kind == "auth_guard"]
        self.assertTrue(len(protected) >= 1, "Expected at least one protected operation")
        self.assertTrue(len(guards) >= 1, "Expected at least one auth guard")
        # Protected operation must appear before auth guard
        self.assertLess(
            protected[0].location.line,
            guards[0].location.line,
            "Protected operation should appear before auth guard",
        )

    def test_mutation_before_auth_fails(self):
        source = read_fixture("fail", "mutation_before_auth.ts")
        rule = AuthFlowRule()
        result = rule.evaluate(source, file_path="handler.ts")
        self.assertEqual(result.status, RuleDecision.FAIL)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].evidence, "db.user.update")

    def test_auth_before_mutation_passes(self):
        source = read_fixture("pass", "auth_before_mutation.ts")
        rule = AuthFlowRule()
        result = rule.evaluate(source, file_path="handler.ts")
        self.assertEqual(result.status, RuleDecision.PASS)
        self.assertEqual(result.violations, [])

    def test_ambiguous_auth_guard_is_inconclusive(self):
        source = (
            "export async function handler(req, db, auth) {\n"
            "  if (req.userId) {\n"
            "    await auth.verify(req);\n"
            "  }\n"
            "  await db.user.update({ id: req.userId });\n"
            "}\n"
        )
        rule = AuthFlowRule()
        result = rule.evaluate(source, file_path="handler.ts")
        self.assertEqual(result.status, RuleDecision.INCONCLUSIVE)
        self.assertEqual(result.violations, [])

    def test_inconclusive_policy_is_documented(self):
        self.assertIn("INCONCLUSIVE", AUTH_FLOW_INCONCLUSIVE_POLICY)
        self.assertIn("ambiguous", AUTH_FLOW_INCONCLUSIVE_POLICY)

    def test_non_handler_source_passes(self):
        source = (
            "async function helper(db) {\n"
            "  await db.user.update({ id: \"u_1\" });\n"
            "}\n"
        )
        rule = AuthFlowRule()
        result = rule.evaluate(source, file_path="helper.ts")
        self.assertEqual(result.status, RuleDecision.PASS)


if __name__ == "__main__":
    unittest.main()
