# WatchLLM Schemas

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  ░░░░  ░░░      ░░░        ░░░      ░░░  ░░░░  ░░  ░░░░░░░░  ░░░░░░░░  ░░░░  ░
▒  ▒  ▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒   ▒▒   ▒
▓        ▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓
█   ██   ██        █████  █████  ████  ██  ████  ██  ████████  ████████  █  █  █
█  ████  ██  ████  █████  ██████      ███  ████  ██        ██        ██  ████  █
████████████████████████████████████████████████████████████████████████████████
```

*Canonical schema contracts for WatchLLM events, rules, and policies.*

## Current status

Drafting phase. Initial event and result schema stubs defined.

## Overview

The `schemas` repository contains the central specifications and interface contracts for the WatchLLM ecosystem. It defines standard data payloads (as JSON Schemas) to ensure compatibility across the Kernel CLI, visual Replay debugging dashboard, Runtime orchestration SDK, and Cloud audit dashboard.

## Core Features

- **Event Specifications:** Schemas for trace logs, including `parse_started`, `parse_completed`, and `telemetry_relayed`.
- **Violation Representation:** Standard structures for code boundary, credentials leak, and auth-flow violations.
- **Decision Contract:** Formal models representing aggregated decisions (`ALLOW`, `BLOCK`, `INCONCLUSIVE`).

## Relationship to Kernel

- **WatchLLM Schemas (Contracts):** Defines the JSON formatting structures.
- **WatchLLM Kernel (Serialization):** Implements these schemas in local violation reporting and JSON outputs.

## Non-goals

- **Executable Logic:** Contains only static schema files (JSON, Proto, etc.); it does not run or parse code.

## File Directory

```text
schemas/
  v1/
    decision.json
    violation.json
    event.json
```

## Links

- [WatchLLM Organization](https://github.com/WatchLLM)
- [Central Documentation](https://github.com/WatchLLM/docs)
- [watchllm.dev](https://watchllm.dev)
