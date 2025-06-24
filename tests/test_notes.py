# tests/test_notes.py
import pytest

from service.config import MAX_NOTE_LENGTH, MAX_NOTES
from service.service import notes_storage

test_notes_data = ["Тестовые данные", "test", "1"]


@pytest.fixture
def mock_notes(monkeypatch):
    def _mock(data):
        monkeypatch.setattr(notes_storage, "get_all", lambda force_refresh=False: data)

    return _mock


# 1. Получаем все заметки
@pytest.mark.asyncio
async def test_get_notes(client, mock_notes):
    mock_notes(test_notes_data)
    response = await client.get("/api/notes?nocache=true")
    json_data = response.json()["notes"]

    assert response.status_code == 200
    assert json_data == test_notes_data


# 2. Добавление заметки
@pytest.mark.asyncio
async def test_add_note(client, mock_notes):
    mock_notes(test_notes_data)
    response_before = await client.get("/api/notes?nocache=true")
    notes_before = response_before.json()["notes"]
    count_before = len(notes_before)

    # Добавляем новую заметку
    response_post = await client.post(
        "/api/notes/add",
        data={"note": "test message"},
        headers={"accept": "application/json"},
    )
    assert response_post.status_code == 303

    # Получаем заметки после добавления
    response_after = await client.get("/api/notes?nocache=true")
    notes_after = response_after.json()["notes"]

    assert len(notes_after) == count_before + 1
    assert "test message" in notes_after


# 3. Удаление заметки
@pytest.mark.asyncio
async def test_delete_note(client, mock_notes):
    mock_notes(test_notes_data)
    note_to_delete = len(test_notes_data) - 1

    # Удаляем заметку
    response_post = await client.post(
        f"/api/notes/delete/{note_to_delete}",
        data={"note": "test message"},
        headers={"accept": "application/json"},
    )
    assert response_post.status_code == 303
    response_after = await client.get("/api/notes?nocache=true")
    notes_after = response_after.json()["notes"]

    assert len(notes_after) == note_to_delete


# 4. Удаление ID вне диапазона при удалении
@pytest.mark.asyncio
async def test_delete_invalid_id(client, mock_notes):
    mock_notes(test_notes_data)

    # Удаляем заметку
    response_post = await client.post(
        f"/api/notes/delete/{MAX_NOTES+1}",
        data={"note": "test message"},
        headers={"accept": "application/json"},
    )
    assert response_post.status_code == 404
    assert response_post.json()["detail"] == {"error": "Заметка не найдена"}


# 5. Проверка добавления пустой заметки
@pytest.mark.asyncio
async def test_add_empty_note(client, mock_notes):
    mock_notes(test_notes_data)
    response_post = await client.post(
        "/api/notes/add",
        data={"note": ""},
        headers={"accept": "application/json"},
    )
    assert response_post.status_code == 400
    assert response_post.json()["detail"] == {"error": "Заметка не может быть пустой"}


# 6. Проверка добавления длинной заметки
@pytest.mark.asyncio
async def test_add_long_note(client, mock_notes):
    mock_notes(test_notes_data)
    # Максимальная допустимая длина
    response_post = await client.post(
        "/api/notes/add",
        data={"note": "x" * MAX_NOTE_LENGTH},
        headers={"accept": "application/json"},
    )

    assert response_post.status_code == 303

    # Переполнение длины
    test_lenght = MAX_NOTE_LENGTH + 1
    response_post = await client.post(
        "/api/notes/add",
        data={"note": "x" * test_lenght},
        headers={"accept": "application/json"},
    )

    assert response_post.status_code == 400
    assert response_post.json()["detail"] == {"error": "Заметка слишком длинная"}


# 7. Проверка переполнения списка заметок
@pytest.mark.asyncio
async def test_overflow_list(client, mock_notes):
    mock_notes([])

    # Добавляем новые заметки пока не упрёмся в лимит
    for _ in range(MAX_NOTES):
        response = await client.post(
            "/api/notes/add",
            data={"note": "test message"},
            headers={"accept": "application/json"},
        )
        assert response.status_code == 303

    # Попытка переполнить
    response = await client.post(
        "/api/notes/add",
        data={"note": "лишняя"},
        headers={"accept": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == {
        "error": "Превышено максимальное количество заметок"
    }


# 8. Добавление пустой заметки с Accept: text/html → редирект с ошибкой
@pytest.mark.asyncio
async def test_add_empty_note_html_accept(client, mock_notes):
    mock_notes([])
    response = await client.post(
        "/api/notes/add",
        data={"note": ""},
        headers={"accept": "text/html"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "error=" in response.headers["location"]


# Не до конца понял что тут тестируем
# 9. Поведение, если background_tasks нет (например, мокнуть None),
