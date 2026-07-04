from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from watchllm_kernel.parser import ParseResult


class Decision(enum.Enum):
    """Top-level decision returned by the kernel."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


class RuleDecision(enum.Enum):
    """Per-rule decision."""
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class Severity(enum.Enum):
    """Severity of a rule violation."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclasses.dataclass
class SourceLocation:
    """Location span in source code."""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclasses.dataclass
class Violation:
    """A single rule violation."""
    rule_id: str
    message: str
    location: Optional[SourceLocation] = None
    severity: Severity = Severity.HIGH
    evidence: Optional[str] = None


@dataclasses.dataclass
class RuleResult:
    """Result of evaluating a single rule."""
    rule_id: str
    decision: RuleDecision
    violations: list[Violation] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class KernelResult:
    """Aggregated result from the kernel."""
    decision: Decision
    rule_results: list[RuleResult] = dataclasses.field(default_factory=list)
    file_path: Optional[str] = None
    language: Optional[str] = None
    mode: str = "enforce"


class Rule:
    """Abstract base for a deterministic rule.

    Every rule must implement ``evaluate`` and return a ``RuleResult``.

    Parameters passed to ``evaluate``:
        source:       The raw source text.
        file_path:    Optional path of the file being evaluated.
        parse_result: Optional pre-parsed ``ParseResult`` from the engine.
                      When provided, rules should use it instead of parsing
                      the source again.  Rules must still work correctly
                      when ``parse_result`` is ``None``.
    """

    def __init__(self, rule_id: str, name: str, description: str = ""):
        self.rule_id = rule_id
        self.name = name
        self.description = description

    def evaluate(
        self,
        source: str,
        file_path: Optional[str] = None,
        parse_result: Optional[ParseResult] = None,
    ) -> RuleResult:
        """Evaluate the rule against the given source text.

        Subclasses must override this method.
        """
        raise NotImplementedError("Subclasses must implement evaluate()")

