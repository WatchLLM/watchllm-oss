# WatchLLM VS Code Extension

## 0) Purpose

This document defines the **VS Code host integration** for WatchLLM (Expansion A). Its sole purpose is to connect the VS Code save event (`onWillSaveTextDocument`) to the local `watchllm_kernel`.

This extension does not parse code, evaluate rules, or manage policies. It blindly trusts the kernel and surfaces the kernel's decisions in the editor.

The design goal is simple:
> If the kernel blocks a file, the extension blocks the save and shows the user why.

---

## 1) Scope

### In scope

* Intercepting `onWillSaveTextDocument` synchronously.
* Invoking the local Python `watchllm_kernel` via subprocess.
* Passing unsaved document text via `stdin`.
* Parsing the JSON stdout of the kernel.
* Blocking the save if the kernel exits with code `1`.
* Surfacing kernel violations as VS Code `Diagnostic` objects (red squiggles) and error messages.
* Simple configuration for Python path, kernel path, and enforce/shadow mode.

### Out of scope

* AST parsing or rule evaluation.
* Bundling the Python runtime or kernel inside the extension (user must have kernel installed locally).
* Cloud telemetry, authentication, or remote policy sync.
* Diagnostics for unsaved keystrokes (only runs on save).

---

## 2) Architecture rules

### 2.1 No duplicate enforcement rule
The extension must never duplicate the logic of the kernel. It is a dumb pipe. All enforcement logic lives in `watchllm/kernel`.

### 2.2 Synchronous UX rule
Save interception must pause the save using `waitUntil`. The user must not be able to bypass the kernel by saving too fast.

### 2.3 Graceful Degradation rule
If the kernel subprocess fails to spawn, crashes, or returns an unexpected error (exit code 2), the extension must **fail-open** by default (allow the save) but show a prominent error message to the user. The goal is to not hold the user's code hostage if the local infrastructure breaks.

### 2.4 Minimal Config rule
Do not over-configure. We need:
* `watchllm.pythonPath` (default: 'python')
* `watchllm.kernelPath` (default: '-m watchllm_kernel evaluate')
* `watchllm.mode` (default: 'enforce', options: 'enforce', 'shadow')

---

## 3) Extension implementation order

1. Repo skeleton.
2. Kernel configuration layer.
3. Subprocess executor for the kernel.
4. Save interception hook.
5. Violation mapping and Diagnostics UI.
6. End-to-end integration testing.
7. Packaging and release prep.

---

## 4) Definition of done

* Extension activates on JS/TS files.
* Extension successfully calls the kernel on save.
* Exit code 1 blocks the save and shows diagnostics.
* Exit code 0 allows the save immediately.
* Exit code 2 allows the save but shows an error notification.
* A valid `.vsix` file is generated.
