⇒ WatchLLM VS Code Extension — 7-Day Prompt Pack

Copy **one full day block** below into your agent session. Each block uses the same template; only task, gate, and scope placeholders are filled from `internal_docs/IMPORTANT.md`.

**Repo:** `watchllm/vscode` (local: `d:\watchllm\vscode`)

---

⇒ Day 01 — Task 01: Build the repo skeleton

⇒ Task Instructions

Today's task:
**VSCODE Task 01 — Build the repo skeleton**

Create the minimal extension layout:

- `package.json` with correct activation events (`onLanguage:javascript`, `onLanguage:typescript`)
- `tsconfig.json`
- `src/extension.ts` stub
- Minimal `.vscode/launch.json` for debugging

Today's gate:
- `npm run compile` succeeds.
- Extension can be launched in the Extension Development Host without crashing.

> Scope Constraints

Only work on:
- Repository skeleton and package configuration (Task 01 only)
- Scaffolding the extension structure

Do NOT:
- write the save hook logic
- add unnecessary dependencies
- invoke subprocesses yet

> Required Outputs

You must:
- implement the task narrowly
- write/update tests if applicable
- update internal_docs/README.md if architecture changes
- explain architectural decisions
- explain potential failure points

> Validation Requirements

Before finishing:
- verify gate behavior
- ensure deterministic output

---

⇒ Day 02 — Task 02: Kernel configuration layer

⇒ Task Instructions

Today's task:
**VSCODE Task 02 — Kernel configuration layer**

Implement reading VS Code settings:

- Expose settings in `package.json` (`watchllm.pythonPath`, `watchllm.kernelPath`, `watchllm.mode`).
- Read these settings securely in `extension.ts` or a `config.ts` module.
- Provide sensible defaults.

Today's gate:
- Settings show up in the VS Code Settings UI under a "WatchLLM" category.
- Changing a setting in `settings.json` is accurately reflected in the extension's runtime config object.

> Scope Constraints

Only work on:
- Configuration parsing and schema (Task 02 only)

Do NOT:
- write the save hook logic
- invoke subprocesses yet

> Required Outputs

You must:
- implement the task narrowly
- update internal_docs/README.md if architecture changes
- explain architectural decisions

> Validation Requirements

Before finishing:
- verify gate behavior

---

⇒ Day 03 — Task 03: Kernel subprocess executor

⇒ Task Instructions

Today's task:
**VSCODE Task 03 — Kernel subprocess executor**

Implement a robust wrapper around `child_process.execFile` or `spawn`:

- Pass unsaved document text to the subprocess `stdin`.
- Pass arguments (`--stdin`, `--json`, `--language`, `--mode`) securely.
- Parse the JSON stdout.
- Handle timeout/crash edge cases properly.

Today's gate:
- Unit/integration tests can successfully invoke a dummy script returning 0/1/2 and parse the stdout as JSON.
- Process timeouts are enforced.

> Scope Constraints

Only work on:
- Subprocess execution and parsing (Task 03 only)

Do NOT:
- bind to the editor save events yet
- map to editor UI elements

> Required Outputs

You must:
- implement the task narrowly
- write tests for the subprocess execution
- explain architectural decisions

> Validation Requirements

Before finishing:
- run tests
- verify gate behavior

---

⇒ Day 04 — Task 04: Save interception hook

⇒ Task Instructions

Today's task:
**VSCODE Task 04 — Save interception hook**

Bind the editor to the subprocess logic:

- Subscribe to `workspace.onWillSaveTextDocument`.
- Use `event.waitUntil` with a Promise that resolves when the kernel check finishes.
- Block the save (or throw/cancel) if the kernel returns exit code 1.

Today's gate:
- A dummy kernel script returning exit code 1 successfully blocks the file save in the editor.
- Returning 0 successfully allows it.

> Scope Constraints

Only work on:
- Save interception and promise chaining (Task 04 only)

Do NOT:
- add diagnostic squiggles or complex UI yet

> Required Outputs

You must:
- implement the task narrowly
- write tests for the hook logic
- explain architectural decisions

> Validation Requirements

Before finishing:
- verify gate behavior

---

⇒ Day 05 — Task 05: Violation mapping & diagnostics

⇒ Task Instructions

Today's task:
**VSCODE Task 05 — Violation mapping & diagnostics**

Make the kernel's decision visible:

- Translate the Kernel's JSON violation schema into VS Code `Diagnostic` objects.
- Create a `DiagnosticCollection` to show red squiggles at the exact line/column of the violation.
- Add a `window.showErrorMessage` popup describing the block.

Today's gate:
- Kernel JSON cleanly maps to editor warnings in the Problems panel.
- Clear error notification is presented to the user.

> Scope Constraints

Only work on:
- UI, Diagnostics, and user feedback (Task 05 only)

Do NOT:
- modify the kernel contract

> Required Outputs

You must:
- implement the task narrowly
- explain architectural decisions

> Validation Requirements

Before finishing:
- verify gate behavior

---

⇒ Day 06 — Task 06: End-to-end integration testing

⇒ Task Instructions

Today's task:
**VSCODE Task 06 — End-to-end integration testing**

Combine all pieces with the real watchllm kernel:

- Ensure the path resolves to the actual local kernel.
- Run a save event with a hardcoded secret in a test file.
- Handle graceful degradation (if the kernel is missing, fail-open but warn the user).

Today's gate:
- Saving a TS file with a known hardcoded secret actually blocks the save and shows a squiggle via the real python kernel.
- Graceful degradation works when kernel is uninstalled.

> Scope Constraints

Only work on:
- End-to-end testing and graceful degradation logic (Task 06 only)

Do NOT:
- rewrite core logic unless bug fixing is required

> Required Outputs

You must:
- implement the task narrowly
- verify all edge cases (missing python, missing kernel, malformed JSON)

> Validation Requirements

Before finishing:
- run manual or automated e2e tests
- verify gate behavior

---

⇒ Day 07 — Task 07: Packaging & Release prep

⇒ Task Instructions

Today's task:
**VSCODE Task 07 — Packaging & Release prep**

Bundle the extension:

- Configure `esbuild` or `webpack` for fast, small bundling.
- Update `.vscodeignore` to exclude source files.
- Configure `vsce package`.

Today's gate:
- `vsce package` creates a `.vsix` file.
- The `.vsix` can be successfully installed into VS Code locally.

> Scope Constraints

Only work on:
- Build tools, bundlers, and package metadata (Task 07 only)

Do NOT:
- add new extension features

> Required Outputs

You must:
- implement the task narrowly
- produce the `.vsix`

> Validation Requirements

Before finishing:
- install the extension from the vsix
- verify gate behavior
