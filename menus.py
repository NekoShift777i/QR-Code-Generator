from typing import Callable

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
