import httpx
import pytest

from watchllm_webproof import AgentClosedError, VerifiableAgent


@pytest.mark.asyncio
async def test_aget_apost_arequest_cookie_persistence_and_streaming(httpx_mock):
    httpx_mock.add_response(method="GET", url="https://example.com/one", status_code=200, headers={"set-cookie": "sid=secret; Path=/"})
    httpx_mock.add_response(method="POST", url="https://example.com/two", status_code=201, content=b"payload")
    httpx_mock.add_response(method="DELETE", url="https://example.com/three", status_code=204)
    async with VerifiableAgent() as agent:
        await agent.aget("https://example.com/one")
        second = await agent.apost("https://example.com/two", json={"value": 1}, stream=True)
        assert not second.is_stream_consumed
        assert agent.async_client.cookies["sid"] == "secret"
        await second.aclose()
        assert (await agent.arequest("DELETE", "https://example.com/three")).status_code == 204
        assert [record["method"] for record in agent.records] == ["GET", "POST", "DELETE"]
    with pytest.raises(AgentClosedError):
        await agent.aget("https://example.com/four")


@pytest.mark.asyncio
async def test_async_nonpersistent_does_not_persist_cookies():
    seen = []

    def handler(request):
        seen.append(request)
        if len(seen) == 1:
            return httpx.Response(200, headers={"set-cookie": "sid=secret; Path=/"})
        return httpx.Response(200)

    # Patch the per-request client factory while preserving the transport under test.
    original = httpx.AsyncClient
    clients = []

    class Client(original):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)
            clients.append(self)

    httpx.AsyncClient = Client
    try:
        async with VerifiableAgent({"session_persistence": False}) as agent:
            await agent.aget("https://example.com/one")
            await agent.aget("https://example.com/two")
            with pytest.raises(RuntimeError, match="unavailable"):
                _ = agent.async_client
    finally:
        httpx.AsyncClient = original
    assert len(clients) == 2 and all(client.is_closed for client in clients)
    assert "cookie" not in seen[1].headers


@pytest.mark.asyncio
async def test_async_failure_recorded():
    async def fail(request):
        raise httpx.ConnectError("offline", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(fail))
    agent = VerifiableAgent(async_client=client)
    with pytest.raises(httpx.ConnectError):
        await agent.aget("https://example.com/fail")
    assert agent.records[0]["error_type"] == "ConnectError"
    await agent.aclose()
    await client.aclose()
