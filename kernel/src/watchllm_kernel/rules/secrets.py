"""Secret-literal rule: block hardcoded credential patterns in structural context.

Uses AST context to avoid flagging safe retrieval calls such as
``process.env.STRIPE_SECRET`` or ``os.getenv("STRIPE_SECRET")``.
"""

from __future__ import annotations

import re
from typing import Optional

from watchllm_kernel.models import (
    Rule,
    RuleDecision,
    RuleResult,
    Severity,
    Violation,
)
from watchllm_kernel.rules._ast_utils import (
    ensure_parse_result,
    location_from_node,
    node_text,
    strip_quotes,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Patterns that look like live secrets (prefix-based)
SECRET_PATTERNS = [
    re.compile(r"sk_live_[0-9a-zA-Z]{10,}"),
    re.compile(r"pk_live_[0-9a-zA-Z]{10,}"),
    re.compile(r"rk_live_[0-9a-zA-Z]{10,}"),
    re.compile(r"whsec_[0-9a-zA-Z]{10,}"),
    re.compile(r"sk_test_[0-9a-zA-Z]{10,}"),
    re.compile(r"pk_test_[0-9a-zA-Z]{10,}"),
    re.compile(r"rk_test_[0-9a-zA-Z]{10,}"),
    re.compile(r"sk-"),
    re.compile(r"xox[baprs]-[0-9a-zA-Z-]{10,}"),
    re.compile(r"ghp_[0-9a-zA-Z]{36}"),
    re.compile(r"gho_[0-9a-zA-Z]{36}"),
    re.compile(r"ghu_[0-9a-zA-Z]{36}"),
    re.compile(r"ghs_[0-9a-zA-Z]{36}"),
    re.compile(r"ghr_[0-9a-zA-Z]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"ya29\.[0-9A-Za-z\-_]+"),
    re.compile(r"sk-ant-api03-[0-9a-zA-Z\-_]{20,}"),
    re.compile(r"sk-or-v1-[0-9a-f]{64}"),
    re.compile(r"sk-proj-[0-9a-zA-Z\-_]{20,}"),
    re.compile(r"sk-svcacct-[0-9a-zA-Z\-_]{20,}"),
    re.compile(r"sk-[0-9a-zA-Z]{48}"),
    re.compile(r"sk-[0-9a-zA-Z]{32}"),
    re.compile(r"sk-[0-9a-zA-Z]{20,}"),
]

# Safe retrieval patterns that indicate the string is a variable name, not a secret
SAFE_RETRIEVAL_PATTERNS = [
    re.compile(r"process\.env\."),
    re.compile(r"os\.getenv\("),
    re.compile(r"os\.environ\["),
    re.compile(r"getenv\("),
    re.compile(r"env\("),
    re.compile(r"config\("),
    re.compile(r"secret\("),
    re.compile(r"vault\("),
    re.compile(r"credential\("),
    re.compile(r"key\("),
    re.compile(r"token\("),
]

# ---------------------------------------------------------------------------
# AST context helpers
# ---------------------------------------------------------------------------


def _is_inside_comment(source_bytes: bytes, node) -> bool:
    """Return True if *node* is inside a comment."""
    current = node
    while current is not None:
        if current.type in ("comment", "line_comment", "block_comment"):
            return True
        current = current.parent
    return False


def _is_inside_safe_retrieval(source_bytes: bytes, node) -> bool:
    """Return True if *node* is inside a safe retrieval call."""
    current = node
    while current is not None:
        if current.type == "call_expression":
            func_node = current.child_by_field_name("function")
            if func_node is not None:
                callee = node_text(source_bytes, func_node).strip()
                for pattern in SAFE_RETRIEVAL_PATTERNS:
                    if pattern.search(callee):
                        return True
        current = current.parent
    return False


def _is_direct_assignment(source_bytes: bytes, node) -> bool:
    """Return True if *node* is directly assigned to a variable or property."""
    current = node
    while current is not None:
        if current.type in (
            "variable_declarator",
            "assignment_expression",
            "pair",
            "object",
            "array",
            "arguments",
        ):
            return True
        current = current.parent
    return False


# ---------------------------------------------------------------------------
# Rule class
# ---------------------------------------------------------------------------


class SecretLiteralRule(Rule):
    """Deterministic rule that blocks hardcoded secret patterns in structural context."""

    def __init__(self):
        super().__init__(
            rule_id="watchllm-rule-secrets",
            name="Secret literal rule",
            description="Blocks hardcoded credential patterns when they appear in assignment or dangerous call contexts.",
        )

    def evaluate(self, source: str, file_path: str | None = None, parse_result=None) -> RuleResult:
        pr = ensure_parse_result(source, file_path=file_path, parse_result=parse_result)
        source_bytes = pr.source
        root = pr.root_node

        violations: list[Violation] = []

        def _walk(node):
            if node.type == "string":
                text = strip_quotes(node_text(source_bytes, node).strip())

                # Check if the string matches any secret pattern
                matched = False
                for pattern in SECRET_PATTERNS:
                    if pattern.search(text):
                        matched = True
                        break

                if not matched:
                    return

                # Skip if inside a comment
                if _is_inside_comment(source_bytes, node):
                    return

                # Skip if inside a safe retrieval call
                if _is_inside_safe_retrieval(source_bytes, node):
                    return

                # Only flag if it's a direct assignment
                if not _is_direct_assignment(source_bytes, node):
                    return

                violations.append(
                    Violation(
                        rule_id=self.rule_id,
                        message=f"Hardcoded secret detected: {text}",
                        location=location_from_node(node),
                        severity=Severity.CRITICAL,
                        evidence=text,
                    )
                )

            for child in node.children:
                _walk(child)

        _walk(root)

        if violations:
            return RuleResult(
                rule_id=self.rule_id,
                status=RuleDecision.FAIL,
                violations=violations,
            )
        return RuleResult(rule_id=self.rule_id, status=RuleDecision.PASS)
