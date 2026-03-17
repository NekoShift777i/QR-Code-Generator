import json
import os
from typing import Optional

import qrcode
from PIL import Image, ImageDraw, ImageFont


# =========================================================
# БАЗОВЫЕ ПУТИ И НАСТРОЙКИ
# =========================================================

def get_script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


SCRIPT_DIR = get_script_dir()
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
LOGOS_DIR = os.path.join(ASSETS_DIR, "logos")
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


DEFAULT_SETTINGS = {
    "error_correction": "H",      # L / M / Q / H
    "box_size": 12,               # 1-60
    "border": 4,                  # 0-10
    "fill_color": "#222222",
    "back_color": "white",
    "logo_percent": 18,           # 5-25
    "logo_padding": 12,           # 1-50
    "show_password_by_default": True,
    "default_output_dir": ""
}


# =========================================================
# СЛУЖЕБНЫЕ ФУНКЦИИ
# =========================================================

def ensure_asset_dirs() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(LOGOS_DIR, exist_ok=True)


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input("\nНажми Enter для продолжения...")


def load_settings() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception as e:
            print(f"[!] Не удалось загрузить config.json: {e}")
            pause()

    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Не удалось сохранить config.json: {e}")
        pause()


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    value = input(prompt + suffix).strip().lower()

    if not value:
        return default

    return value in {"y", "yes", "д", "да"}


def load_font(size: int):
    candidates = [
        "arial.ttf",
        "Arial.ttf",
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def get_error_correction(level: str):
    level = level.upper().strip()
    mapping = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    return mapping.get(level, qrcode.constants.ERROR_CORRECT_H)


def sanitize_filename(name: str) -> str:
    bad_chars = '<>:"/\\|?*'
    for ch in bad_chars:
        name = name.replace(ch, "_")
    return name.strip()


def resolve_output_path(settings: dict, filename: str) -> str:
    output_dir = settings.get("default_output_dir", "").strip()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    return os.path.join(SCRIPT_DIR, filename)


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
# WIFI QR ФОРМАТ
# =========================================================

def build_wifi_string(
    ssid: str,
    password: str,
    security: str = "WPA2-Personal",
    hidden: bool = False
) -> str:
    def escape_value(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(";", r"\;")
            .replace(",", r"\,")
            .replace(":", r"\:")
            .replace('"', r"\"")
        )
        
    security_normalized = security.strip().lower()
    
    if security_normalized in {"wpa2-personal", "wpa3-personal", "wpa", "wpa2", "wpa3"}:
        qr_security = "WPA"
    elif security_normalized in {"nopass", "none", "open", "открытая", "открытая сеть"}:
        qr_security = "nopass"
    else:
        raise ValueError(
            "Поддерживаются только WPA2-Personal, WPA3-Personal, Открытая сеть"
        )
        
    ssid_escaped = escape_value(ssid)
    password_escaped = escape_value(password)
    hidden_str = "True" if hidden else "false"
    
    if qr_security == "nopass":
        return f"WIFI:T:{qr_security};S:{ssid_escaped};H:{hidden_str};;"
        
    return (
        f"WIFI:T:{qr_security};"
        f"S:{ssid_escaped};"
        f"P:{password_escaped};"
        f"H:{hidden_str};;"
    )

# =========================================================
# QR И ЛОГОТИП
# =========================================================

def fit_logo(logo: Image.Image, qr_size: int, logo_percent: int) -> Image.Image:
    logo = logo.convert("RGBA")
    max_size = int(qr_size * (logo_percent / 100))
    logo.thumbnail((max_size, max_size), Image.LANCZOS)
    return logo


def paste_logo_center(
    qr_img: Image.Image,
    logo_path: Optional[str],
    settings: dict
) -> Image.Image:
    if not logo_path:
        return qr_img

    if not os.path.exists(logo_path):
        print(f"[!] Логотип не найден: {logo_path}")
        return qr_img

    qr_img = qr_img.convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    logo = fit_logo(logo, qr_img.width, settings["logo_percent"])

    padding = settings["logo_padding"]
    bg_w = logo.width + padding * 2
    bg_h = logo.height + padding * 2

    x_bg = (qr_img.width - bg_w) // 2
    y_bg = (qr_img.height - bg_h) // 2

    x_logo = (qr_img.width - logo.width) // 2
    y_logo = (qr_img.height - logo.height) // 2
    qr_img.alpha_composite(logo, (x_logo, y_logo))

    return qr_img


def create_qr_image(data: str, settings: dict) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=get_error_correction(settings["error_correction"]),
        box_size=settings["box_size"],
        border=settings["border"],
    )
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image(
        fill_color=settings["fill_color"],
        back_color=settings["back_color"]
    ).convert("RGBA")


def create_card(
    qr_img: Image.Image,
    title: str,
    subtitle_lines: list[str],
) -> Image.Image:
    title_font = load_font(30)
    text_font = load_font(22)

    dummy = Image.new("RGB", (1, 1), "white")
    draw_dummy = ImageDraw.Draw(dummy)

    max_text_width = 0
    total_text_height = 0

    if title:
        bbox = draw_dummy.textbbox((0, 0), title, font=title_font)
        max_text_width = max(max_text_width, bbox[2] - bbox[0])
        total_text_height += (bbox[3] - bbox[1]) + 12

    for line in subtitle_lines:
        bbox = draw_dummy.textbbox((0, 0), line, font=text_font)
        max_text_width = max(max_text_width, bbox[2] - bbox[0])
        total_text_height += (bbox[3] - bbox[1]) + 8

    margin = 30
    spacing = 20

    canvas_width = max(qr_img.width, max_text_width + margin * 2)
    canvas_height = qr_img.height + spacing + total_text_height + margin * 2

    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    qr_x = (canvas_width - qr_img.width) // 2
    qr_y = margin
    canvas.alpha_composite(qr_img, (qr_x, qr_y))

    y = qr_y + qr_img.height + spacing

    if title:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        w = bbox[2] - bbox[0]
        draw.text(((canvas_width - w) // 2, y), title, fill="black", font=title_font)
        y += (bbox[3] - bbox[1]) + 12

    for line in subtitle_lines:
        bbox = draw.textbbox((0, 0), line, font=text_font)
        w = bbox[2] - bbox[0]
        draw.text(((canvas_width - w) // 2, y), line, fill="black", font=text_font)
        y += (bbox[3] - bbox[1]) + 8

    return canvas.convert("RGB")


def generate_qr_card(
    data: str,
    output_path: str,
    settings: dict,
    title: str = "",
    subtitle_lines: Optional[list[str]] = None,
    logo_path: Optional[str] = None,
) -> None:
    if subtitle_lines is None:
        subtitle_lines = []

    qr_img = create_qr_image(data, settings)
    qr_img = paste_logo_center(qr_img, logo_path, settings)
    card = create_card(qr_img, title, subtitle_lines)
    card.save(output_path, "PNG")


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
        print(f"9. Папка сохранения: {settings['default_output_dir'] or '(рядом со скриптом)'}")
        print("10. Сбросить настройки по умолчанию")
        print("11. Назад\n")

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
            value = input("Папка сохранения (пусто = рядом со скриптом): ").strip()
            settings["default_output_dir"] = value
            save_settings(settings)

        elif choice == "10":
            settings.clear()
            settings.update(DEFAULT_SETTINGS.copy())
            save_settings(settings)
            print("\nНастройки сброшены.")
            pause()

        elif choice == "11":
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
        print("5. Выход\n")

        choice = input("Выбор: ").strip()

        if choice == "1":
            wifi_qr_menu(settings)
        elif choice == "2":
            text_qr_menu(settings)
        elif choice == "3":
            logos_menu()
        elif choice == "4":
            settings_menu(settings)
        elif choice == "5":
            print("\nВыход.")
            break
        else:
            print("\nНеверный пункт.")
            pause()


if __name__ == "__main__":
    main()
