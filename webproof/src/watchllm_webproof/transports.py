"""HTTP transports with explicit sync/async ownership and persistence semantics."""

from __future__ import annotations

from typing import Any

import httpx
import requests

from .exceptions import AgentClosedError


class SyncTransport:
    """Manage requests sessions without consuming streamed responses.

    Persistent mode reuses one session (and therefore cookies). Non-persistent
    mode creates and closes one session per request; streamed responses retain
    their request session until the caller closes the response.
    """

    def __init__(self, *, persistent: bool, session: requests.Session | None = None) -> None:
        if session is not None and not persistent:
            raise ValueError("a custom session requires session_persistence=true")
        self.persistent = persistent
        self._session = session
        self._owns_session = session is None
        self.closed = False

    @property
    def session(self) -> requests.Session:
        if not self.persistent:
            raise RuntimeError("session is unavailable when session_persistence=false")
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        if self.closed:
            raise AgentClosedError("agent's synchronous transport is closed")
        if self.persistent:
            return self.session.request(method, url, **kwargs)
        session = requests.Session()
        try:
            response = session.request(method, url, **kwargs)
        except BaseException:
            session.close()
            raise
        if kwargs.get("stream", False):
            original_close = response.close
            closed = False

            def close() -> None:
                nonlocal closed
                if not closed:
                    closed = True
                    try:
                        original_close()
                    finally:
                        session.close()

            response.close = close  # type: ignore[method-assign]
        else:
            session.close()
        return response

    def close(self) -> None:
        if not self.closed and self._owns_session and self._session is not None:
            self._session.close()
        self.closed = True


class AsyncTransport:
    """Manage httpx clients without consuming streamed responses."""

    def __init__(self, *, persistent: bool, client: httpx.AsyncClient | None = None) -> None:
        if client is not None and not persistent:
            raise ValueError("a custom async_client requires session_persistence=true")
        self.persistent = persistent
        self._client = client
        self._owns_client = client is None
        self.closed = False

    @property
    def client(self) -> httpx.AsyncClient:
        if not self.persistent:
            raise RuntimeError("async_client is unavailable when session_persistence=false")
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        if self.closed:
            raise AgentClosedError("agent's asynchronous transport is closed")
        stream = kwargs.pop("stream", False)
        client = self.client if self.persistent else httpx.AsyncClient()
        try:
            if stream:
                auth = kwargs.pop("auth", httpx.USE_CLIENT_DEFAULT)
                follow_redirects = kwargs.pop("follow_redirects", httpx.USE_CLIENT_DEFAULT)
                request = client.build_request(method, url, **kwargs)
                response = await client.send(request, stream=True, auth=auth, follow_redirects=follow_redirects)
            else:
                response = await client.request(method, url, **kwargs)
        except BaseException:
            if not self.persistent:
                await client.aclose()
            raise
        if not self.persistent:
            if stream:
                original_aclose = response.aclose
                closed = False

                async def aclose() -> None:
                    nonlocal closed
                    if not closed:
                        closed = True
                        try:
                            await original_aclose()
                        finally:
                            await client.aclose()

                response.aclose = aclose  # type: ignore[method-assign]
            else:
                await client.aclose()
        return response

    async def close(self) -> None:
        if not self.closed and self._owns_client and self._client is not None:
            await self._client.aclose()
        self.closed = True
