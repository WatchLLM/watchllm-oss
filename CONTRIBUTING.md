# WatchLLM OSS Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Open a pull request

## Development Setup

### Kernel (Python)

```bash
cd kernel
python -m pip install -e .
python -m pip install pytest
pytest
```

### Schemas

```bash
cd schemas
# JSON Schema files — validate with any JSON Schema validator
npx ajv validate -s schemas/v1/violation.json -d examples/violation.json
```

### VS Code Extension

```bash
cd vscode
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

## Commit Conventions

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `test:` — adding or updating tests
- `refactor:` — code change that neither fixes a bug nor adds a feature

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
