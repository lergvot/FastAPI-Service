# tests/test_service.py
import pytest

from service.service import *


# 1. Проверки получения колличества визитов
def test_get_visits_file_not_exists(tmp_path, monkeypatch):
    pass
    """# Подменяем путь
    test_file = tmp_path / "visits.txt"
    monkeypatch.setattr("service.service.VISITS_FILE", test_file)

    # Файл не существует
    assert get_visits() == 0

    # Некорректный файл
    test_file.write_text("invalid")
    assert get_visits() == 0

    # Корректный файл
    test_file.write_text("15")
    assert get_visits() == 15

    # Пустой файл
    test_file.write_text("")
    assert get_visits() == 0"""


# 2. Проверка инкремента визитов
def test_increment_visits(tmp_path, monkeypatch):
    pass
    """test_file = tmp_path / "visits.txt"
    monkeypatch.setattr("service.service.VISITS_FILE", test_file)

    assert get_visits() == 0
    v1 = increment_visits()
    assert v1 == 1
    v2 = increment_visits()
    assert v2 == 2"""


# 3. Проверка получения версии Git
def test_get_git_version_success():
    pass
    """result = get_git_version()
    assert isinstance(result, str)"""


# 4. Проверка ошибки получения версии Git
def test_get_git_version_failure(monkeypatch):
    pass
    """monkeypatch.setattr(
        "subprocess.check_output",
        lambda *a, **kw: (_ for _ in ()).throw(OSError("fail")),
    )
    assert get_git_version() == "unknown"""


# 5. Проверка вывода версии файла
def test_get_version(tmp_path, monkeypatch):
    pass
    """test_file = tmp_path / "version.txt"
    test_file.write_text("0.1.0")
    monkeypatch.setattr("service.service.VERSION_FILE", test_file)

    monkeypatch.setenv("ENV", "prod")
    version = get_version()
    assert version.startswith("v0.1.0")"""


# 6. Проверка корректности вывода версии в prod
def test_get_version_with_valid_file_prod(tmp_path, monkeypatch):
    pass
    """test_file = tmp_path / "version.txt"
    test_file.write_text("2.0.1")
    monkeypatch.setattr("service.service.VERSION_FILE", test_file)

    monkeypatch.setenv("ENV", "prod")
    version_prod = get_version()
    assert version_prod == "v2.0.1"""


# 7. Проверка корректности вывода версии в dev
def test_get_version_with_valid_file_dev(tmp_path, monkeypatch):
    pass
    """test_file = tmp_path / "version.txt"
    test_file.write_text("2.0.1")
    monkeypatch.setattr("service.service.VERSION_FILE", test_file)

    monkeypatch.setenv("ENV", "dev")
    version_dev = get_version()
    assert version_dev.startswith("v2.0.1")
    assert "dev" in version_dev"""


# 8. Проверка при отсутсвии файла
def test_get_version_file_missing(tmp_path, monkeypatch):
    test_file = tmp_path / "version.txt"
    monkeypatch.setattr("service.service.VERSION_FILE", test_file)

    version = get_version()
    assert version.startswith("v0.0.0")


# 9. get_all() получение содержимого файла
def test_get_all_returns_file_data(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["a", "b", "c"], ensure_ascii=False))

    storage = JsonStorage(file, mutable=False)
    data = storage.get_all()

    assert data == ["a", "b", "c"]


# 10. Проверка кэша при получении содержимого файла
def test_get_all_uses_cache(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["first"]))

    storage = JsonStorage(file, mutable=False)
    data1 = storage.get_all()

    # Меняем файл, но без force_refresh
    file.write_text(json.dumps(["modified"]))
    data2 = storage.get_all()

    assert data1 == data2 == ["first"]


# 11. Проверка обновления кэша
def test_get_all_force_refresh(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["first"]))

    storage = JsonStorage(file, mutable=False)
    storage.get_all()

    file.write_text(json.dumps(["updated"]))
    data = storage.get_all(force_refresh=True)

    assert data == ["updated"]


# 12. add() добавляет элемент и сохраняет файл
def test_add_appends_item_and_saves(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["x"]))

    storage = JsonStorage(file, mutable=True)
    storage.add("y")

    # Перечитываем файл напрямую
    data = json.loads(file.read_text(encoding="utf-8"))
    assert data == ["x", "y"]


# 13. delete() удаляет элемент по индексу
def test_delete_removes_item_by_index(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["1", "2", "3"]))

    storage = JsonStorage(file, mutable=True)
    storage.delete(1)  # Удаляем "2"

    assert storage.get_all() == ["1", "3"]


# 14. add() вызывает ошибку, если mutable=False
def test_add_raises_if_immutable(tmp_path):
    file = tmp_path / "data.json"
    file.write_text(json.dumps(["init"]))

    storage = JsonStorage(file, mutable=False)
    with pytest.raises(RuntimeError, match="только для чтения"):
        storage.add("new")
