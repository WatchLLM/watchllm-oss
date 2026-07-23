"""Synchronous and asynchronous WebProof HTTP agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
import requests

from .accumulator import LocalMerkleAccumulator
from .config import RouteConfig, WebProofConfig, load_config, normalize_hostname
from .exceptions import UnsupportedSchemeError
from .transports import AsyncTransport, SyncTransport


class VerifiableAgent:
    """Record privacy-minimized HTTP outcomes and produce a local proof stub.

    The result is not a TLSNotary/Reclaim proof and is not an attestation of
    remote data. Configured prover modes are declarative routing metadata only.
    """

    def __init__(
        self,
        config: Mapping[str, Any] | WebProofConfig | None = None,
        *,
        config_path: str | Path | None = None,
        session: requests.Session | None = None,
        async_client: httpx.AsyncClient | None = None,
        session_id: str | None = None,
    ) -> None:
        if config is not None and config_path is not None:
            raise ValueError("config and config_path are mutually exclusive")
        source = config_path if config_path is not None else config
        self.config = load_config(source)
        self.session_id = session_id or str(uuid4())
        self._accumulator = LocalMerkleAccumulator()
        try:
            self._sync_transport = SyncTransport(persistent=self.config.session_persistence, session=session)
            self._async_transport = AsyncTransport(persistent=self.config.session_persistence, client=async_client)
        except ValueError as exc:
            raise ValueError(f"invalid transport configuration: {exc}") from exc

    def __enter__(self) -> "VerifiableAgent":
        if self._sync_transport.closed:
            from .exceptions import AgentClosedError
            raise AgentClosedError("agent's synchronous transport is closed")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    async def __aenter__(self) -> "VerifiableAgent":
        if self._async_transport.closed:
            from .exceptions import AgentClosedError
            raise AgentClosedError("agent's asynchronous transport is closed")
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.aclose()

    def close(self) -> None:
        self._sync_transport.close()

    async def aclose(self) -> None:
        await self._async_transport.close()

    @property
    def session(self) -> requests.Session:
        """Persistent sync session; unavailable when session persistence is disabled."""
        return self._sync_transport.session

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Persistent async client; unavailable when session persistence is disabled."""
        return self._async_transport.client

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        target = self._target(url)
        try:
            response = self._sync_transport.request(method, url, **kwargs)
        except requests.RequestException as exc:
            self._record(method, target, None, type(exc).__name__)
            raise
        self._record(method, target, response.status_code, None)
        return response

    async def arequest(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        target = self._target(url)
        try:
            response = await self._async_transport.request(method, url, **kwargs)
        except httpx.HTTPError as exc:
            self._record(method, target, None, type(exc).__name__)
            raise
        self._record(method, target, response.status_code, None)
        return response

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", url, **kwargs)

    async def aget(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.arequest("GET", url, **kwargs)

    async def apost(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.arequest("POST", url, **kwargs)

    def proof(self) -> dict[str, Any]:
        return self._accumulator.proof(self.session_id)

    @property
    def records(self) -> tuple[Mapping[str, Any], ...]:
        """Immutable snapshots containing no headers, query strings, cookies, or bodies."""
        return self._accumulator.records

    def route_for(self, hostname: str) -> RouteConfig | None:
        normalized = normalize_hostname(hostname)
        candidates = [
            route for route in self.config.routes
            if route.domain == normalized or normalized.endswith("." + route.domain)
        ]
        return max(candidates, key=lambda route: len(route.domain), default=None)

    def _target(self, url: str) -> dict[str, Any]:
        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"}:
            shown = parsed.scheme or "(missing)"
            raise UnsupportedSchemeError(
                f"unsupported URL scheme {shown!r}; watchllm-webproof supports HTTP and HTTPS only"
            )
        if parsed.username is not None or parsed.password is not None:
            raise UnsupportedSchemeError("credentials in URLs are not supported")
        if parsed.hostname is None:
            raise UnsupportedSchemeError("HTTP(S) URL must include a hostname")
        hostname = normalize_hostname(parsed.hostname)
        route = self.route_for(hostname)
        try:
            port = parsed.port
        except ValueError as exc:
            raise UnsupportedSchemeError(f"invalid URL port: {exc}") from exc
        return {
            "scheme": scheme,
            "domain": hostname,
            "port": port or (80 if scheme == "http" else 443),
            "path": parsed.path or "/",
            "prover_mode": route.prover_mode if route else None,
            "sensitivity": route.sensitivity if route else None,
            "session_ttl": route.session_ttl if route else None,
        }

    def _record(
        self,
        method: str,
        target: Mapping[str, Any],
        status_code: int | None,
        error_type: str | None,
    ) -> None:
        self._accumulator.record({
            "method": method.upper(),
            **target,
            "status_code": status_code,
            "error_type": error_type,
        })
