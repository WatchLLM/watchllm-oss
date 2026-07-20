"""Auth-flow rule: require explicit auth verification before protected operations.

Uses AST-based call extraction inside handler functions to detect
mutation-before-auth patterns.  Ambiguous control-flow contexts return
INCONCLUSIVE.

**Handler detection** (updated 2026-06-02):
In addition to named ``function handler()``, the rule now recognises:
  - Arrow functions assigned to a handler-like variable name
    (``const handler = async (req) => { ... }``)
  - Function expressions assigned to a handler-like variable name
    (``const handler = function(req) { ... }``)
  - ``export default function handler(...)``
"""

from __future__ import annotations

import dataclasses
from typing import Optional

from watchllm_kernel.models import (
    Rule,
    RuleDecision,
    RuleResult,
    Severity,
    SourceLocation,
    Violation,
)
from watchllm_kernel.rules._ast_utils import (
    ensure_parse_result,
    location_from_node,
    node_text,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AUTH_FLOW_INCONCLUSIVE_POLICY = (
    "INCONCLUSIVE: if an auth guard is found only inside a branch or other "
    "ambiguous control-flow context before a protected operation, Task 09 "
    "does not prove all paths are authenticated."
)

PROTECTED_MUTATION_METHODS = frozenset({
    "create",
    "insert",
    "update",
    "delete",
    "remove",
    "query",
    "execute",
    "prepare",
})

AUTH_GUARD_NAMES = frozenset({
    "auth.verify",
    "verifyAuth",
    "requireAuth",
    "authenticate",
    "assertAuthenticated",
})

# Names that identify a function/variable as a request handler.
HANDLER_NAMES = frozenset({
    "handler",
    "handleRequest",
    "requestHandler",
})

AMBIGUOUS_CONTEXT_NODES = frozenset({
    "if_statement",
    "conditional_expression",
    "switch_statement",
    "try_statement",
    "catch_clause",
    "for_statement",
    "for_in_statement",
    "while_statement",
    "do_statement",
})

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CallEvent:
    """A single call event extracted from source code."""

    kind: str
    callee: str
    location: SourceLocation
    ambiguous: bool = False


# ---------------------------------------------------------------------------
# Handler detection
# ---------------------------------------------------------------------------


def _function_name(source_bytes: bytes, node) -> Optional[str]:
    """Return the function name for a function_declaration node, or None."""
    if node.type != "function_declaration":
        return None
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return None
    return node_text(source_bytes, name_node).strip()


def _is_handler_function(source_bytes: bytes, node) -> bool:
    """Return True if *node* is a function_declaration with a handler-like name."""
    if node.type != "function_declaration":
        return False
    name = _function_name(source_bytes, node)
    return name in HANDLER_NAMES


def _is_handler_variable(source_bytes: bytes, node) -> bool:
    """Return True if *node* is a variable_declarator that assigns an
    arrow_function or function (expression) to a handler-like variable name.

    Matches patterns like::

        const handler = async (req) => { ... };
        const handleRequest = function(req) { ... };
    """
    if node.type != "variable_declarator":
        return False
    name_node = node.child_by_field_name("name")
    if name_node is None:
        return False
    var_name = node_text(source_bytes, name_node).strip()
    if var_name not in HANDLER_NAMES:
        return False
    value_node = node.child_by_field_name("value")
    if value_node is None:
        return False
    return value_node.type in ("arrow_function", "function", "function_expression")


# ---------------------------------------------------------------------------
# Call classification helpers
# ---------------------------------------------------------------------------


def _callee_text(source_bytes: bytes, call_node) -> str:
    """Extract the callee text from a call_expression node."""
    func_node = call_node.child_by_field_name("function")
    if func_node is None:
        # Fallback to first child
        func_node = call_node.children[0] if call_node.children else call_node
    return node_text(source_bytes, func_node).strip()


def is_auth_guard_call(callee: str) -> bool:
    """Return True if *callee* matches a known auth guard pattern."""
    if callee in AUTH_GUARD_NAMES:
        return True
    for suffix in (".verify", ".verifyAuth", ".requireAuth", ".authenticate", ".assertAuthenticated"):
        if callee.endswith(suffix):
            return True
    return False


def is_protected_operation_call(callee: str) -> bool:
    """Return True if *callee* is a protected database operation."""
    if not callee.startswith("db."):
        return False
    segments = callee.split(".")
    return any(seg in PROTECTED_MUTATION_METHODS for seg in segments)


# ---------------------------------------------------------------------------
# Event extraction
# ---------------------------------------------------------------------------


def extract_call_events(source: str, file_path: str | None = None, parse_result=None) -> list[CallEvent]:
    """Extract ordered CallEvents from handler functions in *source*.

    Detects handler functions declared as:
      - ``function handler() { ... }``
      - ``const handler = async (req) => { ... }``
      - ``const handler = function(req) { ... }``
    """
    pr = ensure_parse_result(source, file_path=file_path, parse_result=parse_result)
    source_bytes = pr.source
    root = pr.root_node

    events: list[CallEvent] = []

    def _walk_handler_body(node, ambiguous: bool):
        """Recursively walk the body of a handler, collecting call events."""
        if node.type == "call_expression":
            callee = _callee_text(source_bytes, node)
            if is_auth_guard_call(callee):
                events.append(
                    CallEvent(
                        kind="auth_guard",
                        callee=callee,
                        location=location_from_node(node),
                        ambiguous=ambiguous,
                    )
                )
            elif is_protected_operation_call(callee):
                events.append(
                    CallEvent(
                        kind="protected_operation",
                        callee=callee,
                        location=location_from_node(node),
                        ambiguous=ambiguous,
                    )
                )

        next_ambiguous = ambiguous or node.type in AMBIGUOUS_CONTEXT_NODES
        for child in node.children:
            _walk_handler_body(child, next_ambiguous)

    def _walk(node):
        """Top-level walk that locates handler scopes."""
        # Named function declaration: function handler() { ... }
        if node.type == "function_declaration":
            if _is_handler_function(source_bytes, node):
                for child in node.children:
                    _walk_handler_body(child, ambiguous=False)
            # Skip all non-handler function declarations entirely —
            # db calls inside helper functions are not in scope for this rule.
            return

        # Variable declarator: const handler = async (req) => { ... }
        if node.type == "variable_declarator":
            if _is_handler_variable(source_bytes, node):
                value_node = node.child_by_field_name("value")
                if value_node is not None:
                    _walk_handler_body(value_node, ambiguous=False)
            return

        for child in node.children:
            _walk(child)

    _walk(root)

    # Sort by location
    events.sort(key=lambda e: (e.location.line, e.location.column))
    return events


# ---------------------------------------------------------------------------
# Rule class
# ---------------------------------------------------------------------------


class AuthFlowRule(Rule):
    """Deterministic rule that requires auth before protected operations."""

    def __init__(self):
        super().__init__(
            rule_id="watchllm-rule-auth",
            name="Auth flow rule",
            description="Requires explicit auth verification before protected operations in handler scope.",
        )

    def evaluate(self, source: str, file_path: str | None = None, parse_result=None) -> RuleResult:
        events = extract_call_events(source, file_path=file_path, parse_result=parse_result)

        saw_definite_guard = False
        saw_ambiguous_guard = False

        for event in events:
            if event.kind == "auth_guard":
                if event.ambiguous:
                    saw_ambiguous_guard = True
                else:
                    saw_definite_guard = True
            elif event.kind == "protected_operation":
                if saw_definite_guard:
                    continue
                if saw_ambiguous_guard:
                    return RuleResult(
                        rule_id=self.rule_id,
                        status=RuleDecision.INCONCLUSIVE,
                    )
                # No guard seen at all
                violation = Violation(
                    rule_id=self.rule_id,
                    message="Protected operation occurs before auth verification.",
                    location=event.location,
                    severity=Severity.HIGH,
                    evidence=event.callee,
                )
                return RuleResult(
                    rule_id=self.rule_id,
                    status=RuleDecision.FAIL,
                    violations=[violation],
                )

        return RuleResult(rule_id=self.rule_id, status=RuleDecision.PASS)
