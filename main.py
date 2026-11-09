import os
from typing import Optional

from config import (
    DATA_DIR,
    DEFAULT_SETTINGS,
    LOGOS_DIR,
    OUTPUT_DIR,
    PRESETS,
    SCRIPT_DIR,
    apply_preset,
    ensure_data_dirs,
    load_settings,
    save_settings,
)

from qr_generator import generate_qr_card
from wifi import build_wifi_string


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

def get_logo_files() -> list[str]:
    ensure_asset_dirs()

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


def choose_logo_file() -> Optional[str]:
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


def logos_menu() -> None:
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


# =========================================================
# QR И ЛОГОТИП
# =========================================================











# =========================================================
# МЕНЮ ГЕНЕРАЦИИ
# =========================================================

def wifi_qr_menu(settings: dict) -> None:
    clear()
    print("=== Генерация Wi-Fi QR ===\n")

    ssid = input("SSID сети: ").strip()
    if not ssid:
        print("SSID не может быть пустым.")
        pause()
        return

    security = input("Тип защиты (WPA2-Personal / WPA3-Personal / Открытая сеть): ").strip() or "WPA2-Personal"

    password = ""
    if security.lower() not in {"nopass", "none", "open", "открытая", "открытая сеть"}:
        password = input("Пароль сети: ").strip()
        
        if not password:
            print("Пароль не может быть пустым для защищённой сети.")
            pause()
            return

    hidden = ask_yes_no("Скрытая сеть?", default=False)
    show_password = ask_yes_no(
        "Показывать пароль под QR?",
        default=settings["show_password_by_default"]
    )

    title = input("Заголовок карточки [Wi-Fi доступ]: ").strip() or "Wi-Fi доступ"

    logo_path = None
    if ask_yes_no("Добавить логотип?", default=False):
        logo_path = choose_logo_file()

    output_name = input(f"Имя файла [wifi_{ssid}.png]: ").strip()
    if not output_name:
        output_name = f"wifi_{sanitize_filename(ssid)}.png"
    if not output_name.lower().endswith(".png"):
        output_name += ".png"

    output_path = resolve_output_path(settings, output_name)

    wifi_data = build_wifi_string(
        ssid=ssid,
        password=password,
        security=security,
        hidden=hidden
    )

    subtitle_lines = [f"SSID: {ssid}"]

    if security.strip().lower() in {"nopass", "none", "open", "открытая", "открытая сеть"}:
        subtitle_lines.append("Без пароля")
    elif show_password:
        subtitle_lines.append(f"Пароль: {password}")
    else:
        subtitle_lines.append("Пароль: ******")

    if hidden:
        subtitle_lines.append("Скрытая сеть: да")

    try:
        generate_qr_card(
            data=wifi_data,
            output_path=output_path,
            settings=settings,
            title=title,
            subtitle_lines=subtitle_lines,
            logo_path=logo_path
        )
        print(f"\nГотово: {output_path}")
    except Exception as e:
        print(f"\n[!] Ошибка при генерации Wi-Fi QR: {e}")

    pause()


def text_qr_menu(settings: dict) -> None:
    clear()
    print("=== Генерация QR из текста / ссылки ===\n")

    text = input("Введи текст или ссылку:\n").strip()
    if not text:
        print("Текст не может быть пустым.")
        pause()
        return

    title = input("Заголовок карточки [QR-код]: ").strip() or "QR-код"

    logo_path = None
    if ask_yes_no("Добавить логотип?", default=False):
        logo_path = choose_logo_file()

    output_name = input("Имя файла [qr_text.png]: ").strip() or "qr_text.png"
    if not output_name.lower().endswith(".png"):
        output_name += ".png"

    output_path = resolve_output_path(settings, output_name)

    try:
        generate_qr_card(
            data=text,
            output_path=output_path,
            settings=settings,
            title=title,
            subtitle_lines=[text],
            logo_path=logo_path
        )
        print(f"\nГотово: {output_path}")
    except Exception as e:
        print(f"\n[!] Ошибка при генерации QR: {e}")

    pause()


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
            wifi_qr_menu(settings)
        elif choice == "2":
            text_qr_menu(settings)
        elif choice == "3":
            logos_menu()
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