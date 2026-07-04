# Changelog

## [0.1.0] — 2026-07-04

### Added
- **Kernel**: Deterministic Python governance kernel with Tree-sitter AST parsing
  - Auth-flow rule: validates authentication before database mutations
  - Boundary rule: enforces import boundary contracts between layers
  - Secrets rule: detects hardcoded credentials (API keys, tokens)
  - Forbidden imports rule: blocks dangerous module imports
  - CLI interface: `watchllm-kernel scan <path>`
  - Blocked-event reporting
- **Schemas**: Canonical JSON Schema contracts for events, violations, and decisions
- **VS Code Extension**: Save-path governance with inline diagnostics
- **Examples**: Scenario fixtures for auth-flow, boundary, and secrets rules
- **CI/CD**: GitHub Actions for pytest, TypeScript checks, and PyPI publishing
- **Community**: Issue templates, security policy, contributing guide