#!/usr/bin/env python3
"""2-D fit map: PCB features vs shell cut-outs (shell frame, Y up)."""
import json, math
from PIL import Image, ImageDraw, ImageFont

P = json.load(open('work/profile.json'))
CX, CY = P['meta']['cx'], P['meta']['cy']
S = 8.0
W, H = int(120 * S), int(130 * S)
OX, OY = 60.0, 62.0          # shell-frame centre in image mm coords
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
try:
    f14 = ImageFont.truetype(FONT, 15, index=0)
    f11 = ImageFont.truetype(FONT, 12, index=0)
    f18 = ImageFont.truetype(FONT, 19, index=0)
except Exception:
    f14 = f11 = f18 = ImageFont.load_default()


def T(x, y):
    return ((x + OX) * S, (OY - y) * S)


img = Image.new('RGB', (W, H), (255, 255, 255))
d = ImageDraw.Draw(img, 'RGBA')

# grid 10 mm
for gx in range(-55, 55, 10):
    d.line([T(gx, -60), T(gx, 60)], fill=(238, 238, 242))
for gy in range(-60, 60, 10):
    d.line([T(-55, gy), T(55, gy)], fill=(238, 238, 242))


def poly(pts, fill=None, outline=None, width=2):
    d.polygon([T(x, y) for x, y in pts], fill=fill, outline=outline, width=width)


poly(P['off6.0'], fill=(247, 244, 236), outline=(210, 150, 60), width=2)
poly(P['off2.8'], fill=(236, 244, 232), outline=(90, 150, 100), width=2)
poly(P['board'], fill=(232, 238, 246), outline=(50, 90, 160), width=2)


def S2(x, y):
    return (x - CX, CY - y)


def rrect(cx, cy, w, h, color, width=2, fill=None):
    x0, y0 = T(cx - w / 2, cy + h / 2)
    x1, y1 = T(cx + w / 2, cy - h / 2)
    d.rounded_rectangle([x0, y0, x1, y1], radius=2 * S, outline=color, width=width, fill=fill)


# PCB components
u1 = S2(145.542, 78.232)
rrect(u1[0], u1[1], 22.52, 18.0, (230, 140, 30), 2, (250, 235, 220))
d.text(T(u1[0] - 9, u1[1] + 11.5), 'ESP32-C3 SuperMini', font=f11, fill=(180, 100, 20))
u2 = S2(144.526, 103.58)
rrect(u2[0], u2[1], 27.3, 27.8, (40, 110, 190), 2, (225, 235, 248))
rrect(u2[0], u2[1], 26.7, 19.26, (90, 130, 190), 1)
aa = S2(144.526, 103.58)
rrect(aa[0], aa[1], 21.744, 10.864, (30, 80, 150), 2, (205, 222, 245))
d.text(T(u2[0] + 6, u2[1] + 12.5), 'SSD1306', font=f11, fill=(20, 70, 140))
d.text(T(aa[0] - 10.5, aa[1] - 1.2), 'AA', font=f11, fill=(20, 70, 140))

sw = [(123.444, 123.952), (137.668, 123.952), (153.518, 123.952), (169.164, 123.952)]
for i, (x, y) in enumerate(sw):
    p = S2(x, y)
    rrect(p[0], p[1], 4.5, 5.2, (200, 60, 120), 2, (250, 225, 236))
    d.text(T(p[0] - 3.5, p[1] - 5.8), f'SW{i+1}', font=f11, fill=(170, 40, 100))
led = S2(145.288, 122.936)
rrect(led[0], led[1], 2.0, 1.25, (200, 40, 40), 2, (250, 220, 220))
d.text(T(led[0] + 2.0, led[1] - 1.0), 'D1', font=f11, fill=(170, 30, 30))
for x, y in [(121.007, 131.064), (126.05, 131.064), (134.724, 131.064), (140.274, 131.064),
             (145.288, 131.064), (150.876, 131.064), (155.956, 131.064), (165.608, 131.064),
             (170.688, 131.064)]:
    p = S2(x, y)
    rrect(p[0], p[1], 2.0, 1.25, (140, 140, 140), 1, (225, 225, 225))

# screws / posts
for i, (x, y) in enumerate([(145.288, 65.024), (117.348, 96.012), (175.768, 113.792)]):
    p = S2(x, y)
    r = 6.4 / 2
    d.ellipse([T(p[0]-r, p[1]+r), T(p[0]+r, p[1]-r)], outline=(120, 120, 130), width=2)
    r = 1.6
    d.ellipse([T(p[0]-r, p[1]+r), T(p[0]+r, p[1]-r)], outline=(60, 60, 70), width=2)
    d.line([T(p[0]-2.4, p[1]), T(p[0]+2.4, p[1])], fill=(60, 60, 70), width=1)
    d.line([T(p[0], p[1]-2.4), T(p[0], p[1]+2.4)], fill=(60, 60, 70), width=1)
    d.text(T(p[0]+4.2, p[1]+2.0), f'S{i+1}', font=f11, fill=(90, 90, 100))

# screen window & bezel
w = S2(144.526, 102.50)
rrect(w[0], w[1], 27.5, 18.5, (30, 130, 90), 2)
d.rounded_rectangle([T(w[0]-12, w[1]+7.1), T(w[0]+12, w[1]-7.1)], radius=2.2*S, outline=(20, 120, 80), width=3)
d.text(T(w[0] - 11.5, w[1] + 8.2), 'WINDOW 24.0×14.2', font=f11, fill=(20, 110, 75))

# button holes + counterbores
for x, y in sw:
    p = S2(x, y)
    for r, col, wd in [(5.2, (150, 40, 90), 2), (4.8, (120, 20, 70), 2)]:
        d.ellipse([T(p[0]-r, p[1]+r), T(p[0]+r, p[1]-r)], outline=col, width=wd)
# led hole
for r, col in [(1.2, (170, 40, 40))]:
    d.ellipse([T(led[0]-r, led[1]+r), T(led[0]+r, led[1]-r)], outline=col, width=2)

# usb-c port + slot marker
up = S2(132.78, 78.23)
rrect(up[0] + 3.6, up[1], 7.35, 8.94, (120, 60, 200), 2, (238, 230, 250))
d.text(T(up[0] + 4.5, up[1] + 6.2), 'USB-C', font=f11, fill=(100, 50, 180))
px0, py = T(up[0], up[1])
d.line([px0, py, px0 - 26, py], fill=(120, 60, 200), width=2)
d.polygon([(px0-26, py-5), (px0-32, py), (px0-26, py+5)], fill=(120, 60, 200))
d.text(T(up[0] - 27, up[1] - 7.0), 'CHARGE SLOT', font=f11, fill=(100, 50, 180))

# dims
d.line([T(-35.05, -46.5), T(35.05, -46.5)], fill=(60, 60, 70), width=1)
d.text(T(-8, -49.5), 'PCB 70.10 × 85.33', font=f11, fill=(60, 60, 70))

# legend
lx, ly = T(-56, 57)
items = [((50, 90, 160), 'PCB 輪廓 / board outline (70.10 × 85.33)'),
         ((210, 150, 60), '外殼外輪廓 / shell outer (+6.0 → 82.05 × 97.28)'),
         ((90, 150, 100), '內腔 / cavity (+2.8, 單邊間隙 2.8 mm)'),
         ((20, 120, 80), '螢幕窗 24.0×14.2（斜邊至 25.4×15.6）'),
         ((150, 40, 90), '按鍵 φ9.6 直通孔（開關直接外露）+ φ10.4 導引口'),
         ((170, 40, 40), 'LED 孔 φ2.4（無沉孔）'),
         ((120, 120, 130), 'M3 螺絲柱 φ6.4 / 孔 φ3.2（PCB）'),
         ((120, 60, 200), 'USB-C 充電開口（側壁）')]
for i, (c, txt) in enumerate(items):
    y = ly + i * 17
    d.rectangle([lx, y, lx + 12, y + 12], fill=c)
    d.text((lx + 18, y - 2), txt, font=f11, fill=(40, 40, 50))

d.text(T(-20, 60), 'Tamagotchi 蛋形外殼 — 開孔對位圖 (mm)', font=f18, fill=(20, 20, 30))
img.save('work/fit_map.png')
print('saved', img.size)
