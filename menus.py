from typing import Callable

from logos import choose_logo_file
from qr_generator import generate_qr_card


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
