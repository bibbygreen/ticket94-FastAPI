import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_health(client: AsyncClient):
    resp = await client.get("/health")

    assert resp.status_code == 200
