import os
import importlib.util
import sys

def check_working_dir():
    cwd = os.getcwd()
    print(f"[✓] Текущая директория: {cwd}")
    expected_file = os.path.join(cwd, 'main.py')
    if os.path.isfile(expected_file):
        print(f"[✓] Найден main.py в рабочей директории.")
    else:
        print(f"[✗] Не найден main.py в {cwd}.")
        return False
    return True

def check_module_import():
    try:
        spec = importlib.util.spec_from_file_location("main", "./main.py")
        main = importlib.util.module_from_spec(spec)
        sys.modules["main"] = main
        spec.loader.exec_module(main)

        if hasattr(main, "app"):
            print(f"[✓] Модуль main загружен, переменная 'app' найдена.")
        else:
            print(f"[✗] Модуль main загружен, но переменная 'app' не найдена.")
            return False
    except Exception as e:
        print(f"[✗] Ошибка при импорте main.py: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Проверка FastAPI окружения\n" + "="*30)
    dir_ok = check_working_dir()
    if dir_ok:
        import_ok = check_module_import()
        if import_ok:
            print("\n✅ Всё готово для запуска: `uvicorn main:app` должен работать.")
        else:
            print("\n🚫 Проверь, есть ли в `main.py` переменная `app = FastAPI()`.")
    else:
        print("\n🚫 Убедись, что `main.py` находится в текущей директории.")

