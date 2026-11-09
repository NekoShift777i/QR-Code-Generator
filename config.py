import json
import os
import shutil
import sys


# =========================================================
# БАЗОВЫЕ ПУТИ И НАСТРОЙКИ
# =========================================================

def get_app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    
    return os.path.dirname(os.path.abspath(__file__))


SCRIPT_DIR = get_app_dir()
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
LOGOS_DIR = os.path.join(DATA_DIR, "logos")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")


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

PRESETS = {
    "Стандартный": {
        "error_correction": "H",
        "box_size": 12,
        "border": 4,
        "fill_color": "#222222",
        "back_color": "white",
        "logo_percent": 18,
        "logo_padding": 12,
    },
    
    "Компактный": {
        "error_correction": "M",
        "box_size": 8,
        "border": 4,
        "fill_color": "black",
        "back_color": "white",
        "logo_percent": 15,
        "logo_padding": 8,
    },
}


def ensure_data_dirs() -> None:
    """Создаёт каталоги данных и переносит старые пользовательские файлы."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGOS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    old_config = os.path.join(SCRIPT_DIR, "config.json")
    if os.path.isfile(old_config) and not os.path.exists(CONFIG_PATH):
        shutil.move(old_config, CONFIG_PATH)

    old_logos_dir = os.path.join(ASSETS_DIR, "logos")
    if os.path.isdir(old_logos_dir):
        for name in os.listdir(old_logos_dir):
            source = os.path.join(old_logos_dir, name)
            target = os.path.join(LOGOS_DIR, name)
            if os.path.isfile(source) and not os.path.exists(target):
                shutil.move(source, target)


def _pause() -> None:
    input("\nНажми Enter для продолжения...")


def load_settings() -> dict:
    ensure_data_dirs()
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception as e:
            print(f"[!] Не удалось загрузить config.json: {e}")
            _pause()

    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    try:
        ensure_data_dirs()
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[!] Не удалось сохранить config.json: {e}")
        _pause()
        
def apply_preset(settings: dict, preset_name: str) -> None:
    preset = PRESETS.get(preset_name)
    
    if preset is None:
        raise ValueError(f"Пресет не найден: {preset_name}")
    
    settings.update(preset)
    save_settings(settings)


