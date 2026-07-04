# WatchLLM Schemas

## 0) Purpose

This repository contains the central specifications and interface contracts (JSON Schemas) for the WatchLLM ecosystem. It ensures all components (Kernel, Runtime, VSCode, Klyd, Replay) speak the exact same data structures.

---

## 1) Scope

### In scope
* `event.json` (Trace logs and standard telemetry)
* `violation.json` (Code boundary and security leak block structures)
* `decision.json` (ALLOW/BLOCK/INCONCLUSIVE outcomes)
* Versioning structure (`v1/`, `v2/`, etc.)

### Out of scope
* Executable validators or code generation. This repo is purely static schemas.

---

## 2) Architecture Rules

### 2.1 The Cross-Language Contract Rule
All schemas must be strict Draft-07 compatible JSON Schema. They must be parsable by both Python (for the Kernel) and Rust (for the Runtime) without relying on language-specific extensions.

### 2.2 Semantic Versioning
Schemas may never introduce breaking changes within the same major version folder (e.g., `v1/`). A breaking change requires a new folder (e.g., `v2/`).

---

## 3) Implementation Order

1. **Skeleton**: Create the `schemas/v1/` directory structure.
2. **Event Schema**: Define `event.json` for trace logs.
3. **Violation Schema**: Define `violation.json` for Kernel blocks.
4. **Decision Schema**: Define `decision.json` for the final gate result.

---

## 4) Definition of Done
* All three schemas exist in `schemas/v1/` and pass a standard JSON Schema linter.
