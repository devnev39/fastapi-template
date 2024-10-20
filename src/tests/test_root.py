from src.main import app
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
