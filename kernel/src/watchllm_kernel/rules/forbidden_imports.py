"""Forbidden import rule: block dangerous imports and disallowed internal paths.

Uses AST-based import extraction to detect forbidden modules and relative
traversal patterns.

**Denylist rationale** (updated 2026-06-02):
The default forbidden set is intentionally conservative — only modules that
enable *arbitrary code execution* or *sandbox escape* are blocked by default.
Common Node.js modules (``http``, ``path``, ``fs``, etc.) are available for
users to add to a custom list via the ``forbidden_modules`` constructor arg.
"""

from __future__ import annotations

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
    node_text,
    strip_quotes,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# CRITICAL: modules that enable arbitrary code/command execution.
# These are always blocked by default in agent-generated code.
DEFAULT_FORBIDDEN_MODULES = frozenset({
    "child_process",
    "vm",
})

# ELEVATED: modules that grant powerful system access.  Deployments can
# merge this set into ``forbidden_modules`` for stricter enforcement.
ELEVATED_RISK_MODULES = frozenset({
    "cluster",
    "dgram",
    "dns",
    "fs",
    "net",
    "os",
    "readline",
    "repl",
    "tls",
    "tty",
    "v8",
    "worker_threads",
})

DEFAULT_FORBIDDEN_PREFIXES = frozenset({
    "../",
    "../../",
    "../../../",
    "../../../../",
    "../../../../../",
})

# Paths that are explicitly allowed even if they match a forbidden prefix.
# These correspond to boundary-approved cross-module surfaces (e.g. db/public
# contracts that auth modules are permitted to import).
DEFAULT_ALLOWED_RELATIVE_PREFIXES = frozenset({
    "../db/public",
    "../../db/public",
    "../../../db/public",
    "@app/db/public",
})

# ---------------------------------------------------------------------------
# Import extraction
# ---------------------------------------------------------------------------


def extract_import_paths_from_tree(root_node, source_bytes: bytes) -> list[str]:
    """Extract import source strings from a pre-parsed AST.

    Accepts the root tree-sitter node and source bytes directly — no
    parsing is performed.

    Returns a list of import paths (e.g. ``"child_process"``, ``"./utils"``).
    """
    paths: list[str] = []

    def _walk(node):
        if node.type == "import_statement":
            source_node = node.child_by_field_name("source")
            if source_node is not None:
                raw = strip_quotes(node_text(source_bytes, source_node).strip())
                paths.append(raw)
        elif node.type == "call_expression":
            # Handle require('...') calls
            func_node = node.child_by_field_name("function")
            if func_node is not None and node_text(source_bytes, func_node).strip() == "require":
                args = node.child_by_field_name("arguments")
                if args is not None:
                    for child in args.children:
                        if child.type == "string":
                            raw = strip_quotes(node_text(source_bytes, child).strip())
                            paths.append(raw)
        for child in node.children:
            _walk(child)

    _walk(root_node)
    return paths


def extract_import_paths(source: str, file_path: str | None = None, parse_result=None) -> list[str]:
    """Extract import source strings from JS/TS source using Tree-sitter.

    When *parse_result* is provided, the AST is reused — no parsing occurs.
    Returns a list of import paths (e.g. ``"child_process"``, ``"./utils"``).
    """
    pr = ensure_parse_result(source, file_path=file_path, parse_result=parse_result)
    return extract_import_paths_from_tree(pr.root_node, pr.source)


def normalize_import_path(path: str) -> str:
    """Normalise an import path for comparison.

    Strips leading ``./`` and trailing slashes.
    """
    p = path.strip()
    while p.startswith("./"):
        p = p[2:]
    return p.rstrip("/")


# ---------------------------------------------------------------------------
# Rule class
# ---------------------------------------------------------------------------


class ForbiddenImportRule(Rule):
    """Deterministic rule that blocks forbidden imports and disallowed relative paths."""

    def __init__(
        self,
        forbidden_modules: frozenset[str] | None = None,
        forbidden_prefixes: frozenset[str] | None = None,
        allowed_relative_prefixes: frozenset[str] | None = None,
    ):
        super().__init__(
            rule_id="watchllm-rule-imports",
            name="Forbidden import rule",
            description="Blocks dangerous imports and disallowed internal path patterns.",
        )
        self.forbidden_modules = frozenset(forbidden_modules) if forbidden_modules is not None else DEFAULT_FORBIDDEN_MODULES
        self.forbidden_prefixes = frozenset(forbidden_prefixes) if forbidden_prefixes is not None else DEFAULT_FORBIDDEN_PREFIXES
        self.allowed_relative_prefixes = frozenset(allowed_relative_prefixes) if allowed_relative_prefixes is not None else DEFAULT_ALLOWED_RELATIVE_PREFIXES

    def evaluate(self, source: str, file_path: str | None = None, parse_result=None) -> RuleResult:
        import_paths = extract_import_paths(source, file_path=file_path, parse_result=parse_result)
        violations: list[Violation] = []

        for path in import_paths:
            normalised = normalize_import_path(path)

            # Check forbidden module names
            if normalised in self.forbidden_modules:
                violations.append(
                    Violation(
                        rule_id=self.rule_id,
                        message=f"Forbidden import: {path}",
                        severity=Severity.HIGH,
                        evidence=path,
                    )
                )
                continue

            # Check forbidden relative prefixes, but skip explicitly allowed paths.
            # Allowed paths take precedence — they represent boundary-approved
            # cross-module surfaces (e.g. ../db/public contracts).
            if any(path.startswith(allowed) for allowed in self.allowed_relative_prefixes):
                continue

            for prefix in self.forbidden_prefixes:
                if path.startswith(prefix):
                    violations.append(
                        Violation(
                            rule_id=self.rule_id,
                            message=f"Forbidden relative import: {path}",
                            severity=Severity.HIGH,
                            evidence=path,
                        )
                    )
                    break

        if violations:
            return RuleResult(
                rule_id=self.rule_id,
                status=RuleDecision.FAIL,
                violations=violations,
            )
        return RuleResult(rule_id=self.rule_id, status=RuleDecision.PASS)
