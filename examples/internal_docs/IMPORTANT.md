# WatchLLM Examples

## 0) Purpose

This repository holds curated demonstrations and integration examples for the WatchLLM ecosystem. It provides sample codebases that act as integration test targets for the Kernel and learning resources for users.

---

## 1) Scope

### In scope
* Dummy application code demonstrating compliance with rules.
* Dummy application code demonstrating architectural violations.
* Hardcoded secrets examples for scanner testing.
* Example `watchllm.yml` configurations for the scenarios.

### Out of scope
* Core WatchLLM rule development.
* Executable frameworks for checking rules.

---

## 2) Architecture Rules

### 2.1 The Isolation Rule
Each scenario must be fully self-contained in its own directory under `scenarios/`.

### 2.2 The Binary Outcomes Rule
Every scenario directory must clearly document whether it is intended to PASS validation (safe) or FAIL validation (unsafe).

---

## 3) Implementation Order

1. **Skeleton**: Set up the `scenarios/` structure.
2. **Secrets Scenario**: Create a failing scenario with leaked keys and a passing scenario with `.env` loading.
3. **Boundaries Scenario**: Create a failing scenario importing from isolated domains.
4. **Auth Flow Scenario**: Create a failing scenario demonstrating missing auth checks on mutations.

---

## 4) Definition of Done
* `watchllm-kernel check` run against the `scenarios/` folder perfectly triggers all expected PASS and FAIL events.
