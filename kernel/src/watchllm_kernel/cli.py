import argparse
import dataclasses
import enum
import json
import sys
from pathlib import Path
from typing import Any

from watchllm_kernel.engine import ENFORCE_MODE, SHADOW_MODE, evaluate_source
from watchllm_kernel.models import Decision
from watchllm_kernel.reporting import format_human_report, write_block_log
from watchllm_kernel.rules.auth_flow import AuthFlowRule
from watchllm_kernel.rules.boundary import BoundaryRule
from watchllm_kernel.rules.forbidden_imports import ForbiddenImportRule
from watchllm_kernel.config_loader import load_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_jsonable(obj: Any) -> Any:
    """Convert dataclasses and enums to JSON‑serialisable primitives."""
    if dataclasses.is_dataclass(obj):
        return {f.name: _to_jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, enum.Enum):
        return obj.value
    if isinstance(obj, list):
        return [_to_jsonable(item) for item in obj]
    return obj


def build_default_rules(config: dict | None = None):
    """Return the default rule set for the kernel CLI, applying overrides from config.
    """
    config = config or {}
    rules = []

    try:
        from watchllm_kernel.rules.secrets import SecretLiteralRule
    except ModuleNotFoundError:
        SecretLiteralRule = None

    if SecretLiteralRule is not None:
        secrets_cfg = config.get("rules", {}).get("secrets", {})
        if secrets_cfg.get("enabled", True):
            rules.append(SecretLiteralRule())

    # Build Forbidden Import Rule
    fi_cfg = config.get("rules", {}).get("forbidden_imports", {})
    if fi_cfg.get("enabled", True):
        rules.append(ForbiddenImportRule(
            forbidden_modules=fi_cfg.get("modules"),
            forbidden_prefixes=fi_cfg.get("forbidden_prefixes"),
            allowed_relative_prefixes=fi_cfg.get("allowed_relative_prefixes")
        ))

    # Build Boundary Rule
    boundary_cfg = config.get("rules", {}).get("boundary", {})
    if boundary_cfg.get("enabled", True):
        rules.append(BoundaryRule(
            boundary_map=boundary_cfg.get("map")
        ))

    # Build Auth Flow Rule
    auth_cfg = config.get("rules", {}).get("auth_flow", {})
    if auth_cfg.get("enabled", True):
        rules.append(AuthFlowRule())

    return rules


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="watchllm-kernel",
        description="Deterministic local write-path governance kernel for autonomous coding agents.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    sub = parser.add_subparsers(dest="command", help="sub-command")

    # check
    check_parser = sub.add_parser("check", help="Check source against rules")
    check_parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read source from stdin instead of a file path",
    )
    check_parser.add_argument(
        "--filepath",
        default=None,
        help="Path to source file (ignored when --stdin is used)",
    )
    check_parser.add_argument(
        "--language",
        choices=["js", "ts"],
        default=None,
        help="Language identifier (js or ts). Inferred from file extension when omitted.",
    )
    check_parser.add_argument(
        "--mode",
        choices=[ENFORCE_MODE, SHADOW_MODE],
        default=ENFORCE_MODE,
        help="Evaluation mode (default: enforce)",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    return parser


# ---------------------------------------------------------------------------
# Language resolution
# ---------------------------------------------------------------------------

_LANGUAGE_SHORT_MAP = {
    "js": "javascript",
    "ts": "typescript",
}


def _resolve_language(language: str | None, file_path: str | None) -> str | None:
    if language and language in _LANGUAGE_SHORT_MAP:
        return _LANGUAGE_SHORT_MAP[language]
    if language:
        return language
    if file_path is None:
        return None
    suffix = Path(file_path).suffix.lower()
    if suffix in (".ts", ".tsx"):
        return "typescript"
    if suffix in (".js", ".jsx", ".mjs", ".cjs"):
        return "javascript"
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)

    if args.command != "check":
        parser.print_help()
        return 0

    # --- read source ---
    if args.stdin:
        source = sys.stdin.read()
        file_path = None
    else:
        if args.filepath is None:
            print("Error: either --stdin or --filepath is required", file=sys.stderr)
            return 2
        file_path = args.filepath
        try:
            source = Path(file_path).read_text(encoding="utf-8")
        except Exception as exc:
            print(f"Error reading file {file_path}: {exc}", file=sys.stderr)
            return 2

    language = _resolve_language(args.language, file_path)

    # --- load config ---
    start_path = str(Path(file_path).parent) if file_path else "."
    config = load_config(start_path=start_path)

    # --- evaluate ---
    rules = build_default_rules(config=config)
    result = evaluate_source(
        source,
        file_path=file_path,
        language=language,
        rules=rules,
        mode=args.mode,
    )

    # --- local blocked-event logging ---
    write_block_log(result)

    # --- output ---
    if args.json:
        payload = _to_jsonable(result)
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(format_human_report(result))

    # exit code
    if result.decision == Decision.BLOCK:
        return 1
    return 0
