"""Isolated unit tests for the SecretLiteralRule.

Covers:
- Detection of every SECRET_PATTERNS prefix
- Safe retrieval context (process.env, os.getenv, config(), etc.)
- Comments exclusion
- Non-assignment contexts (template literals, console.log)
- Edge cases: empty string, numeric-looking tokens, false positives
"""

from __future__ import annotations

import unittest

from watchllm_kernel.models import RuleDecision
from watchllm_kernel.rules.secrets import SecretLiteralRule


class TestSecretsRule(unittest.TestCase):
    """Unit tests exercising SecretLiteralRule.evaluate() directly."""

    def setUp(self):
        self.rule = SecretLiteralRule()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _evaluate(self, source: str, language: str = "typescript") -> RuleDecision:
        result = self.rule.evaluate(source, file_path="test.ts" if language == "typescript" else "test.js")
        return result.status

    # ------------------------------------------------------------------
    # Detection by pattern
    # ------------------------------------------------------------------

    def test_detects_stripe_live_secret(self):
        status = self._evaluate('const secret = "sk_live_1234567890abcdef";')
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_stripe_pk_live(self):
        status = self._evaluate('const key = "pk_live_abcdef1234567890";')
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_github_pat(self):
        status = self._evaluate(
            'const token = "ghp_abcdefghijklmnopqrstuvwxyz1234567890";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_github_oauth(self):
        status = self._evaluate(
            'const oauth = "gho_abcdefghijklmnopqrstuvwxyz1234567890";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_aws_access_key(self):
        status = self._evaluate('const key = "AKIAIOSFODNN7EXAMPLE";')
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_google_api_key(self):
        # Construct the provider-shaped fixture at runtime so secret scanners do
        # not mistake a contiguous test literal for a leaked credential.
        provider_prefix = "AI" + "zaSy"
        synthetic_payload = "D4iE2xV45rCx6kT0Yb3dOQ1M_fLkPH8pI"
        status = self._evaluate(
            f'const key = "{provider_prefix}{synthetic_payload}";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_generic_sk_prefix(self):
        status = self._evaluate(
            'const key = "sk-abcdefghijklmnopqrstuvwxyz123456";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_object_property_assignment(self):
        status = self._evaluate(
            'const config = { stripeKey: "sk_live_abcdef12345678" };'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_in_function_argument(self):
        status = self._evaluate(
            'initializeClient("sk_live_abcdef12345678");'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_in_array(self):
        status = self._evaluate(
            'const secrets = ["sk_live_abcdef12345678"];'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_openai_sk_proj(self):
        status = self._evaluate(
            'const key = "sk-proj-abcdefghijklmnopqrstuvwxyz";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_anthropic_api_key(self):
        status = self._evaluate(
            'const key = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz";'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    # ------------------------------------------------------------------
    # Safe retrieval contexts (should PASS)
    # ------------------------------------------------------------------

    def test_allows_process_env_access(self):
        status = self._evaluate(
            'const secret = process.env.STRIPE_SECRET_KEY;'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_os_getenv(self):
        status = self._evaluate(
            'const secret = os.getenv("STRIPE_SECRET_KEY");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_config_call(self):
        status = self._evaluate(
            'const secret = config("stripe.secret_key");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_secret_call(self):
        status = self._evaluate(
            'const secret = secret("STRIPE_SECRET_KEY");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_vault_call(self):
        status = self._evaluate(
            'const secret = vault("stripe_key");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_env_call(self):
        status = self._evaluate(
            'const value = env("API_KEY");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_credential_call(self):
        status = self._evaluate(
            'const cred = credential("db_password");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_key_call(self):
        status = self._evaluate(
            'const k = key("my-key");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_token_call(self):
        status = self._evaluate(
            'const t = token("access_token");'
        )
        self.assertEqual(status, RuleDecision.PASS)

    # ------------------------------------------------------------------
    # Comments (should PASS)
    # ------------------------------------------------------------------

    def test_allows_secret_in_line_comment(self):
        status = self._evaluate(
            '// Example key: sk_live_abcdef12345678\nconst safe = true;'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_secret_in_block_comment(self):
        status = self._evaluate(
            '/* API key format: sk_live_abcdef12345678 */\nconst safe = true;'
        )
        self.assertEqual(status, RuleDecision.PASS)

    # ------------------------------------------------------------------
    # Non-assignment context (should PASS)
    # ------------------------------------------------------------------

    def test_allows_secret_in_comment_only(self):
        """The only safe place for a raw secret literal is a comment."""
        status = self._evaluate(
            '// sk_live_abcdef12345678\nconst safe = true;'
        )
        self.assertEqual(status, RuleDecision.PASS)

    def test_detects_secret_in_log_call(self):
        """Even console.log with a secret should be flagged — it's still in
        arguments context."""
        status = self._evaluate(
            'console.log("Debug: sk_live_abcdef12345678");'
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_allows_secret_in_template_literal(self):
        status = self._evaluate(
            'const msg = `Using key: sk_live_abcdef12345678`;'
        )
        self.assertEqual(status, RuleDecision.PASS)

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_allows_empty_string(self):
        status = self._evaluate('const secret = "";')
        self.assertEqual(status, RuleDecision.PASS)

    def test_detects_any_sk_prefixed_string(self):
        """The bare 'sk-' pattern acts as a catch-all for unknown sk- variants."""
        status = self._evaluate('const key = "sk-live_abc";')
        self.assertEqual(status, RuleDecision.FAIL)

    def test_allows_normal_variable_assignment(self):
        status = self._evaluate('const name = "hello world";')
        self.assertEqual(status, RuleDecision.PASS)

    def test_allows_numeric_looking_but_not_secret(self):
        status = self._evaluate('const count = "12345";')
        self.assertEqual(status, RuleDecision.PASS)

    def test_detects_assignment_to_property_in_javascript(self):
        """Assigning a hardcoded secret to process.env is still a direct assignment."""
        status = self._evaluate(
            'process.env.STRIPE_KEY = "sk_live_abcdef12345678";', language="javascript"
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_assigned_secret_in_javascript(self):
        status = self._evaluate(
            'const stripe = "sk_live_abcdef12345678";', language="javascript"
        )
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_pattern_as_substring(self):
        """Patterns are regex-based, so substring matches trigger. This is a
        known design decision — better to flag a potential false positive
        than miss a real secret."""
        status = self._evaluate('const action = "task_live_1234567890";')
        self.assertEqual(status, RuleDecision.FAIL)

    def test_detects_multiple_violations_in_single_source(self):
        source = """
        const stripe = "sk_live_abc1234567890";
        const github = "ghp_abcdefghijklmnopqrstuvwxyz1234567890";
        """
        result = self.rule.evaluate(source, file_path="test.ts")
        self.assertEqual(result.status, RuleDecision.FAIL)
        self.assertEqual(len(result.violations), 2)

    def test_violation_has_evidence_and_location(self):
        source = 'const key = "sk_live_abcdef12345678";'
        result = self.rule.evaluate(source, file_path="test.ts")
        self.assertEqual(result.status, RuleDecision.FAIL)
        self.assertEqual(len(result.violations), 1)
        v = result.violations[0]
        self.assertEqual(v.evidence, "sk_live_abcdef12345678")
        self.assertIsNotNone(v.location)
        self.assertEqual(v.location.line, 1)

    def test_violation_line_number_is_accurate(self):
        source = """
        const a = 1;
        const b = 2;
        const key = "sk_live_abcdef12345678";
        const c = 3;
        """
        result = self.rule.evaluate(source, file_path="test.ts")
        self.assertEqual(result.status, RuleDecision.FAIL)
        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].location.line, 4)


if __name__ == "__main__":
    unittest.main()