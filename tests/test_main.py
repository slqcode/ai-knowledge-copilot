import json

import httpx
import pytest

from app.main import app, settings


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app"] == "ai-knowledge-copilot"


@pytest.mark.anyio
async def test_hello(client):
    response = await client.get("/hello", params={"name": "FE"})
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, FE"


@pytest.mark.anyio
async def test_stream_events(client):
    original_delay = settings.STREAM_DELAY_SECONDS
    settings.STREAM_DELAY_SECONDS = 0
    try:
        response = await client.get("/stream")
    finally:
        settings.STREAM_DELAY_SECONDS = original_delay

    events = [line for line in response.text.splitlines() if line.startswith("data: ")]
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert len(events) == 5
    assert json.loads(events[0].removeprefix("data: ")) == {"token": "chunk-1"}
