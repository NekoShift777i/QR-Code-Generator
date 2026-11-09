import os

from config import (
    DATA_DIR,
    DEFAULT_SETTINGS,
    OUTPUT_DIR,
    PRESETS,
    SCRIPT_DIR,
    apply_preset,
    ensure_data_dirs,
    load_settings,
    save_settings,
)

from logos import logos_menu
from menus import text_qr_menu, wifi_qr_menu


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

def presets_menu(settings: dict) -> None:
    while True:
        clear()
        print("=== Пресеты QR ===\n")
        
        preset_names = list(PRESETS.keys())
    
        for i, preset_name in enumerate(preset_names, start=1):
            print(f"{i}. {preset_name}")
        
        print("\n0. Назад\n")
        
        choice = input("Выбор: ").strip()
        
        if choice == "0":
            break
        
        if choice.isdigit():
            idx = int(choice)
            
            if 1 <= idx <= len(preset_names):
                preset_name = preset_names[idx - 1]
                apply_preset(settings, preset_name)
                
                print(f"\nПрименён пресет: {preset_name}")
                pause()
                continue
            
            print("\nНеверный выбор")
            pause()

def settings_menu(settings: dict) -> None:
    while True:
        clear()
        print("=== Настройки QR ===\n")
        print(f"1. Уровень коррекции ошибок: {settings['error_correction']}")
        print(f"2. Размер элемента (box_size): {settings['box_size']}")
        print(f"3. Защитное поле (border): {settings['border']}")
        print(f"4. Цвет элементов: {settings['fill_color']}")
        print(f"5. Цвет фона: {settings['back_color']}")
        print(f"6. Размер логотипа (%): {settings['logo_percent']}")
        print(f"7. Поля логотипа (px): {settings['logo_padding']}")
        print(f"8. Показывать пароль по умолчанию: {settings['show_password_by_default']}")
        print(f"9. Папка сохранения: {settings['default_output_dir'] or '(data/output)'}")
        print(f"10. Пресеты")
        print("11. Сбросить настройки по умолчанию")
        print("-----------------------------------")
        print("0. Назад\n")

        choice = input("Выбор: ").strip()

        if choice == "1":
            value = input("Введите L / M / Q / H: ").strip().upper()
            if value in {"L", "M", "Q", "H"}:
                settings["error_correction"] = value
                save_settings(settings)

        elif choice == "2":
            value = input("Размер элемента (1-60): ").strip()
            if value.isdigit():
                n = int(value)
                if 1 <= n <= 60:
                    settings["box_size"] = n
                    save_settings(settings)

        elif choice == "3":
            value = input("Размер защитного поля (0-10): ").strip()
            if value.isdigit():
                n = int(value)
                if 0 <= n <= 10:
                    settings["border"] = n
                    save_settings(settings)

        elif choice == "4":
            value = input("Цвет элементов (например black или #222222): ").strip()
            if value:
                settings["fill_color"] = value
                save_settings(settings)

        elif choice == "5":
            value = input("Цвет фона (например white или #ffffff): ").strip()
            if value:
                settings["back_color"] = value
                save_settings(settings)

        elif choice == "6":
            value = input("Размер логотипа в % (5-25): ").strip()
            if value.isdigit():
                n = int(value)
                if 5 <= n <= 25:
                    settings["logo_percent"] = n
                    save_settings(settings)

        elif choice == "7":
            value = input("Поля логотипа в px (1-50): ").strip()
            if value.isdigit():
                n = int(value)
                if 1 <= n <= 50:
                    settings["logo_padding"] = n
                    save_settings(settings)

        elif choice == "8":
            settings["show_password_by_default"] = ask_yes_no(
                "Показывать пароль по умолчанию?",
                default=settings["show_password_by_default"]
            )
            save_settings(settings)

        elif choice == "9":
            value = normalize_path(
                input("Папка сохранения (пусто = data/output): ")
            )
            settings["default_output_dir"] = value
            save_settings(settings)
        
        elif choice == "10":
            presets_menu(settings)

        elif choice == "11":
            settings.clear()
            settings.update(DEFAULT_SETTINGS.copy())
            save_settings(settings)
            print("\nНастройки сброшены.")
            pause()

        elif choice == "0":
            break


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
            settings_menu(settings)
        elif choice == "0":
            print("\nВыход.")
            break
        else:
            print("\nНеверный пункт.")
            pause()


if __name__ == "__main__":
    main()