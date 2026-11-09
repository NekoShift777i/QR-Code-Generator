"""Создание QR-кодов и карточек с дополнительными изображениями."""

import os
from typing import Optional

import qrcode
from PIL import Image, ImageDraw, ImageFont


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

