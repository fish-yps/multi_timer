# -*- coding: utf-8 -*-
"""生成墨绿玻璃时钟图标 -> MultiTimer.ico / 多尺寸 png。"""

from PIL import Image, ImageDraw, ImageFilter
import math
import os

SIZE = 512
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

GREEN = (21, 104, 71)
GREEN_BRIGHT = (29, 138, 95)
GREEN_DARK = (12, 44, 30)
GREEN_LIGHT = (43, 122, 85)
FG = (216, 239, 226)
ACCENT = (201, 162, 39)  # 琥珀秒针


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_clock(size=SIZE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 外圈阴影
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([size * 0.03, size * 0.03, size * 0.97, size * 0.97],
               fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size * 0.04))
    img.alpha_composite(shadow)

    # 表盘渐变（墨绿玻璃）
    dial = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dial)
    top = lerp(GREEN_BRIGHT, GREEN, 0.35)
    bottom = GREEN_DARK
    for y in range(int(size * 0.06), int(size * 0.94)):
        t = (y - size * 0.06) / (size * 0.88)
        color = lerp(top, bottom, t)
        dd.line([(size * 0.06, y), (size * 0.94, y)], fill=color + (255,))
    # 裁成圆形
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([size * 0.06, size * 0.06, size * 0.94, size * 0.94], fill=255)
    dial = Image.composite(dial, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask)
    img.alpha_composite(dial)

    # 表盘高光（左上玻璃反光）
    gloss = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.ellipse([size * 0.14, size * 0.10, size * 0.52, size * 0.40],
               fill=(255, 255, 255, 28))
    gloss = gloss.filter(ImageFilter.GaussianBlur(size * 0.03))
    gloss = Image.composite(gloss, Image.new("RGBA", (size, size), (0, 0, 0, 0)), mask)
    img.alpha_composite(gloss)

    # 外边框
    d.ellipse([size * 0.06, size * 0.06, size * 0.94, size * 0.94],
              outline=GREEN_LIGHT, width=max(2, int(size * 0.012)))

    # 刻度
    cx = cy = size / 2
    r_outer = size * 0.40
    r_inner = size * 0.355
    for i in range(60):
        ang = math.radians(i * 6 - 90)
        is_major = i % 5 == 0
        r2 = r_outer if is_major else (r_outer - size * 0.018)
        w = max(3, int(size * 0.014)) if is_major else max(2, int(size * 0.006))
        color = FG if is_major else lerp(FG, GREEN, 0.5)
        x1 = cx + (r_inner if is_major else r_inner + size * 0.01) * math.cos(ang)
        y1 = cy + (r_inner if is_major else r_inner + size * 0.01) * math.sin(ang)
        x2 = cx + r2 * math.cos(ang)
        y2 = cy + r2 * math.sin(ang)
        d.line([(x1, y1), (x2, y2)], fill=color + (255,), width=w)

    # 时针（指向 10 点方向，约 10:10）
    def hand(angle_deg, length_frac, width_frac, color):
        ang = math.radians(angle_deg - 90)
        lx = cx + size * length_frac * math.cos(ang)
        ly = cy + size * length_frac * math.sin(ang)
        d.line([(cx, cy), (lx, ly)], fill=color + (255,),
               width=max(2, int(size * width_frac)))

    hand(300, 0.22, 0.030, FG)      # 时针 -> 10 点
    hand(60, 0.32, 0.022, FG)       # 分针 -> 2 点
    hand(180, 0.33, 0.008, ACCENT)  # 秒针 -> 6 点

    # 中心圆点
    d.ellipse([cx - size * 0.02, cy - size * 0.02,
               cx + size * 0.02, cy + size * 0.02], fill=ACCENT + (255,))
    d.ellipse([cx - size * 0.008, cy - size * 0.008,
               cx + size * 0.008, cy + size * 0.008], fill=FG + (255,))

    return img


def main():
    img = draw_clock(SIZE)
    # 保存 png
    png_path = os.path.join(OUT_DIR, "MultiTimer_512.png")
    img.save(png_path)
    print("saved", png_path)

    # 多尺寸 png + ico
    sizes = [16, 24, 32, 48, 64, 128, 256]
    imgs = []
    for s in sizes:
        imgs.append(img.resize((s, s), Image.LANCZOS))
        imgs[-1].save(os.path.join(OUT_DIR, f"MultiTimer_{s}.png"))
    ico_path = os.path.join(OUT_DIR, "MultiTimer.ico")
    img.save(ico_path, sizes=[(s, s) for s in sizes])
    print("saved", ico_path)


if __name__ == "__main__":
    main()
