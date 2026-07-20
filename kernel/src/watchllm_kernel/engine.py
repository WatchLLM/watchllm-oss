"""Deterministic decision engine for the WatchLLM kernel.

Combines rule results into a single kernel-level decision.

The engine now parses source **once** via ``parser.parse_source`` and
passes the resulting ``ParseResult`` to every rule, eliminating the
redundant per-rule parsing that existed previously.
"""

from __future__ import annotations

from typing import Optional

from watchllm_kernel.models import Decision, KernelResult, Rule, RuleDecision, RuleResult, Violation
from watchllm_kernel.parser import parse_source
from watchllm_kernel.rules._ast_utils import infer_language_from_path

# ---------------------------------------------------------------------------
# Mode constants
# ---------------------------------------------------------------------------

ENFORCE_MODE = "enforce"
SHADOW_MODE = "shadow"
VALID_MODES = frozenset({ENFORCE_MODE, SHADOW_MODE})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def has_blocking_failure(rule_results: list[RuleResult]) -> bool:
    """Return True if any rule result is a FAIL.

    PASS and INCONCLUSIVE are not considered blocking for Task 10.
    """
    return any(rr.status == RuleDecision.FAIL for rr in rule_results)


def collect_violations(rule_results: list[RuleResult]) -> list[Violation]:
    """Return a flat list of all violations from *rule_results*.

    Preserves rule execution order and violation order inside each rule.
    """
    violations: list[Violation] = []
    for rr in rule_results:
        violations.extend(rr.violations)
    return violations


def reduce_decision(
    rule_results: list[RuleResult], mode: str = ENFORCE_MODE
) -> Decision:
    """Reduce a list of rule results into a single kernel decision.

    Raises ValueError if *mode* is not a recognised mode.
    """
    if mode not in VALID_MODES:
        raise ValueError(
            f"Unknown mode {mode!r}. Valid modes: {sorted(VALID_MODES)}"
        )

    if mode == SHADOW_MODE:
        return Decision.ALLOW

    # enforce mode
    if has_blocking_failure(rule_results):
        return Decision.BLOCK
    return Decision.ALLOW


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


def evaluate_source(
    source: str,
    *,
    file_path: str | None = None,
    language: str | None = None,
    rules: list[Rule] | tuple[Rule, ...],
    mode: str = ENFORCE_MODE,
) -> KernelResult:
    """Run *rules* against *source* and return a coherent KernelResult.

    The engine parses the source **once** and shares the ``ParseResult``
    with every rule, eliminating redundant tree-sitter work.

    Rules are evaluated in the given order.  Exceptions are not caught in
    Task 10 – failing fast is acceptable for now.
    """
    if mode not in VALID_MODES:
        raise ValueError(
            f"Unknown mode {mode!r}. Valid modes: {sorted(VALID_MODES)}"
        )

    # Parse once — infer language from file_path if not given explicitly.
    resolved_language = language or infer_language_from_path(file_path)
    parse_result = parse_source(source, language=resolved_language, file_path=file_path)

    rule_results: list[RuleResult] = []
    for rule in rules:
        result = rule.evaluate(source, file_path=file_path, parse_result=parse_result)
        rule_results.append(result)

    decision = reduce_decision(rule_results, mode=mode)

    return KernelResult(
        decision=decision,
        rule_results=rule_results,
        file_path=file_path,
        language=resolved_language,
        mode=mode,
    )
