import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_add_and_get_notes():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        note_text = "Тестовая заметка"
        response = await ac.post("/api/notes/add", data={"note": note_text})
        assert response.status_code == 200

        response = await ac.get("/api/notes")
        assert response.status_code == 200
        data = response.json()
        assert any(note_text in notes for notes in data.values())
