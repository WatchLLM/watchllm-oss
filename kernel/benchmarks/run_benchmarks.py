"""WatchLLM Kernel benchmark runner.

Measures parser, rule evaluation, and end-to-end latency for the current
Python kernel.  Uses only the standard library and existing project modules.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap repo root so that `watchllm_kernel` is importable.
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from watchllm_kernel.cli import build_default_rules
from watchllm_kernel.engine import ENFORCE_MODE, evaluate_source
from watchllm_kernel.parser import parse_source

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "rules"
VALID_SUFFIXES = frozenset({".js", ".jsx", ".ts", ".tsx"})
VALID_PARENT_DIRS = frozenset({"pass", "fail"})

SCHEMA_VERSION = "watchllm.kernel.benchmark.v1"

BUDGETS = {
    "parse_median_ms": 4.0,
    "rule_evaluation_median_ms": 5.0,
    "end_to_end_median_ms": 10.0,
}


# ---------------------------------------------------------------------------
# Fixture discovery
# ---------------------------------------------------------------------------
def discover_fixtures() -> list[Path]:
    """Return a deterministically sorted list of fixture files.

    Only files whose immediate parent directory is ``pass`` or ``fail``
    and whose suffix is in ``VALID_SUFFIXES`` are included.
    """
    fixtures: list[Path] = []
    for path in sorted(FIXTURE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in VALID_SUFFIXES:
            continue
        if path.parent.name not in VALID_PARENT_DIRS:
            continue
        fixtures.append(path)
    return fixtures


def infer_language(path: Path) -> str:
    """Map file extension to a language identifier understood by the parser."""
    suffix = path.suffix.lower()
    if suffix == ".tsx":
        return "tsx"
    if suffix == ".ts":
        return "typescript"
    return "javascript"


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------
def compute_stats(timings_ms: list[float]) -> dict:
    """Return a dict with count, min, median, p95, max, mean for *timings_ms*.

    If *timings_ms* is empty, returns zeros with count 0.
    """
    if not timings_ms:
        return {
            "count": 0,
            "min_ms": 0.0,
            "median_ms": 0.0,
            "p95_ms": 0.0,
            "max_ms": 0.0,
            "mean_ms": 0.0,
        }

    sorted_timings = sorted(timings_ms)
    n = len(sorted_timings)

    def _percentile(p: float) -> float:
        """Return the p-th percentile (0 <= p <= 100) using linear interpolation."""
        if n == 1:
            return sorted_timings[0]
        k = (p / 100.0) * (n - 1)
        f = int(k)
        c = k - f
        if f + 1 < n:
            return sorted_timings[f] + c * (sorted_timings[f + 1] - sorted_timings[f])
        return sorted_timings[f]

    return {
        "count": n,
        "min_ms": sorted_timings[0],
        "median_ms": statistics.median(sorted_timings),
        "p95_ms": _percentile(95),
        "max_ms": sorted_timings[-1],
        "mean_ms": statistics.mean(sorted_timings),
    }


# ---------------------------------------------------------------------------
# Benchmark groups
# ---------------------------------------------------------------------------
def run_parse_benchmark(fixtures: list[Path], iterations: int, warmup: int) -> dict:
    timings: list[float] = []
    for _ in range(warmup):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            language = infer_language(path)
            parse_source(source, language=language, file_path=str(path))

    for _ in range(iterations):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            language = infer_language(path)
            t0 = time.perf_counter()
            parse_source(source, language=language, file_path=str(path))
            elapsed = (time.perf_counter() - t0) * 1000.0
            timings.append(elapsed)

    return compute_stats(timings)


def run_rule_evaluation_benchmark(
    fixtures: list[Path], iterations: int, warmup: int
) -> dict:
    rules = build_default_rules()
    timings: list[float] = []

    for _ in range(warmup):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            for rule in rules:
                rule.evaluate(source, file_path=str(path))

    for _ in range(iterations):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            for rule in rules:
                t0 = time.perf_counter()
                rule.evaluate(source, file_path=str(path))
                elapsed = (time.perf_counter() - t0) * 1000.0
                timings.append(elapsed)

    return compute_stats(timings)


def run_end_to_end_benchmark(
    fixtures: list[Path], iterations: int, warmup: int
) -> dict:
    rules = build_default_rules()
    timings: list[float] = []

    for _ in range(warmup):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            language = infer_language(path)
            evaluate_source(
                source,
                file_path=str(path),
                language=language,
                rules=rules,
                mode=ENFORCE_MODE,
            )

    for _ in range(iterations):
        for path in fixtures:
            source = path.read_text(encoding="utf-8")
            language = infer_language(path)
            t0 = time.perf_counter()
            evaluate_source(
                source,
                file_path=str(path),
                language=language,
                rules=rules,
                mode=ENFORCE_MODE,
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            timings.append(elapsed)

    return compute_stats(timings)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WatchLLM Kernel benchmark runner"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of measured iterations (default: 50)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=5,
        help="Number of warmup iterations (default: 5)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON result to stdout",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON result to the given file path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    fixtures = discover_fixtures()
    if not fixtures:
        print("No fixtures found under", FIXTURE_ROOT, file=sys.stderr)
        return 1

    parse_stats = run_parse_benchmark(fixtures, args.iterations, args.warmup)
    rule_stats = run_rule_evaluation_benchmark(fixtures, args.iterations, args.warmup)
    e2e_stats = run_end_to_end_benchmark(fixtures, args.iterations, args.warmup)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "fixture_count": len(fixtures),
        "benchmarks": {
            "parse_ms": parse_stats,
            "rule_evaluation_ms": rule_stats,
            "end_to_end_ms": e2e_stats,
        },
        "budgets": BUDGETS,
        "environment": {
            "python": sys.version,
            "platform": sys.platform,
        },
    }

    json_text = json.dumps(payload, indent=2)

    if args.output:
        args.output.write_text(json_text, encoding="utf-8")

    if args.json:
        print(json_text)
    elif not args.output:
        # Human-readable summary
        print("WatchLLM Kernel Benchmark")
        print(f"  fixtures: {len(fixtures)}")
        print(f"  iterations: {args.iterations}  warmup: {args.warmup}")
        print()
        for group, stats in payload["benchmarks"].items():
            print(f"  {group}:")
            for key, value in stats.items():
                print(f"    {key}: {value}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
