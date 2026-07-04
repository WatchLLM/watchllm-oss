"""Boundary rule: enforce declared service/module import boundaries.

Uses AST-extracted import paths from the forbidden-import rule to detect
cross-boundary edges.  Circular dependency detection is explicitly deferred.
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
from watchllm_kernel.rules._ast_utils import ensure_parse_result
from watchllm_kernel.rules.forbidden_imports import (
    extract_import_paths,
    normalize_import_path,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BOUNDARY_MAP = {
    "auth": {
        "forbidden": (("db", "internal"),),
        "allowed": (("db", "public"),),
    },
}

CIRCULAR_DEPENDENCY_POLICY = (
    "EXCLUDED: Task 08 evaluates single-file import edges only; "
    "repository-wide circular dependency detection is deferred."
)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ImportEdge:
    """A single import edge extracted from source code."""

    source_module: str
    target_module: Optional[str]
    target_surface: Optional[str]
    import_path: str
    location: Optional[SourceLocation] = None


# ---------------------------------------------------------------------------
# Source module inference
# ---------------------------------------------------------------------------


def infer_source_module(file_path: str | None) -> str:
    """Infer a logical module name from a file path.

    Returns ``"unknown"`` when no module can be inferred.
    """
    if not file_path:
        return "unknown"

    # Normalise Windows separators
    path = file_path.replace("\\", "/")

    # Check for explicit auth segment
    segments = path.split("/")
    if "auth" in segments:
        return "auth"

    # Check basename for auth_ or auth- prefix
    basename = segments[-1] if segments else ""
    if basename.startswith("auth_") or basename.startswith("auth-"):
        return "auth"

    return "unknown"


# ---------------------------------------------------------------------------
# Target classification helpers
# ---------------------------------------------------------------------------


def _matches_path_prefix(path: str, prefix: str) -> bool:
    """Return True if *path* equals *prefix* or starts with *prefix* + ``/``."""
    return path == prefix or path.startswith(prefix + "/")


def classify_import_target(import_path: str) -> tuple[str | None, str | None]:
    """Classify an import path into (module, surface).

    Returns ``(None, None)`` when the path does not match any known target.
    """
    normalised = normalize_import_path(import_path)

    # DB internal prefixes
    for prefix in (
        "../db/internal",
        "../../db/internal",
        "../../../db/internal",
        "@app/db/internal",
    ):
        if _matches_path_prefix(normalised, prefix):
            return ("db", "internal")

    # DB public prefixes
    for prefix in (
        "../db/public",
        "../../db/public",
        "../../../db/public",
        "@app/db/public",
    ):
        if _matches_path_prefix(normalised, prefix):
            return ("db", "public")

    return (None, None)


# ---------------------------------------------------------------------------
# Import graph extraction
# ---------------------------------------------------------------------------


def extract_import_edges(
    source: str, file_path: str | None = None, parse_result=None
) -> list[ImportEdge]:
    """Extract import edges from source text using AST-derived import paths.

    When *parse_result* is provided the AST is reused, avoiding a
    redundant parse.
    """
    source_module = infer_source_module(file_path)
    import_paths = extract_import_paths(source, parse_result=parse_result)

    edges: list[ImportEdge] = []
    for path in import_paths:
        target_module, target_surface = classify_import_target(path)
        edges.append(
            ImportEdge(
                source_module=source_module,
                target_module=target_module,
                target_surface=target_surface,
                import_path=path,
            )
        )
    return edges


# ---------------------------------------------------------------------------
# Boundary violation decision
# ---------------------------------------------------------------------------


def is_boundary_violation(
    edge: ImportEdge,
    boundary_map: dict[
        str, dict[str, tuple[tuple[str, str], ...]]
    ] = DEFAULT_BOUNDARY_MAP,
) -> bool:
    """Return True if *edge* violates the declared boundary map."""
    if edge.source_module not in boundary_map:
        return False
    if edge.target_module is None or edge.target_surface is None:
        return False

    policy = boundary_map[edge.source_module]
    forbidden = policy.get("forbidden", ())
    return (edge.target_module, edge.target_surface) in forbidden


# ---------------------------------------------------------------------------
# Rule class
# ---------------------------------------------------------------------------


class BoundaryRule(Rule):
    """Deterministic rule that blocks imports violating declared boundaries."""

    def __init__(self, boundary_map=None):
        super().__init__(
            rule_id="BOUNDARY",
            name="Boundary rule",
            description="Blocks imports that violate declared service/module boundaries.",
        )
        self.boundary_map = (
            boundary_map if boundary_map is not None else DEFAULT_BOUNDARY_MAP
        )

    def evaluate(self, source: str, file_path: str | None = None, parse_result=None) -> RuleResult:
        edges = extract_import_edges(source, file_path=file_path, parse_result=parse_result)
        violations: list[Violation] = []

        for edge in edges:
            if is_boundary_violation(edge, self.boundary_map):
                violations.append(
                    Violation(
                        rule_id=self.rule_id,
                        message=(
                            f"Boundary violation: {edge.source_module} cannot import "
                            f"{edge.target_module}/{edge.target_surface}"
                        ),
                        location=edge.location,
                        severity=Severity.HIGH,
                        evidence=edge.import_path,
                    )
                )

        if violations:
            return RuleResult(
                rule_id=self.rule_id,
                decision=RuleDecision.FAIL,
                violations=violations,
            )
        return RuleResult(rule_id=self.rule_id, decision=RuleDecision.PASS)
