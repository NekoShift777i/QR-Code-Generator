from config import (
    ensure_data_dirs,
    load_settings,
)

from logos import logos_menu
from menus import settings_menu, text_qr_menu, wifi_qr_menu


from utils import (
    ask_yes_no,
    clear,
    normalize_path,
    pause,
    resolve_output_path,
    sanitize_filename,
)


def main() -> None:
    ensure_data_dirs()
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