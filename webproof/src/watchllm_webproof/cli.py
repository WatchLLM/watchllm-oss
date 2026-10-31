"""Command-line interface for watchllm-webproof."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Sequence

import requests

from .agent import VerifiableAgent
from .cloud import CloudClient, build_edge_envelope
from .exceptions import WebProofError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="watchllm")
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify-url", help="request an HTTP(S) URL and print a local proof summary")
    verify.add_argument("url")
    verify.add_argument("--config", metavar="FILE", help="optional JSON or YAML configuration file")
    verify.add_argument("--timeout", type=float, default=30.0)
    cloud = verify.add_argument_group("explicit cloud submission")
    cloud.add_argument("--submit", metavar="HTTPS_URL", help="opt in to submit the local commitment to WebProof Edge")
    cloud.add_argument("--api-key-env", default="WATCHLLM_API_KEY", metavar="NAME", help="environment variable containing key_id.secret (default: WATCHLLM_API_KEY)")
    cloud.add_argument("--response-hash", metavar="SHA256", help="required unbound response hash metadata when --submit is used")
    cloud.add_argument("--chain", choices=("base-sepolia", "base-mainnet"))
    cloud.add_argument("--poll-timeout", type=float, default=0.0, metavar="SECONDS", help="poll after submission for at most this duration")

    status = subparsers.add_parser("cloud-status", help="explicitly fetch a WebProof Edge verification status")
    status.add_argument("verification_id")
    status.add_argument("--endpoint", required=True, metavar="HTTPS_URL")
    status.add_argument("--api-key-env", default="WATCHLLM_API_KEY", metavar="NAME")
    status.add_argument("--timeout", type=float, default=30.0)
    status.add_argument("--poll-timeout", type=float, default=0.0, metavar="SECONDS")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "verify-url":
            if args.poll_timeout < 0:
                raise ValueError("--poll-timeout cannot be negative")
            if args.submit is None and (args.response_hash is not None or args.chain is not None or args.poll_timeout > 0):
                raise ValueError("cloud options require --submit")
            if args.submit is not None and args.response_hash is None:
                raise ValueError("--response-hash is required with --submit")
            with VerifiableAgent(config_path=args.config) as agent:
                agent.get(args.url, timeout=args.timeout)
                proof = agent.proof()
                if args.submit is None:
                    print(json.dumps(proof, sort_keys=True))
                    return 0
                envelope = build_edge_envelope(
                    agent.records,
                    proof,
                    leaf_index=len(agent.records) - 1,
                    response_hash=args.response_hash,
                    observed_at=int(time.time() * 1000),
                    chain=args.chain,
                )
                with _cloud_client(args.submit, args.api_key_env, args.timeout) as client:
                    result = client.submit(envelope)
                    if args.poll_timeout > 0:
                        result = client.poll(result.verification_id, timeout=args.poll_timeout)
                print(json.dumps(dict(result.data), sort_keys=True))
                return 0
        if args.command == "cloud-status":
            if args.poll_timeout < 0:
                raise ValueError("--poll-timeout cannot be negative")
            with _cloud_client(args.endpoint, args.api_key_env, args.timeout) as client:
                result = client.status(args.verification_id)
                if args.poll_timeout > 0 and result.status not in {"anchored", "failed"}:
                    result = client.poll(args.verification_id, timeout=args.poll_timeout)
            print(json.dumps(dict(result.data), sort_keys=True))
            return 0
    except (WebProofError, requests.RequestException, OSError, ValueError) as exc:
        print(f"watchllm: {exc}", file=sys.stderr)
        return 1
    return 2


def _cloud_client(endpoint: str, env_name: str, timeout: float) -> CloudClient:
    if not env_name or "=" in env_name:
        raise ValueError("API key environment variable name is invalid")
    api_key = os.environ.get(env_name)
    if api_key is None:
        raise ValueError(f"API key environment variable {env_name!r} is not set")
    return CloudClient(endpoint, api_key, timeout=timeout)


if __name__ == "__main__":
    raise SystemExit(main())
