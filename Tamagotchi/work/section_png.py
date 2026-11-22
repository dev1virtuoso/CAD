#!/usr/bin/env python3
"""Annotated A-A cross-section (Y=0) with numbered call-outs."""
import json
from PIL import Image, ImageDraw, ImageFont

S = json.load(open('work/section_y0.json'))
SC = 11.0
W, H = 1280, 720
X0, Y0 = 640, 300
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
f = ImageFont.truetype(FONT, 16, index=0)
fs = ImageFont.truetype(FONT, 13, index=0)
fb = ImageFont.truetype(FONT, 21, index=0)
COL = {'front_cover': (35, 85, 155), 'back_cover': (35, 85, 155),
       'pcb': (25, 125, 75), 'comps': (55, 55, 65), 'buttons': (145, 75, 145)}


def T(x, z):
    return (X0 + x * SC, Y0 - z * SC)


img = Image.new('RGB', (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)
d.polygon([T(-41.03, 12.3), T(41.03, 12.3), T(41.03, -7.0), T(-41.03, -7.0)], fill=(231, 237, 246))
d.polygon([T(-37.85, 10.3), T(37.85, 10.3), T(37.85, -5.0), T(-37.85, -5.0)], fill=(252, 252, 255))

for name, polys in S.items():
    for p in polys:
        if len(p) >= 2:
            d.line([T(x, z) for x, z in p], fill=COL[name], width=2)

d.line([T(-46, 0), T(46, 0)], fill=(215, 215, 222), width=1)


def dim_v(x, z1, z2, label, col=(196, 90, 40), tx=None):
    px = T(x, 0)[0]
    y1, y2 = T(x, z1)[1], T(x, z2)[1]
    d.line([(px, y1), (px, y2)], fill=col, width=1)
    for yy in (y1, y2):
        d.line([(px - 4, yy), (px + 4, yy)], fill=col, width=1)
    d.text(((tx if tx is not None else px + 8), (y1 + y2) / 2 - 8), label, font=fs, fill=col)


def dim_h(z, x1, x2, label, col=(196, 90, 40), dy=0):
    py = T(0, z)[1]
    xa, xb = T(x1, 0)[0], T(x2, 0)[0]
    d.line([(xa, py), (xb, py)], fill=col, width=1)
    for xx in (xa, xb):
        d.line([(xx, py - 4), (xx, py + 4)], fill=col, width=1)
    d.text(((xa + xb) / 2 - 24, py + 4 + dy), label, font=fs, fill=col)


dim_h(13.4, -41.03, 41.03, '外殼 82.05', dy=-22)
dim_h(-8.2, -37.85, 37.85, '內腔 75.65')
dim_v(-45.5, 12.3, -7.0, '19.3', tx=96)
dim_v(44.6, 10.3, 1.6, '8.7')
dim_v(44.6, 1.6, 0.0, '1.6')
dim_v(44.6, 0.0, -5.0, '5.0')

# z-level ticks (short, no text) on the left
for gz in (10.2, 8.2, 1.6, 0.0, -8.0, -10.0):
    px, py = T(-41.03, gz)
    d.line([(px - 7, py), (px, py)], fill=(150, 150, 160), width=1)
d.text((96, T(0, 12.3)[1] - 22), 'z=+12.3（前表面）', font=fs, fill=(150, 150, 160))
d.text((96, T(0, 0)[1] + 8), 'z=0（PCB 背面／分模面）', font=fs, fill=(150, 150, 160))


def mark(n, x, z):
    px, py = T(x, z)
    d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(255, 255, 255), outline=(196, 90, 40), width=2)
    tw = d.textlength(str(n), font=fs)
    d.text((px - tw / 2, py - 7), str(n), font=fs, fill=(196, 90, 40))


mark(1, -30, 11.2)     # front wall
mark(2, -30, 6.0)      # front cavity
mark(3, -30, 0.8)      # pcb
mark(4, 26, -2.5)      # back cavity
mark(5, 26, -6.0)      # back wall
mark(6, 0.0, 6.6)      # screen module
mark(7, 13.0, 9.6)     # window / bezel

d.text((24, 18), 'A-A 剖面（穿過螢幕中心 Y=0）｜單位 mm', font=fb, fill=(25, 30, 40))

notes = [
    (1, '前殼壁厚 2.0 mm'),
    (2, '前腔淨空 8.7 mm（螢幕模組上方餘 3.76 mm）'),
    (3, 'PCB 厚 1.6 mm，壓在 3 個卡扣柱上（免螺絲）'),
    (4, '後腔 5.0 mm（走線／焊點空間；PCB 沒有電池）'),
    (5, '後殼壁厚 2.0 mm'),
    (6, 'SSD1306 模組頂面 z≈6.54 mm'),
    (7, '螢幕窗 24.0 × 14.2，內側斜邊至 25.4 × 15.6'),
    (8, '前後殼卡扣：4 個 L 形鉤 + 內壁凹槽，免螺絲'),
]
for i, (n, txt) in enumerate(notes):
    col_i = i % 2
    row = i // 2
    x = 24 + col_i * 620
    y = 520 + row * 30
    d.text((x, y), f'{n}', font=fs, fill=(196, 90, 40))
    d.text((x + 16, y), txt, font=fs, fill=(45, 45, 55))

d.text((24, 640), '■ 前/後殼   ■ PCB   ■ 元件   ■ 按鍵', font=f, fill=(60, 60, 70))
d.text((24, 668), '外形 82.05 × 97.28 × 19.3 mm ｜ 板邊單邊間隙 2.8 mm ｜ 內腔 75.65 × 90.88 mm',
       font=fs, fill=(95, 95, 105))
d.text((24, 690), '預估重量（PLA、3 層牆、20% 填充）約 23–27 g', font=fs, fill=(95, 95, 105))
img.save('work/section_drawing.png')
print('ok')
