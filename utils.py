"""Общие вспомогательные функции приложения."""

import os
import ntpath

from config import OUTPUT_DIR


class InvalidOutputPathError(ValueError):
    """Неккоректный путь к каталогу сохранения"""


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

    if len(path) >= 2 and path[0] == path[-1] and path[0] in {'"', "'"}:
        path = path[1:-1]

    path = path.strip()

    if not path:
        return ""

    if os.name == "nt":
        drive, tail = ntpath.splitdrive(path)

        if len(drive) == 2 and drive[1] == ":":
            if not tail:
                path = drive + "\\"
            elif not tail.startswith(("\\", "/")):
                raise InvalidOutputPathError(
                    "Укажи абсолютный путь к каталогу, например D:\\QR."
                )

    return os.path.normpath(path)


def sanitize_filename(name: str) -> str:
    bad_chars = '<>:"/\\|?*'
    for ch in bad_chars:
        name = name.replace(ch, "_")
    return name.strip()


def resolve_output_path(settings: dict, filename: str) -> str:
    output_dir = normalize_path(settings.get("default_output_dir", ""))

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, filename)

    return os.path.join(OUTPUT_DIR, filename)
