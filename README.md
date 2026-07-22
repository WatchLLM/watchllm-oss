<div align="center">
  <img src="https://raw.githubusercontent.com/kaadipranav/kaadipranav/refs/heads/main/assets/2.png"/>
</div>

**Deterministic agent governance — open-core platform for safe autonomous coding agents.**

[Website](https://watchllm.dev) · [Docs](https://docs.watchllm.dev)

---

## What is WatchLLM?

WatchLLM is a deterministic runtime governance platform that parses code via Tree-sitter AST, enforces boundary, auth-flow, and secrets rules in real-time, and blocks unsafe writes before they happen.

This repository contains the **currently shipped open-core** components of WatchLLM — the local kernel, canonical schemas, the VS Code extension source, and example scenarios. A MIT-licensed webproof client SDK is planned but has not shipped; the proving and verification engine remains proprietary.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  WatchLLM Cloud                  │
│   (Managed platform — closed source)             │
│   ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│   │ Runtime  │  │  Replay  │  │ Reliability   │  │
│   │ (Rust)   │  │ (DAG UI) │  │ (Adversarial) │  │
│   └──────────┘  └──────────┘  └───────────────┘  │
└──────────────────────────────────────────────────┘
                        │
         Uses schemas & kernel contracts
                        │
┌──────────────────────────────────────────────────┐
│          Open Source (this repo)                 │
│   ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│   │  Kernel  │  │  Schemas  │  │    VS Code   │  │
│   │ (Python) │  │(Contracts)│  │   Extension  │  │
│   └──────────┘  └───────────┘  └──────────────┘  │
│   ┌───────────────────────────────────────────┐  │
│   │                 Examples                  │  │
│   └───────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
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

The extension is not currently published to the VS Code Marketplace. Build and run it locally using the instructions in [`vscode/README.md`](./vscode/README.md).

## License

MIT — see [LICENSE](./LICENSE).

---

**[WatchLLM Cloud](https://watchllm.dev)** offers the production-grade Rust runtime with DAG replay, adversarial reliability testing, architectural memory (klyd), and multi-model orchestration — all built on the same schemas and kernel contracts in this repo.
