import pytest


@pytest.mark.asyncio
async def test_add_and_get_notes(async_client):
    note = "Заметка из теста"
    await async_client.post("/api/notes/add", data={"note": note})
    response = await async_client.get("/api/notes")
    assert response.status_code == 200
    assert any(note in notes for notes in response.json().values())
