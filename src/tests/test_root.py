# ruff: noqa: S101
import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
