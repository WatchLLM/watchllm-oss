"""Command-line interface for watchllm-webproof."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

import requests

from .agent import VerifiableAgent
from .exceptions import WebProofError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="watchllm")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify-url", help="request an HTTP(S) URL and print a local proof summary")
    verify.add_argument("url")
    verify.add_argument("--config", metavar="FILE", help="optional JSON or YAML configuration file")
    verify.add_argument("--timeout", type=float, default=30.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "verify-url":
        try:
            with VerifiableAgent(config_path=args.config) as agent:
                agent.get(args.url, timeout=args.timeout)
                print(json.dumps(agent.proof(), sort_keys=True))
            return 0
        except (WebProofError, requests.RequestException, OSError) as exc:
            print(f"watchllm: {exc}", file=sys.stderr)
            return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
