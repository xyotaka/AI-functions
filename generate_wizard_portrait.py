"""Generate a 144x144 SNES-era JRPG wizard portrait using pixel_to_image."""
import math
from pixel_to_image import create_image

W, H = 144, 144

# Color palette
BG_DARK = [25, 20, 50, 255]
BG_MED = [35, 28, 65, 255]
BG_LIGHT = [45, 36, 80, 255]

SKIN = [255, 218, 185, 255]
SKIN_LT = [255, 228, 200, 255]
SKIN_HI = [255, 235, 215, 255]
SKIN_SH = [220, 180, 150, 255]
SKIN_DSH = [195, 155, 125, 255]

HAIR_LT = [255, 235, 130, 255]
HAIR = [240, 210, 90, 255]
HAIR_MD = [220, 185, 65, 255]
HAIR_DK = [190, 155, 45, 255]
HAIR_DSH = [160, 130, 35, 255]

EYE_WHITE = [240, 240, 245, 255]
EYE_IRIS = [50, 120, 200, 255]
EYE_IRIS_LT = [80, 155, 230, 255]
EYE_PUPIL = [20, 20, 40, 255]
EYE_LINE = [60, 40, 30, 255]
LASH = [40, 25, 15, 255]
BROW = [180, 140, 50, 255]

LIP = [230, 140, 130, 255]
LIP_DK = [200, 110, 105, 255]
LIP_HI = [245, 175, 165, 255]
NOSE_SH = [235, 190, 160, 255]

HAT_MAIN = [60, 35, 120, 255]
HAT_DK = [40, 22, 85, 255]
HAT_LT = [80, 50, 150, 255]
HAT_HI = [100, 70, 175, 255]
HAT_BAND = [200, 170, 60, 255]
HAT_BAND_LT = [230, 200, 90, 255]
HAT_BAND_DK = [170, 140, 40, 255]
HAT_GEM = [100, 220, 255, 255]
HAT_GEM_HI = [180, 240, 255, 255]
HAT_GEM_DK = [40, 140, 200, 255]

ROBE = [70, 40, 130, 255]
ROBE_LT = [90, 55, 160, 255]
ROBE_DK = [50, 28, 95, 255]
ROBE_HI = [110, 75, 180, 255]
COLLAR_GOLD = [210, 180, 70, 255]
COLLAR_GOLD_LT = [240, 215, 100, 255]
COLLAR_GOLD_DK = [175, 145, 45, 255]

STAR = [255, 255, 200, 255]
SPARKLE = [200, 220, 255, 200]

OUTLINE = [30, 20, 15, 255]

# Initialize canvas with background gradient
grid = []
for y in range(H):
    row = []
    for x in range(W):
        t = y / H
        r = int(BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * t)
        g = int(BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * t)
        b = int(BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * t)
        row.append([r, g, b, 255])
    grid.append(row)

def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        grid[y][x] = list(c)

def fill_ellipse(cx, cy, rx, ry, color):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                put(x, y, color)

def fill_rect(x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            put(x, y, color)

def fill_tri(x1, y1, x2, y2, x3, y3, color):
    """Fill a triangle using barycentric coordinates."""
    min_x = max(0, min(x1, x2, x3))
    max_x = min(W - 1, max(x1, x2, x3))
    min_y = max(0, min(y1, y2, y3))
    max_y = min(H - 1, max(y1, y2, y3))
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
            if d == 0:
                continue
            a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / d
            b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / d
            c = 1 - a - b
            if a >= 0 and b >= 0 and c >= 0:
                put(x, y, color)

def outline_ellipse(cx, cy, rx, ry, color, thickness=1):
    for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
        for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if abs(d - 1.0) < thickness / max(rx, ry):
                put(x, y, color)

def draw_line(x1, y1, x2, y2, color, thickness=1):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        t = i / steps
        cx = x1 + dx * t
        cy = y1 + dy * t
        for tx in range(-thickness // 2, thickness // 2 + 1):
            for ty in range(-thickness // 2, thickness // 2 + 1):
                put(int(cx + tx), int(cy + ty), color)

# ── Background sparkles ──
import random
random.seed(42)
for _ in range(30):
    sx = random.randint(0, W - 1)
    sy = random.randint(0, H - 1)
    put(sx, sy, SPARKLE)

# ── HAIR (back layer - long flowing hair) ──
# Hair flows behind and to the left (she faces right)
# Back hair mass
fill_ellipse(62, 68, 38, 42, HAIR_DK)
fill_ellipse(60, 65, 36, 40, HAIR_MD)
fill_ellipse(58, 62, 34, 38, HAIR)

# Long flowing hair strands going down-left
for i in range(8):
    base_x = 35 + i * 5
    for y in range(75, 140):
        wave = int(math.sin((y - 75) * 0.08 + i * 0.5) * (3 + i * 0.3))
        x = base_x + wave - (y - 75) // 6
        shade = HAIR_DK if i % 3 == 0 else (HAIR_MD if i % 3 == 1 else HAIR)
        for dx in range(-2, 3):
            put(x + dx, y, shade)

# Hair highlight strands
for i in range(5):
    base_x = 40 + i * 7
    for y in range(70, 135):
        wave = int(math.sin((y - 70) * 0.08 + i * 0.7) * (2 + i * 0.2))
        x = base_x + wave - (y - 70) // 7
        put(x, y, HAIR_LT)

# ── NECK ──
fill_rect(68, 95, 82, 110, SKIN)
fill_rect(68, 95, 72, 110, SKIN_SH)
fill_rect(78, 95, 82, 105, SKIN_LT)

# ── CLOTHING (shoulders and collar) ──
# Shoulders
fill_ellipse(75, 120, 40, 18, ROBE_DK)
fill_ellipse(75, 118, 38, 16, ROBE)
fill_ellipse(80, 116, 30, 12, ROBE_LT)

# Extended robe to bottom
fill_rect(35, 120, 115, 143, ROBE_DK)
fill_rect(38, 118, 112, 143, ROBE)

# Robe shading
for y in range(118, 144):
    for x in range(38, 112):
        if x < 55:
            put(x, y, ROBE_DK)
        elif x > 100:
            put(x, y, ROBE_DK)

# Robe highlights
for y in range(120, 140):
    for x in range(70, 92):
        if (x + y) % 8 == 0:
            put(x, y, ROBE_HI)

# Gold collar / necklace
draw_line(50, 112, 75, 108, COLLAR_GOLD, 2)
draw_line(75, 108, 100, 112, COLLAR_GOLD, 2)
draw_line(50, 113, 75, 109, COLLAR_GOLD_LT, 1)
draw_line(75, 109, 100, 113, COLLAR_GOLD_DK, 1)

# Collar ornamental points
fill_tri(73, 108, 77, 108, 75, 118, COLLAR_GOLD)
fill_ellipse(75, 115, 3, 3, HAT_GEM)
put(75, 114, HAT_GEM_HI)
put(74, 115, HAT_GEM_HI)

# Gold trim lines on robe
for y in range(120, 144, 8):
    draw_line(45, y, 55, y + 3, COLLAR_GOLD_DK, 1)
    draw_line(95, y, 105, y + 3, COLLAR_GOLD_DK, 1)

# Star emblems on robe
for sx, sy in [(50, 130), (98, 128), (65, 138), (88, 140)]:
    put(sx, sy, STAR)
    put(sx - 1, sy, COLLAR_GOLD)
    put(sx + 1, sy, COLLAR_GOLD)
    put(sx, sy - 1, COLLAR_GOLD)
    put(sx, sy + 1, COLLAR_GOLD)

# ── FACE ──
# Head shape (facing right, so center shifted right slightly)
face_cx, face_cy = 72, 68
fill_ellipse(face_cx, face_cy, 24, 28, OUTLINE)
fill_ellipse(face_cx, face_cy, 23, 27, SKIN)

# Face shading - left side darker (facing right)
for y in range(42, 96):
    for x in range(48, 96):
        dx = x - face_cx
        dy = y - face_cy
        if (dx / 23) ** 2 + (dy / 27) ** 2 <= 1.0:
            if dx < -10:
                put(x, y, SKIN_SH)
            elif dx < -16:
                put(x, y, SKIN_DSH)
            elif dx > 12:
                put(x, y, SKIN_LT)
            elif dx > 16:
                put(x, y, SKIN_HI)

# Right cheek highlight (facing right)
fill_ellipse(82, 74, 6, 5, SKIN_HI)
fill_ellipse(84, 73, 4, 3, SKIN_LT)

# ── NOSE (profile-ish, pointing right) ──
for y in range(66, 76):
    nose_x = 88 + (y - 66) // 3
    put(nose_x, y, NOSE_SH)
    put(nose_x + 1, y, SKIN_SH)
# Nose tip
put(91, 74, SKIN_SH)
put(92, 74, NOSE_SH)
put(91, 75, NOSE_SH)
# Nostril hint
put(89, 76, SKIN_DSH)

# ── EYES ──
# Right eye (closer, larger since facing right) - at about x=80
r_eye_cx, r_eye_cy = 82, 64
fill_ellipse(r_eye_cx, r_eye_cy, 7, 5, EYE_WHITE)
# Iris
fill_ellipse(r_eye_cx + 2, r_eye_cy, 4, 4, EYE_IRIS)
fill_ellipse(r_eye_cx + 3, r_eye_cy - 1, 2, 2, EYE_IRIS_LT)
# Pupil
fill_ellipse(r_eye_cx + 2, r_eye_cy, 2, 2, EYE_PUPIL)
# Highlight
put(r_eye_cx + 4, r_eye_cy - 2, [255, 255, 255, 255])
put(r_eye_cx + 3, r_eye_cy - 2, [255, 255, 255, 255])
# Eye outline
outline_ellipse(r_eye_cx, r_eye_cy, 7, 5, EYE_LINE)
# Upper lash (thicker)
for x in range(r_eye_cx - 6, r_eye_cx + 7):
    for dy in range(-1, 1):
        put(x, r_eye_cy - 4 + dy, LASH)
# Lower lash line
for x in range(r_eye_cx - 4, r_eye_cx + 6):
    put(x, r_eye_cy + 5, EYE_LINE)
# Lash flicks
put(r_eye_cx + 7, r_eye_cy - 5, LASH)
put(r_eye_cx + 8, r_eye_cy - 6, LASH)
put(r_eye_cx - 7, r_eye_cy - 4, LASH)

# Left eye (further away, smaller)
l_eye_cx, l_eye_cy = 64, 65
fill_ellipse(l_eye_cx, l_eye_cy, 5, 4, EYE_WHITE)
fill_ellipse(l_eye_cx + 1, l_eye_cy, 3, 3, EYE_IRIS)
fill_ellipse(l_eye_cx + 2, l_eye_cy - 1, 1, 1, EYE_IRIS_LT)
fill_ellipse(l_eye_cx + 1, l_eye_cy, 1, 1, EYE_PUPIL)
put(l_eye_cx + 3, l_eye_cy - 2, [255, 255, 255, 255])
outline_ellipse(l_eye_cx, l_eye_cy, 5, 4, EYE_LINE)
for x in range(l_eye_cx - 4, l_eye_cx + 5):
    put(x, l_eye_cy - 4, LASH)
put(l_eye_cx - 5, l_eye_cy - 3, LASH)

# ── EYEBROWS ──
# Right brow (arched, elegant)
for i in range(14):
    x = r_eye_cx - 6 + i
    y_off = -int(math.sin(i / 13 * math.pi) * 3)
    put(x, r_eye_cy - 8 + y_off, BROW)
    put(x, r_eye_cy - 9 + y_off, BROW)

# Left brow
for i in range(10):
    x = l_eye_cx - 4 + i
    y_off = -int(math.sin(i / 9 * math.pi) * 2)
    put(x, l_eye_cy - 7 + y_off, BROW)
    put(x, l_eye_cy - 8 + y_off, BROW)

# ── MOUTH ──
mouth_cx, mouth_cy = 78, 82
# Upper lip
for x in range(mouth_cx - 5, mouth_cx + 6):
    curve = int(math.sin((x - mouth_cx + 5) / 10 * math.pi) * 1.5)
    put(x, mouth_cy - curve, LIP_DK)

# Lower lip
for x in range(mouth_cx - 4, mouth_cx + 5):
    curve = int(math.sin((x - mouth_cx + 4) / 8 * math.pi) * 2)
    put(x, mouth_cy + 1 + curve, LIP)
    if curve > 0:
        put(x, mouth_cy + curve, LIP)

# Lip highlight
put(mouth_cx + 1, mouth_cy + 2, LIP_HI)
put(mouth_cx + 2, mouth_cy + 2, LIP_HI)

# Mouth line
for x in range(mouth_cx - 4, mouth_cx + 5):
    put(x, mouth_cy, LIP_DK)

# ── HAIR (front layer) ──
# Bangs swept to the right
for y in range(38, 62):
    for x in range(50, 96):
        # Wavy bangs shape
        wave = int(math.sin((x - 50) * 0.12) * 3)
        top_line = 38 + (x - 50) * 0.3 + wave
        if y < top_line + 8 and y >= top_line:
            depth = y - top_line
            if depth < 2:
                put(x, y, HAIR_LT)
            elif depth < 5:
                put(x, y, HAIR)
            else:
                put(x, y, HAIR_MD)

# Side hair on left (facing right, hair falls on left side)
for y in range(55, 100):
    for x in range(46, 58):
        if ((x - 50) / 8) ** 2 + ((y - 72) / 30) ** 2 <= 1.0:
            wave = int(math.sin(y * 0.15) * 2)
            xx = x + wave
            if xx < 52:
                put(xx, y, HAIR_DK)
            elif xx < 55:
                put(xx, y, HAIR_MD)
            else:
                put(xx, y, HAIR)

# Hair strands over forehead
for i in range(6):
    start_x = 55 + i * 6
    for y in range(40, 55):
        wave = int(math.sin((y + i * 2) * 0.2) * 1.5)
        x = start_x + wave + (y - 40) // 4
        if i % 2 == 0:
            put(x, y, HAIR_LT)
        else:
            put(x, y, HAIR)

# ── WIZARD HAT ──
# Hat brim
fill_ellipse(70, 42, 32, 6, OUTLINE)
fill_ellipse(70, 42, 31, 5, HAT_DK)
fill_ellipse(70, 43, 30, 4, HAT_MAIN)

# Hat cone (tall, pointed, slightly tilted right)
hat_base_y = 42
hat_tip_x, hat_tip_y = 82, -5
for y in range(hat_tip_y, hat_base_y):
    t = (y - hat_tip_y) / (hat_base_y - hat_tip_y)
    half_w = t * 22
    cx = hat_tip_x + (70 - hat_tip_x) * t
    for x in range(int(cx - half_w), int(cx + half_w) + 1):
        # Shading
        rel = (x - (cx - half_w)) / max(half_w * 2, 1)
        if rel < 0.3:
            put(x, y, HAT_DK)
        elif rel < 0.6:
            put(x, y, HAT_MAIN)
        elif rel < 0.8:
            put(x, y, HAT_LT)
        else:
            put(x, y, HAT_HI)

# Hat outline
for y in range(hat_tip_y, hat_base_y):
    t = (y - hat_tip_y) / (hat_base_y - hat_tip_y)
    half_w = t * 22
    cx = hat_tip_x + (70 - hat_tip_x) * t
    put(int(cx - half_w), y, OUTLINE)
    put(int(cx + half_w), y, OUTLINE)

# Hat band
band_y = 38
for y in range(band_y, band_y + 4):
    t = (y - hat_tip_y) / (hat_base_y - hat_tip_y)
    half_w = t * 22
    cx = hat_tip_x + (70 - hat_tip_x) * t
    for x in range(int(cx - half_w) + 1, int(cx + half_w)):
        rel = (x - (cx - half_w)) / max(half_w * 2, 1)
        if rel < 0.3:
            put(x, y, HAT_BAND_DK)
        elif rel > 0.7:
            put(x, y, HAT_BAND_LT)
        else:
            put(x, y, HAT_BAND)

# Gem on hat band (center)
gem_cx, gem_cy = 73, 39
fill_ellipse(gem_cx, gem_cy, 3, 2, HAT_GEM_DK)
fill_ellipse(gem_cx, gem_cy, 2, 2, HAT_GEM)
put(gem_cx - 1, gem_cy - 1, HAT_GEM_HI)
put(gem_cx, gem_cy - 1, HAT_GEM_HI)

# Stars/sparkles on hat
hat_stars = [(65, 20), (78, 10), (58, 28), (85, 25), (72, 5), (90, 18)]
for sx, sy in hat_stars:
    t = (sy - hat_tip_y) / (hat_base_y - hat_tip_y)
    half_w = t * 22
    cx = hat_tip_x + (70 - hat_tip_x) * t
    if abs(sx - cx) < half_w - 2:
        put(sx, sy, STAR)
        put(sx - 1, sy, [200, 200, 150, 180])
        put(sx + 1, sy, [200, 200, 150, 180])
        put(sx, sy - 1, [200, 200, 150, 180])
        put(sx, sy + 1, [200, 200, 150, 180])

# Hat tip curl
for i in range(15):
    angle = i * 0.3
    x = int(hat_tip_x + math.cos(angle) * (i * 0.8))
    y = int(hat_tip_y + math.sin(angle) * (i * 0.4) - i * 0.3)
    put(x, y, HAT_LT)
    put(x, y + 1, HAT_MAIN)

# ── EAR (visible on right side) ──
ear_cx, ear_cy = 93, 68
fill_ellipse(ear_cx, ear_cy, 4, 6, SKIN)
fill_ellipse(ear_cx + 1, ear_cy, 2, 4, SKIN_SH)
# Earring
put(ear_cx, ear_cy + 6, COLLAR_GOLD)
put(ear_cx, ear_cy + 7, COLLAR_GOLD_LT)
put(ear_cx, ear_cy + 8, HAT_GEM)
put(ear_cx - 1, ear_cy + 8, HAT_GEM_DK)

# ── MAGICAL SPARKLE EFFECTS ──
sparkle_positions = [(100, 55), (105, 70), (110, 45), (30, 90), (115, 85),
                     (25, 60), (120, 60), (108, 100), (20, 105)]
for sx, sy in sparkle_positions:
    put(sx, sy, [200, 220, 255, 255])
    put(sx - 1, sy, [150, 180, 255, 150])
    put(sx + 1, sy, [150, 180, 255, 150])
    put(sx, sy - 1, [150, 180, 255, 150])
    put(sx, sy + 1, [150, 180, 255, 150])

# ── Generate the image ──
out = create_image(grid, output_path="wizard_portrait.png", scale=3)
print(f"Saved: {out}")
