from typing import Callable

from config import DEFAULT_SETTINGS, PRESETS, apply_preset, save_settings

from logos import choose_logo_file
from qr_generator import generate_qr_card
from wifi import build_wifi_string


def text_qr_menu(
    settings: dict,
    clear: Callable[[], None],
    pause: Callable[[], None],
    ask_yes_no: Callable[..., bool],
    resolve_output_path: Callable[[dict, str], str],
) -> None:
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
        logo_path = choose_logo_file(clear, pause)

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


def wifi_qr_menu(
    settings: dict,
    clear: Callable[[], None],
    pause: Callable[[], None],
    ask_yes_no: Callable[..., bool],
    resolve_output_path: Callable[[dict, str], str],
    sanitize_filename: Callable[[str], str],
) -> None:
    clear()
    print("=== Генерация Wi-Fi QR ===\n")

    ssid = input("SSID сети: ").strip()
    if not ssid:
        print("SSID не может быть пустым.")
        pause()
        return

    supported_security = {
        "wpa2-personal": "WPA2-Personal",
        "wpa3-personal": "WPA3-Personal",
        "открытая сеть": "Открытая сеть",
    }
    while True:
        security_input = input(
            "Тип защиты (WPA2-Personal / WPA3-Personal / Открытая сеть) "
            "[WPA2-Personal]: "
        ).strip()
        security = supported_security.get(
            (security_input or "WPA2-Personal").lower()
        )
        if security is not None:
            break
        print("[!] Недопустимый тип защиты. Выбери один из трёх вариантов.\n")

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
        logo_path = choose_logo_file(clear, pause)

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


def settings_menu(
    settings: dict,
    clear: Callable[[], None],
    pause: Callable[[], None],
    ask_yes_no: Callable[..., bool],
    normalize_path: Callable[[str], str],
) -> None:
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
            presets_menu(settings, clear, pause)

        elif choice == "11":
            settings.clear()
            settings.update(DEFAULT_SETTINGS.copy())
            save_settings(settings)
            print("\nНастройки сброшены.")
            pause()

        elif choice == "0":
            break


def presets_menu(settings: dict, clear: Callable[[], None], pause: Callable[[], None]) -> None:
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
