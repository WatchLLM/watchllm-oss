# WatchLLM Open Source

```
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░  ░░░░  ░░░      ░░░        ░░░      ░░░  ░░░░  ░░  ░░░░░░░░  ░░░░░░░░  ░░░░  ░
    ▒  ▒  ▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒▒▒   ▒▒   ▒
    ▓        ▓▓  ▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓        ▓
    █   ██   ██        █████  █████  ████  ██  ████  ██  ████████  ████████  █  █  █
    █  ████  ██  ████  █████  ██████      ███  ████  ██        ██        ██  ████  █
    ████████████████████████████████████████████████████████████████████████████████
```

**Deterministic agent governance — open-core platform for safe autonomous coding agents.**

[Website](https://watchllm.dev) · [Docs](https://docs.watchllm.dev) · [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=watchllm.watchllm-vscode)

---

## What is WatchLLM?

WatchLLM is a deterministic runtime governance platform that parses code via Tree-sitter AST, enforces boundary, auth-flow, and secrets rules in real-time, and blocks unsafe writes before they happen.

This repository contains the **open-core** components of WatchLLM — the local kernel, canonical schemas, the VS Code extension, and example scenarios.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  WatchLLM Cloud                   │
│   (Managed platform — closed source)              │
│   ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│   │ Runtime  │  │  Replay  │  │ Reliability  │  │
│   │ (Rust)   │  │ (DAG UI) │  │  (Adversarial)│  │
│   └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘
                        │
         Uses schemas & kernel contracts
                        │
┌─────────────────────────────────────────────────┐
│          Open Source (this repo)                  │
│   ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│   │  Kernel  │  │ Schemas  │  │  VS Code     │  │
│   │ (Python) │  │(Contracts)│  │  Extension   │  │
│   └──────────┘  └──────────┘  └──────────────┘  │
│   ┌──────────────────────────────────────────┐  │
│   │              Examples                     │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Repository Structure

| Directory | Description |
|-----------|-------------|
| [`kernel/`](./kernel) | Deterministic Python kernel — Tree-sitter AST parsing, rule engine, CLI |
| [`schemas/`](./schemas) | Canonical JSON Schema contracts for events, violations, and decisions |
| [`vscode/`](./vscode) | VS Code extension for save-path governance and inline diagnostics |
| [`examples/`](./examples) | Scenario fixtures demonstrating boundary, auth, and secrets rules |

## Quick Start

### Install the kernel

```bash
pip install watchllm-kernel
```

### Run a local scan

```bash
watchllm-kernel scan ./my-project
```

### Use with VS Code

Install the [WatchLLM extension](https://marketplace.visualstudio.com/items?itemName=watchllm.watchllm-vscode) from the marketplace.

## License

MIT — see [LICENSE](./LICENSE).

---

**[WatchLLM Cloud](https://watchllm.dev)** offers the production-grade Rust runtime with DAG replay, adversarial reliability testing, architectural memory (klyd), and multi-model orchestration — all built on the same schemas and kernel contracts in this repo.