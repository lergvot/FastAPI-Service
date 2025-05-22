import pytest


@pytest.mark.asyncio
async def test_cat(async_client):
    response = await async_client.get("/api/cat")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data or "image" in data  # зависит от структуры
