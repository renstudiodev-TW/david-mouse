"""Compose the FB launch banner: before/after comparison of full-mode
window vs the new 90×90 watch widget.

Canvas: 1200×630 (FB share-image ratio). Both screenshots scaled down
~55% so the full-mode screenshot fits comfortably next to the 90×90
watch widget without overlapping the headline. The size gap is still
very obvious (watch is ~1/8 the area of full mode at that scale).

Output: docs/fb-banner.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs" / "screenshots" / "zh-TW"
OUT = ROOT / "docs" / "fb-banner.png"

W, H = 1200, 630
BG_TOP = (243, 247, 252)
BG_BOTTOM = (255, 255, 255)
INK = (26, 26, 26)
MUTED = (90, 90, 90)
ACCENT = (35, 131, 226)
SCALE = 0.55  # both screenshots scaled equally to keep comparison honest


def gradient_bg(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/msjhbd.ttc" if bold else "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/segoeui.ttf",
        "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def shadow_paste(canvas, img, xy):
    sx, sy = xy[0] + 4, xy[1] + 8
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    silhouette = Image.new("RGBA", img.size, (0, 0, 0, 70))
    shadow.paste(silhouette, (0, 0))
    canvas.paste(shadow, (sx, sy), shadow)
    canvas.paste(img, xy)


def main():
    canvas = gradient_bg(W, H, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(canvas)

    f_h1 = load_font(48, bold=True)
    f_h2 = load_font(24, bold=False)
    f_label = load_font(20, bold=True)
    f_url = load_font(24, bold=True)

    # Headline band (top)
    draw.text((60, 50), "看 YouTube 不再被誤觸暫停", font=f_h1, fill=INK)
    draw.text((60, 115), "「觀影模式」一鍵把視窗縮成角落小方塊，畫面不擋、頭部晃動也不誤觸",
              font=f_h2, fill=MUTED)

    # Load and scale screenshots
    full = Image.open(SHOTS / "ui-running.png").convert("RGB")
    watch = Image.open(SHOTS / "ui-watch.png").convert("RGB")
    fw, fh = full.size
    full_scaled = full.resize((int(fw * SCALE), int(fh * SCALE)), Image.LANCZOS)
    watch_scaled = watch.resize((int(watch.size[0] * SCALE), int(watch.size[1] * SCALE)),
                                Image.LANCZOS)

    # Layout the comparison row
    image_area_top = 200
    image_area_bottom = H - 90  # leave room for URL band
    fw2, fh2 = full_scaled.size
    ww2, wh2 = watch_scaled.size

    # Horizontal positions: left third for full, right third for watch
    full_x = 180
    watch_x = W - ww2 - 280
    full_y = image_area_top + ((image_area_bottom - image_area_top) - fh2) // 2
    # Center watch vertically against the full-mode block
    watch_y = full_y + (fh2 - wh2) // 2

    shadow_paste(canvas, full_scaled, (full_x, full_y))
    shadow_paste(canvas, watch_scaled, (watch_x, watch_y))

    # Labels under each
    label_full = f"原本：{fw}×{fh}"
    label_watch = f"觀影模式：{watch.size[0]}×{watch.size[1]}"
    bb = draw.textbbox((0, 0), label_full, font=f_label)
    lw = bb[2] - bb[0]
    draw.text((full_x + (fw2 - lw) // 2, full_y + fh2 + 12),
              label_full, font=f_label, fill=INK)
    bb = draw.textbbox((0, 0), label_watch, font=f_label)
    lw = bb[2] - bb[0]
    draw.text((watch_x + (ww2 - lw) // 2, watch_y + wh2 + 12),
              label_watch, font=f_label, fill=ACCENT)

    # Arrow between them
    arrow_y = full_y + fh2 // 2
    arrow_x1 = full_x + fw2 + 40
    arrow_x2 = watch_x - 40
    draw.line([(arrow_x1, arrow_y), (arrow_x2, arrow_y)],
              fill=ACCENT, width=6)
    draw.polygon([
        (arrow_x2, arrow_y),
        (arrow_x2 - 22, arrow_y - 16),
        (arrow_x2 - 22, arrow_y + 16),
    ], fill=ACCENT)

    cap = "一鍵縮小"
    bb = draw.textbbox((0, 0), cap, font=f_label)
    cap_w = bb[2] - bb[0]
    mid_x = (arrow_x1 + arrow_x2) // 2
    draw.text((mid_x - cap_w // 2, arrow_y - 48), cap, font=f_label, fill=ACCENT)

    # URL band (bottom)
    band_h = 60
    band_y = H - band_h
    draw.rectangle((0, band_y, W, H), fill=ACCENT)
    url = "David Mouse 大衛滑鼠  ·  davidmouse.renstudio.tw  ·  免費 / 開源 / 4 語系"
    bb = draw.textbbox((0, 0), url, font=f_url)
    url_w = bb[2] - bb[0]
    draw.text(((W - url_w) // 2, band_y + (band_h - 32) // 2),
              url, font=f_url, fill=(255, 255, 255))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT, "PNG", optimize=True)
    print(f"saved: {OUT}  ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
