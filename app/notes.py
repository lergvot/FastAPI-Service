# app/notes.py
import logging
from typing import Dict, List
from urllib.parse import urlencode

from fastapi import APIRouter, Form, status
from fastapi.responses import RedirectResponse

from service.service import load_notes, save_notes
from service.variables import MAX_NOTE_LENGTH, MAX_NOTES

logging.basicConfig(level=logging.INFO)
router = APIRouter()


@router.post("/notes/add", tags=["Notes"])
def add_note(note: str = Form(...)) -> RedirectResponse:
    """Добавление заметки"""
    notes: List[str] = load_notes()

    if not note.strip():
        params = urlencode({"error": "Заметка не может быть пустой"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    if len(notes) >= MAX_NOTES:
        params = urlencode({"error": "Превышено максимальное количество заметок"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    if len(note) > MAX_NOTE_LENGTH:
        params = urlencode({"error": "Заметка слишком длинная"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    notes.append(note)
    save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/notes/delete/{note_id}", tags=["Notes"])
def delete_note(note_id: int) -> RedirectResponse:
    """Удаление заметки"""
    notes: List[str] = load_notes()
    if 0 <= note_id < len(notes):
        notes.pop(note_id)
        save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/notes", tags=["Notes"])
def get_notes() -> Dict[str, List[str]]:
    """Получение всех заметок"""
    notes = load_notes()
    return {"notes": notes}
