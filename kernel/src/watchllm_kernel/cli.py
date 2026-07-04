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


def build_default_rules():
    """Return the default rule set for the kernel CLI.

    The secret‑literal rule is optional; if the module is not available it is
    silently skipped.
    """
    rules = []

    try:
        from watchllm_kernel.rules.secrets import SecretLiteralRule
    except ModuleNotFoundError:
        SecretLiteralRule = None

    if SecretLiteralRule is not None:
        rules.append(SecretLiteralRule())

    rules.extend([
        ForbiddenImportRule(),
        BoundaryRule(),
        AuthFlowRule(),
    ])
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

    # evaluate
    eval_parser = sub.add_parser("evaluate", help="Evaluate source against rules")
    eval_parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read source from stdin instead of a file path",
    )
    eval_parser.add_argument(
        "file",
        nargs="?",
        help="Path to source file (ignored when --stdin is used)",
    )
    eval_parser.add_argument(
        "--language",
        default=None,
        help="Language identifier (e.g. javascript, typescript). Inferred from file extension when omitted.",
    )
    eval_parser.add_argument(
        "--mode",
        choices=[ENFORCE_MODE, SHADOW_MODE],
        default=ENFORCE_MODE,
        help="Evaluation mode (default: enforce)",
    )
    eval_parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    return parser


# ---------------------------------------------------------------------------
# Language inference
# ---------------------------------------------------------------------------


def _infer_language(file_path: str | None) -> str | None:
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

    if args.command != "evaluate":
        parser.print_help()
        return 0

    # --- read source ---
    if args.stdin:
        source = sys.stdin.read()
        file_path = None
    else:
        if args.file is None:
            print("Error: either --stdin or a file path is required", file=sys.stderr)
            return 2
        file_path = args.file
        try:
            source = Path(file_path).read_text(encoding="utf-8")
        except Exception as exc:
            print(f"Error reading file {file_path}: {exc}", file=sys.stderr)
            return 2

    language = args.language or _infer_language(file_path)

    # --- evaluate ---
    rules = build_default_rules()
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
