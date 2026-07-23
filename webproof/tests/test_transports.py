"""Focused transport ownership and unconsumed-stream lifecycle tests."""

import httpx
import pytest
import requests
import responses

from watchllm_webproof import VerifiableAgent


@responses.activate
def test_sync_stream_is_not_consumed():
    responses.add(responses.GET, "https://example.com/data", body=b"payload")
    with VerifiableAgent() as agent:
        response = agent.get("https://example.com/data", stream=True)
        assert response._content is False
        response.close()


@responses.activate
def test_sync_nonpersistent_stream_owns_session_until_response_close(monkeypatch):
    closed = []
    original = requests.Session.close

    def close(session):
        closed.append(session)
        original(session)

    monkeypatch.setattr(requests.Session, "close", close)
    responses.add(responses.GET, "https://example.com/data", body=b"payload")
    agent = VerifiableAgent({"session_persistence": False})
    response = agent.get("https://example.com/data", stream=True)
    assert not closed
    response.close()
    assert len(closed) == 1
    response.close()
    assert len(closed) == 1
    agent.close()


def test_caller_owned_sync_session_is_not_closed_and_requires_persistence():
    session = requests.Session()
    agent = VerifiableAgent(session=session)
    agent.close()
    assert session.headers is not None
    with pytest.raises(ValueError, match="requires session_persistence=true"):
        VerifiableAgent({"session_persistence": False}, session=session)
    session.close()


@pytest.mark.asyncio
async def test_async_nonpersistent_stream_owns_client_until_response_close(monkeypatch):
    original = httpx.AsyncClient
    clients = []

    class Client(original):
        def __init__(self, *args, **kwargs):
            class Stream(httpx.AsyncByteStream):
                async def __aiter__(self):
                    yield b"payload"

            kwargs["transport"] = httpx.MockTransport(
                lambda request: httpx.Response(200, stream=Stream())
            )
            super().__init__(*args, **kwargs)
            clients.append(self)

    monkeypatch.setattr(httpx, "AsyncClient", Client)
    agent = VerifiableAgent({"session_persistence": False})
    response = await agent.aget("https://example.com/data", stream=True)
    assert not response.is_stream_consumed
    assert not clients[0].is_closed
    await response.aclose()
    assert clients[0].is_closed
    await response.aclose()
    await agent.aclose()


@pytest.mark.asyncio
async def test_caller_owned_async_client_is_not_closed_and_requires_persistence():
    client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    agent = VerifiableAgent(async_client=client)
    await agent.aclose()
    assert not client.is_closed
    with pytest.raises(ValueError, match="requires session_persistence=true"):
        VerifiableAgent({"session_persistence": False}, async_client=client)
    await client.aclose()
