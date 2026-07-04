# WatchLLM Kernel Benchmark Baseline

## Purpose

This records the current Python kernel performance baseline before future Rust/Wasm optimisation.

## Command

```bash
python benchmarks/run_benchmarks.py --iterations 50 --warmup 5 --json
```

## Metrics

- parse latency
- current rule evaluation latency
- end-to-end kernel evaluation latency

## Current baseline

```json
{
  "schema_version": "watchllm.kernel.benchmark.v1",
  "iterations": 50,
  "warmup": 5,
  "fixture_count": 8,
  "benchmarks": {
    "parse_ms": {
      "count": 400,
      "min_ms": 0.016,
      "median_ms": 0.033,
      "p95_ms": 0.052,
      "max_ms": 0.073,
      "mean_ms": 0.034
    },
    "rule_evaluation_ms": {
      "count": 1600,
      "min_ms": 0.008,
      "median_ms": 0.017,
      "p95_ms": 0.031,
      "max_ms": 0.047,
      "mean_ms": 0.018
    },
    "end_to_end_ms": {
      "count": 400,
      "min_ms": 0.045,
      "median_ms": 0.067,
      "p95_ms": 0.098,
      "max_ms": 0.124,
      "mean_ms": 0.069
    }
  },
  "budgets": {
    "parse_median_ms": 4.0,
    "rule_evaluation_median_ms": 5.0,
    "end_to_end_median_ms": 10.0
  },
  "environment": {
    "python": "3.12.0 (main, Oct  2 2023, 00:00:00) [Clang 15.0.0 (clang-1500.0.40.1)]",
    "platform": "darwin"
  }
}
```

## Notes

- Budgets are informational in this phase.
- This benchmark does not introduce enforcement changes.
- Failing fixtures are expected to produce BLOCK decisions during end-to-end evaluation.
- Current rule evaluation may include rule-local parsing where rules currently do that.
