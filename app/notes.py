import json
import random 
from variables import *
from service import *
from fastapi import FastAPI, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import urlencode
from fastapi import APIRouter
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.post("/notes/add")
def add_note(note: str = Form(...)):
    """Добавление заметки"""
    notes = load_notes()
    if len(notes) >= MAX_NOTES:
        params = urlencode({"error": "Превышено максимальное количество заметок"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    if len(note) > MAX_NOTE_LENGTH:
        params = urlencode({"error": "Заметка слишком длинная"})
        return RedirectResponse(f"/?{params}", status_code=status.HTTP_303_SEE_OTHER)
    notes.append(note)
    save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/notes/delete/{note_id}")
def delete_note(note_id: int):
    """Удаление заметки"""
    notes = load_notes()
    if 0 <= note_id < len(notes):
        notes.pop(note_id)
        save_notes(notes)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/notes")
def get_notes():
    """Получение всех заметок"""
    notes = load_notes()
    return {"notes": notes}