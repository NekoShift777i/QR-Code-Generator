import os

from config import (
    DATA_DIR,
    OUTPUT_DIR,
    ensure_data_dirs,
    load_settings,
)

from logos import logos_menu
from menus import settings_menu, text_qr_menu, wifi_qr_menu


# =========================================================
# СЛУЖЕБНЫЕ ФУНКЦИИ
# =========================================================

def ensure_asset_dirs() -> None:
    ensure_data_dirs()


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input("\nНажми Enter для продолжения...")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    value = input(prompt + suffix).strip().lower()

    if not value:
        return default

    return value in {"y", "yes", "д", "да"}





def normalize_path(path: str) -> str:
    path = path.strip()
    
    if len(path) >= 2 and path[0] ==path[-1] and path[0] in {'"', "'"}:
        path = path[1:-1]
        
    return path.strip()

def sanitize_filename(name: str) -> str:
    bad_chars = '<>:"/\\|?*'
    for ch in bad_chars:
        name = name.replace(ch, "_")
    return name.strip()


def resolve_output_path(settings: dict, filename: str) -> str:
    output_dir = normalize_path(
        settings.get("default_output_dir", "")
    )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    return os.path.join(OUTPUT_DIR, filename)


# =========================================================
# РАБОТА С ЛОГОТИПАМИ
# =========================================================

# =========================================================
# QR И ЛОГОТИП
# =========================================================











# =========================================================
# МЕНЮ ГЕНЕРАЦИИ
# =========================================================

# =========================================================
# МЕНЮ НАСТРОЕК
# =========================================================



# =========================================================
# ГЛАВНОЕ МЕНЮ
# =========================================================

def main() -> None:
    ensure_asset_dirs()
    settings = load_settings()

    while True:
        clear()
        print("========== QR UTILITY ==========\n")
        print("1. Создать Wi-Fi QR")
        print("2. Создать QR из текста / ссылки")
        print("3. Логотипы")
        print("4. Настройки")
        print("--------------------------------")
        print("0. Выход\n")

        choice = input("Выбор: ").strip()

        if choice == "1":
            wifi_qr_menu(settings, clear, pause, ask_yes_no, resolve_output_path, sanitize_filename)
        elif choice == "2":
            text_qr_menu(settings, clear, pause, ask_yes_no, resolve_output_path)
        elif choice == "3":
            logos_menu(clear, pause)
        elif choice == "4":
            settings_menu(settings, clear, pause, ask_yes_no, normalize_path)
        elif choice == "0":
            print("\nВыход.")
            break
        else:
            print("\nНеверный пункт.")
            pause()


if __name__ == "__main__":
    main()