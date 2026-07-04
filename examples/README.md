# WatchLLM Examples

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  ░░░░  ░░░      ░░░        ░░░      ░░░  ░░░░  ░░  ░░░░░░░░  ░░░░░░░░  ░░░░  ░
▒  ▒  ▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒   ▒▒   ▒
▓        ▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓
█   ██   ██        █████  █████  ████  ██  ████  ██  ████████  ████████  █  █  █
█  ████  ██  ████  █████  ██████      ███  ████  ██        ██        ██  ████  █
████████████████████████████████████████████████████████████████████████████████
```

*Curated demonstrations and integration examples for the WatchLLM governance ecosystem.*

## Current status

Active development. Scenario directories structured with READMEs and stub files. Safe/unsafe pairs being expanded.

## Overview

The `examples` repository hosts curated scenarios and code samples to demonstrate the enforcement patterns of the WatchLLM Kernel. It includes examples of secure practices (which pass validation) and insecure violations (which block save operations), serving as a regression test target and user-onboarding guide.

## Directory Structure

This repository is organized into distinct scenario folders:

- **[scenarios/](scenarios/README.md):** Root directory for scenario demonstrations.
- **scenarios/secrets:** Demonstrates hardcoded credential detection versus safe retrieval environments.
- **scenarios/boundaries:** Demonstrates service-boundary importing checks (e.g. blocking internal DB imports).
- **scenarios/auth_flow:** Demonstrates sequential DB mutations without auth verification.

## Relationship to Kernel

- **WatchLLM Examples (Targets):** The sample codebases evaluated by the Kernel.
- **WatchLLM Kernel (Evaluator):** Scans these folders during end-to-end integration tests to assert block/allow decisions.

## Non-goals

- **Core Rule Development:** No rules are written in this repository; it contains target codebases only.

## Links

- [WatchLLM Organization](https://github.com/WatchLLM)
- [Central Documentation](https://github.com/WatchLLM/docs)
- [watchllm.dev](https://watchllm.dev)