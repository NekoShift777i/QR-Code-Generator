import os
from typing import Callable, Optional

from config import LOGOS_DIR, ensure_data_dirs


def get_logo_files() -> list[str]:
    ensure_data_dirs()

    allowed_ext = {".png", ".jpg", ".jpeg", ".webp"}
    files = []

    for name in os.listdir(LOGOS_DIR):
        path = os.path.join(LOGOS_DIR, name)
        if os.path.isfile(path):
            ext = os.path.splitext(name)[1].lower()
            if ext in allowed_ext:
                files.append(name)

    files.sort()
    return files


def choose_logo_file(clear: Callable[[], None], pause: Callable[[], None]) -> Optional[str]:
    logos = get_logo_files()

    if not logos:
        print("\n[!] В папке assets/logos нет подходящих логотипов.")
        print(f"Папка: {LOGOS_DIR}")
        print("Поддерживаются: .png, .jpg, .jpeg, .webp")
        pause()
        return None

    while True:
        clear()
        print("=== Выбор логотипа ===\n")
        print("0. Без логотипа\n")

        for i, logo_name in enumerate(logos, start=1):
            print(f"{i}. {logo_name}")

        choice = input("\nВыбор: ").strip()

        if choice == "0":
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(logos):
                return os.path.join(LOGOS_DIR, logos[idx - 1])

        print("\nНеверный выбор.")
        pause()


def logos_menu(clear: Callable[[], None], pause: Callable[[], None]) -> None:
    while True:
        clear()
        logos = get_logo_files()

        print("=== Логотипы ===\n")
        print(f"Папка логотипов: {LOGOS_DIR}\n")

        if logos:
            print("Найденные логотипы:")
            for i, logo_name in enumerate(logos, start=1):
                print(f"{i}. {logo_name}")
        else:
            print("Логотипов пока нет.")

        print("\n1. Открыть папку logos")
        print("2. Обновить список")
        print("3. Назад\n")

        choice = input("Выбор: ").strip()

        if choice == "1":
            try:
                os.startfile(LOGOS_DIR)  # Windows
            except AttributeError:
                print("\n[!] Автооткрытие папки поддерживается только в Windows.")
                pause()
            except Exception as e:
                print(f"\n[!] Не удалось открыть папку: {e}")
                pause()

        elif choice == "2":
            continue

        elif choice == "3":
            break
