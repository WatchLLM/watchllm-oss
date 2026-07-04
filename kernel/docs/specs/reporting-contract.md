# Reporting Contract

## Purpose

Defines the local violation reporting and JSONL logging contract for the Python kernel.

## Scope

- Local blocked-event logging
- Human-readable CLI violation output
- Machine-readable JSONL violation reports

## Non-goals

- Cloud telemetry
- Remote sync
- LLM explanations
- Policy override
- Editor UI diagnostics

## Log location

Default:

`.watchllm/logs/violations.jsonl`

Override:

`WATCHLLM_LOG_PATH`

## JSONL schema

Schema version:

`watchllm.kernel.violation_report.v1`

Required top-level fields:

- schema_version
- timestamp
- decision
- file_path
- language
- mode
- parse_status
- violations

Required violation fields:

- rule_id
- message
- severity
- evidence
- location

## Parse status

For Task 14, parse status is recorded as `not_recorded` because parsing currently happens inside individual rules rather than through a central parse pipeline.

## Guarantees

- Logging is local-only.
- Logging does not affect enforcement decisions.
- Logging does not require network access.
- Blocked events are appended as JSONL.
- JSON CLI output is not polluted by log messages.
