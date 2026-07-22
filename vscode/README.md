# WatchLLM VS Code Extension

*VS Code extension for save-path governance interception and diagnostics.*

## Current status

Early design & specification phase. Subsystem boundary defined; codebase scaffolded.

## Overview

The `vscode` repository contains the thin editor host extension for WatchLLM. It intercepts save commands before changes write to disk, evaluates them via the local WatchLLM Kernel CLI, blocks the save if any rule fails, and highlights violations using inline diagnostics.

The extension is not the kernel. It serves purely as the write-path interceptor and UI bridge.

## Core Features

- **Save-Path Interception:** Uses the `onWillSaveTextDocument` event to halt disk writes during rule evaluations.
- **Subprocess Bridge:** Spawns the local `watchllm-kernel` CLI, piping the document buffer via stdin to avoid local file sync delays.
- **Inline Diagnostics:** Renders syntax node annotations and compiler-like warning markers on blocked lines.
- **Shadow Mode Telemetry:** Non-blocking audits that log violations locally/remotely without interrupting development velocity.

## Relationship to Kernel

- **VS Code Extension (Host):** Intercepts write events, captures buffers, and displays error messages.
- **WatchLLM Kernel (Engine):** Evaluates AST queries, processes security rules, and issues allow/block verdicts.

## Non-goals

- **AST Parsing:** The extension does not compile or parse AST nodes itself; it leaves parsing to the Python/Wasm Kernel.
- **Rule Verification:** Rule evaluations and policy engines are defined and executed by the Kernel, not the extension.

## Installation

The extension is not currently published to the VS Code Marketplace. Compile it locally:

```bash
npm install
npm run compile
```

## Usage

Enable the extension, and it will automatically apply rules configured in your `.watchllm` settings or policy file on every save.

## Links

- [WatchLLM Organization](https://github.com/WatchLLM)
- [Central Documentation](https://github.com/WatchLLM/docs)
- [watchllm.dev](https://watchllm.dev)
