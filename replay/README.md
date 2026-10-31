# WatchLLM Replay

*Execution replay and runtime forensics for autonomous coding agents.*

## Current status

Early design & specification phase. Subsystem boundary defined; codebase scaffolded.

## Overview

The `replay` repository contains the observability suite for WatchLLM. It records agent execution graphs, including every tool call, state change, and final code modification event. Developers and security teams can replay agent histories in a visual timeline, perform branch comparisons, and analyze hallucinations with lineage tracing instead of guessing.

## Core Features

- **Execution Graph Recording:** Captures structured trace events containing tool parameters and environmental modifications.
- **Trace Replay Engine:** Replays step-by-step agent decisions to diagnose failures.
- **Visual Graph UI:** Displays execution flows as directed acyclic graphs (DAGs) representing tool calls and decisions.
- **Divergence Lineage:** Identifies when an agent diverged from an expected path, highlighting the causing state or prompt context.

## Relationship to Kernel

- **WatchLLM Replay (Observability):** Consumes logs and execution events written by the Kernel or Runtime.
- **WatchLLM Kernel (Enforcement):** Operates inline to enforce policies and block saves, writing execution and violation events to local logs for Replay ingestion.

## Non-goals

- **Security Enforcement:** `replay` is a diagnostics tool; it does not block disk writes or execute inline code controls.
- **Agent Orchestration:** `replay` does not execute or launch agents itself; it only visualizes their execution logs.

## Installation

```bash
npm install
```

## Usage

Start the full Replay dashboard:

```bash
npm start
```

This launches:

- backend API on `http://localhost:3001`
- frontend dashboard on `http://localhost:5173`

For separate development terminals:

```bash
npm run dev:backend
npm run dev:frontend
```

Run tests:

```bash
npm test
```

Build the frontend:

```bash
npm run build:frontend
```

## Links

- [WatchLLM Organization](https://github.com/WatchLLM)
- [Central Documentation](https://github.com/WatchLLM/docs)
- [watchllm.dev](https://watchllm.dev)
