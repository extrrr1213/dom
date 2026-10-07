"""Планировка на участке 6 сот. по объявлению (≈593 м² по сторонам): дом DP-Module «Модерн 105» + мастер-модуль.
Дом ближе к дороге (терраса у дороги в 5 м от забора — запас под красную линию улицы), длинная ось З–В,
мастер-блок с юга, жилая зона у дороги; на западе — спортплощадка 7×14 м (парный корт для бадминтона) и детская
зона, на юге — бассейн и купель, лужайка у гостиной; парковка на 2 авто РЯДОМ в юго-восточной нише,
бетон до входной террасы, откатные ворота с зоной отката, калитка за ней.
Выбран и доработан по итогам сравнения 4 вариантов (дом у дороги / у севера / в глубине / «сначала бадминтон»)."""
import math

AB, BC, CD, DA = 32.6, 18.5, 30.7, 19.0  # юг (низ), дорога (восток), север (верх), запад (лево)
SETBACK = 3.0          # отступ дома и террас от всех границ


def shape(a):
    A, B = (0.0, 0.0), (AB, 0.0)
    D = (DA * math.cos(a), DA * math.sin(a))
    dx, dy = B[0] - D[0], B[1] - D[1]
    L = math.hypot(dx, dy)
    # C: |BC|=BC, |DC|=CD, по левую сторону от D->B (выпуклый четырёхугольник)
    x = (CD**2 - BC**2 + L**2) / (2 * L)
    h = math.sqrt(max(CD**2 - x**2, 0))
    ux, uy = dx / L, dy / L
    C = (D[0] + ux * x - uy * h, D[1] + uy * x + ux * h)
    return [A, B, C, D]


def f1(v):
    """Число с одним знаком, половинки — вверх (11.25 → 11.3)."""
    return f"{math.floor(v * 10 + 0.5 + 1e-9) / 10:.1f}"


def area(p):
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2


# угол при юго-западном углу A снят с чертежа объявления (макс. возможная площадь по сторонам — 592.7 м²)
best_a = math.radians(85.9)
P = shape(best_a)
A, B, C, D = P


def inset(poly, d):
    n = len(poly)
    lines = []
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L  # внутрь для CCW
        lines.append(((p[0] + nx * d, p[1] + ny * d), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    return out


def inside(poly, pt):
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        if (q[0] - p[0]) * (pt[1] - p[1]) - (q[1] - p[1]) * (pt[0] - p[0]) < -1e-9:
            return False
    return True


BUILD = inset(P, SETBACK)


def line_x_at_y(p, q, y):
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def line_y_at_x(p, q, x):
    return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0])


def x_road(y):   # x забора у дороги (восток) на высоте y
    return line_x_at_y(B, C, y)


def x_west(y):   # x западного забора
    return line_x_at_y(A, D, y)


def y_north(x):  # y северного забора
    return line_y_at_x(C, D, x)


# DP-Module «Модерн 105»: 14 × 7.5 м (6 модулей 7 × 2.5 м) + 1 модуль 7 × 2.5 м под мастер-спальню → Г, 122.5 м².
# Локальные координаты дома: X — вдоль длинной стороны (0 = торец в сад, 14 = торец к дороге), Y — поперёк (0 = юг).
# Мастер-блок — с юга (солнечная сторона, рядом купель), жилая зона — у дороги; 7.5-метровая часть у дороги
# прижата к северу, под ней (на юго-востоке) — ниша 8 м под парковку на 2 авто рядом.
HOUSE_L = 14.0
OUTLINE = [(0, 0), (7, 0), (7, 2.5), (14, 2.5), (14, 10), (0, 10)]  # Г-образный контур, 122.5 м²

ROOMS = [
    # мастер-блок (доп. модуль) — с юга
    ("Мастер-спальня", 0.0, 0.0, 3.6, 4.7, "#cfe0f3"),
    ("Гардеробная", 3.6, 2.5, 7.0, 4.7, "#e6e0f0"),
    ("С/у мастер", 3.6, 0.0, 7.0, 2.5, "#d6f0ee"),
    # коридор между спальнями -> выход в сад
    ("Коридор", 0.0, 4.7, 7.0, 6.0, "#eeeeee"),
    ("Спальня", 0.0, 6.0, 3.6, 10.0, "#dfe9f5"),
    ("Детская", 3.6, 6.0, 7.0, 10.0, "#f6e0ea"),
    # общая зона (вход — с террасы у дороги)
    ("Холл", 7.0, 4.7, 9.5, 7.0, "#eeeeee"),
    ("Санузел", 7.0, 2.5, 9.5, 4.7, "#d6f0ee"),
    ("Кухня-столовая", 7.0, 7.0, 14.0, 10.0, "#fde7c4"),
    ("Гостиная", 9.5, 2.5, 14.0, 7.0, "#fbf1d6"),
]
GARDEN_T = 2.5   # садовая терраса глубже прежних 2 м: летняя столовая (25 м²)
TERRACES = [
    ("терраса", 14.0, 2.5, 15.5, 10.0),        # у дороги, во всю стену гостиной и кухни-столовой (вход)
    ("терраса", -GARDEN_T, 0.0, 0.0, 10.0),    # в сад, во всю 10-метровую стену (мастер-спальня, коридор, спальня)
]
DOORS = [("вход", 14.0, 6.2, 14.75, 5.0), ("в сад", 0.0, 5.35, -GARDEN_T / 2, 4.1),
         ("к купели", 3.0, 0.0, 3.0, 0.45)]   # дверь из мастер-спальни на юг (к бассейну и купели)
HOUSE_BLOCKS = [(0, 2.5, 14, 10), (0, 0, 7, 2.5)]


def overlap(p1, p2, gap=0.0):
    """Пересекаются ли два выпуклых многоугольника (с зазором gap) — теорема о разделяющей оси."""
    for poly in (p1, p2):
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            nx, ny = y1 - y2, x2 - x1
            L = math.hypot(nx, ny)
            nx, ny = nx / L, ny / L
            a = [x * nx + y * ny for x, y in p1]
            b = [x * nx + y * ny for x, y in p2]
            if max(a) + gap <= min(b) or max(b) + gap <= min(a):
                return False
    return True


def seg_dist(p, a, b):
    ex, ey = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / (ex * ex + ey * ey)))
    return math.hypot(p[0] - a[0] - ex * t, p[1] - a[1] - ey * t)


def poly_gap(p1, p2):
    """Минимальный зазор между непересекающимися многоугольниками."""
    return min(min(seg_dist(p, q[i], q[(i + 1) % len(q)]) for p in s for i in range(len(q)))
               for s, q in ((p1, p2), (p2, p1)))


# дом ставим параллельно южной границе (32.6 м): длинная ось З–В
def place(xe, y0):
    return lambda X, Y: (xe - (HOUSE_L - X), y0 + Y)


def corners(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def fits(xe, y0):
    loc = place(xe, y0)
    pts = [loc(*p) for p in OUTLINE] + [loc(*c) for t in TERRACES for c in corners(*t[1:])]
    return all(inside(BUILD, p) for p in pts)


def dist_to_line(p, a, b):
    return abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / math.hypot(b[0] - a[0], b[1] - a[1])


def max_xe(y0, lo=22.0, hi=32.0):
    """Самое восточное положение торца дома при данном y0 (бисекция, шаг вниз до 0.01 м)."""
    if not fits(lo, y0):
        return None
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if fits(m, y0) else (lo, m)
    return math.floor(lo * 100) / 100


# положение дома: терраса у дороги в ROAD_GAP от забора (СП 42.13330: жилой дом ≥5 м от красной линии улицы —
# запас, если по ГПЗУ дорога окажется улицей; +0.2 м: угол участка снят с картинки, ошибка 1° ≈ 0.28 м у дороги),
# северная стена в NORTH_GAP от северного забора (0.2 м запаса к отступу 3 м; уточнить по межевому плану)
ROAD_GAP, NORTH_GAP = 5.2, 3.2
xe, hy = 26.0, 5.0
for _ in range(60):
    loc = place(xe, hy)
    tops = [loc(X, 10.0) for X in (-GARDEN_T, 0.0, 14.0, 15.5)]
    hy += min(dist_to_line(p, C, D) for p in tops) - NORTH_GAP
    xe += min(dist_to_line(place(xe, hy)(*c), B, C) for c in corners(*TERRACES[0][1:])) - ROAD_GAP
assert fits(xe, hy), "дом с террасами вне пятна застройки"
HX0, HY0 = xe - HOUSE_L, hy   # x торца дома в сад, y южной стены мастер-блока (дальше НЕ переиспользуются)
print(f"дом: торец у дороги x = {xe:.2f}, юг дома y = {HY0:.2f}")
local = place(xe, HY0)


def lrect(x0, y0, x1, y1):
    return [local(x0, y0), local(x1, y0), local(x1, y1), local(x0, y1)]


def xyrect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle_poly(cx, cy, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


HOUSE = [local(*p) for p in OUTLINE]
HOUSE_AREA = area(HOUSE)

# ---------- парковка: 2 авто РЯДОМ в юго-восточной нише, бетон от южного забора, въезд через ворота с дороги ----------
PARK_D = 6.5            # глубина от забора у дороги (у северного края; у южного чуть больше — забор наклонный)
park_y1 = HY0 + 2.5     # бетон от южного забора до края входной террасы (южная стена гостиной)
PARK_W = park_y1        # ширина вдоль дороги — 2 места рядом
park_x0 = x_road(park_y1) - PARK_D
PARK = [(park_x0, 0.0), B, (x_road(park_y1), park_y1), (park_x0, park_y1)]
PARK_D_MAX = B[0] - park_x0
print(f"парковка: {PARK_W:g} × {PARK_D:g}–{PARK_D_MAX:.2f} м = {area(PARK):.1f} м² (2 места рядом по {PARK_W / 2:g} м); "
      f"зазор до стены гостиной {poly_gap(PARK, lrect(*HOUSE_BLOCKS[0])):.2f} м")

# ---------- жизнь на участке (абсолютные координаты участка, м) ----------
TW = HX0 - GARDEN_T                                   # западный край садовой террасы
SP_L, SP_W, SP_Y0 = 14.0, 6.6, 0.6                    # спортплощадка вдоль западного забора (С–Ю, как корт)
SP_X0 = math.ceil((x_west(SP_Y0 + SP_L) + 0.5) * 10) / 10   # ≥0.5 м от западного забора (сетка 3 м по забору)
SPORT = (SP_X0, SP_Y0, SP_X0 + SP_W, SP_Y0 + SP_L)
DECK = 0.4
_px0 = SPORT[2] + 0.8 + DECK                          # бассейн: 0.8 м от площадки, перед садовой террасой (с юга)
POOL = (_px0, 1.4, _px0 + 5.0, 1.4 + 2.5)             # чаша 5 × 2.5 м, настил 0.4 м вокруг
TUB_DECK = 0.3
TUB = (POOL[2] + DECK + 1.2 + 1.0 + TUB_DECK, (POOL[1] + POOL[3]) / 2, 1.0)   # купель Ø2 м у мастер-блока
# детская зона на северо-западе: у садовой террасы, вдали от машин, воды и дороги; качели осью качания З–В
SWING = (3.6, SPORT[3] + 0.8, 5.7, SPORT[3] + 0.8 + 2.8)                       # качели/горка 2.1 × 2.8 м (балка С–Ю)
SWING_ZONE = (SWING[0] - 2.0, SWING[1], SWING[2] + 2.0, SWING[3])                # зона качания 2 м на запад и восток
SAND = (HX0 - GARDEN_T + 0.25, HY0 + 10.6, HX0 - GARDEN_T + 2.25, HY0 + 12.6)   # песочница 2 × 2 м у садовой террасы
# откатные ворота: проём 6 м у южного угла, откат ≈1.45 проёма вдоль забора на север; калитка — за зоной отката
GATE_W = 6.0
GATE_Y0 = (HY0 + 2.5 - GATE_W) / 2                                             # проём по центру площадки
GATE_ROLL = (GATE_Y0 + GATE_W, GATE_Y0 + GATE_W + 1.5 * GATE_W)
CARS = (GATE_Y0 + 0.4 + 0.95, GATE_Y0 + GATE_W - 0.4 - 0.95)                    # оси машин: по 0.4 м до столбов
WICKET = (GATE_ROLL[1] + 0.4, GATE_ROLL[1] + 1.4)                              # калитка 1 м за зоной отката
PATH = (xe + 1.5, WICKET[0] - 0.1, x_road(WICKET[1] + 0.1), WICKET[1] + 0.1)   # дорожка от калитки (1.2 м)
LANDING = (xe, HY0 + 10.0, xe + 1.5, PATH[3])                                  # площадка-ступень у входной террасы

OBJ = {
    "дом (основной объём)": lrect(*HOUSE_BLOCKS[0]),
    "дом (доп. модуль)": lrect(*HOUSE_BLOCKS[1]),
    "терраса у дороги": lrect(*TERRACES[0][1:]),
    "терраса в сад": lrect(*TERRACES[1][1:]),
    "парковка": PARK,
    "бассейн+настил": xyrect(POOL[0] - DECK, POOL[1] - DECK, POOL[2] + DECK, POOL[3] + DECK),
    "купель+настил": circle_poly(TUB[0], TUB[1], TUB[2] + TUB_DECK),
    "спортплощадка": xyrect(*SPORT),
    "песочница": xyrect(*SAND),
    "качели/горка": xyrect(*SWING),
    "дорожка": xyrect(*PATH),
    "площадка у террасы": xyrect(*LANDING),
    "зона качания": xyrect(*SWING_ZONE),
}

# ---------- SVG ----------
xs = [p[0] for p in P]; ys = [p[1] for p in P]
minx, maxx, miny, maxy = min(xs) - 4, max(xs) + 8, min(ys) - 4, max(ys) + 4
SC = 32


def sv(p):
    return ((p[0] - minx) * SC, (maxy - p[1]) * SC)


def poly_svg(pts, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in map(sv, pts))}" {attrs}/>'


def text(p, s, size=13, **kw):
    x, y = sv(p)
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="middle" font-family="sans-serif" {attrs}>{s}</text>'


def mid(a, b, off=0.0):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + off)


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


ROOMS_SVG = []
for name, tx0, ty0, tx1, ty1 in TERRACES:
    pts = lrect(tx0, ty0, tx1, ty1)
    ROOMS_SVG.append(poly_svg(pts, fill="#c9a36b", stroke="#6b4f1d", stroke_width=1.5))
    c = local((tx0 + tx1) / 2, ty1 - 1.6)
    ROOMS_SVG.append(text((c[0], c[1] + 0.2), name, 9))
    ROOMS_SVG.append(text((c[0], c[1] - 0.5), f"{abs(tx1 - tx0):g}×{abs(ty1 - ty0):g} м", 9))
    ROOMS_SVG.append(text((c[0], c[1] - 1.1), f"{f1(abs((tx1 - tx0) * (ty1 - ty0)))} м²", 9))
ROOMS_SVG.append(poly_svg(HOUSE, fill="#f3e6c8", stroke="#6b4f1d", stroke_width=3))
for name, rx0, ry0, rx1, ry1, col in ROOMS:
    ROOMS_SVG.append(poly_svg(lrect(rx0, ry0, rx1, ry1), fill=col, stroke="#6b4f1d", stroke_width=1.2))
ROOMS_SVG.append(poly_svg(HOUSE, fill="none", stroke="#6b4f1d", stroke_width=3))
for name, rx0, ry0, rx1, ry1, col in ROOMS:
    c = centroid(lrect(rx0, ry0, rx1, ry1))
    a = abs((rx1 - rx0) * (ry1 - ry0))
    fs = 11 if a > 12 else 9
    ROOMS_SVG.append(text((c[0], c[1] + 0.15), name, fs, font_weight="bold"))
    ROOMS_SVG.append(text((c[0], c[1] - 0.45), f"{f1(a)} м²", fs - 1))
for name, X, Y, LX, LY in DOORS:
    dx, dy = sv(local(X, Y))
    ROOMS_SVG.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="5" fill="#c0392b"/>')
    if name:
        ROOMS_SVG.append(text(local(LX, LY), name, 10, fill="#c0392b", font_weight="bold"))


def dist_to_line_any(p):
    return min(dist_to_line(p, P[i], P[(i + 1) % 4]) for i in range(4))


def ray_to_fence(p, d):
    """Точка пересечения луча p + k·d с границей участка (ближайшая)."""
    best_k = None
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        k = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
        m = ((a[0] - p[0]) * d[1] - (a[1] - p[1]) * d[0]) / den
        if k > 1e-6 and -1e-9 <= m <= 1 + 1e-9 and (best_k is None or k < best_k):
            best_k = k
    return (p[0] + d[0] * best_k, p[1] + d[1] * best_k), best_k


DIMS = [  # (точка в координатах дома, направление[, подпись снизу]) — от стены/террасы до забора
    ((-GARDEN_T, 9.95), (-1, 0), 1),  # садовая терраса -> западный забор (над кортом, под зоной качания)
    ((4.02, 0.0), (0, -1), 0, 0.12),  # мастер-блок -> южный забор (между бассейном и купелью, подпись у дома)
    ((10.4, 2.5), (0, -1)),           # гостиная -> южный забор (лужайка у гостиной)
    ((13.3, 10.0), (0, 1)),           # северная стена -> северный забор
    ((15.5, 9.6), (1, 0), 1),         # терраса у дороги -> забор у дороги (у северного края — самое узкое место)
]
DIM_SVG = []
for (X, Y), d, *opt in DIMS:
    below, t_lbl = (opt + [0, 0.5])[:2]
    p = local(X, Y)
    q, dist = ray_to_fence(p, d)
    (x1, y1), (x2, y2) = sv(p), sv(q)
    DIM_SVG.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#0b5cad" stroke-width="1.6" '
                   f'marker-start="url(#arr)" marker-end="url(#arr)"/>')
    mx, my = x1 + (x2 - x1) * t_lbl, y1 + (y2 - y1) * t_lbl
    lbl = f"{dist:.1f} м"
    if d[0] == 0:  # вертикальная размерная — подпись сбоку
        DIM_SVG.append(f'<rect x="{mx + 4:.1f}" y="{my - 9:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx + 8:.1f}" y="{my + 4:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" font-family="sans-serif">{lbl}</text>')
    else:
        if below:
            my += 24
        DIM_SVG.append(f'<rect x="{mx - len(lbl) * 3.75:.1f}" y="{my - 20:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx:.1f}" y="{my - 7:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" text-anchor="middle" font-family="sans-serif">{lbl}</text>')
    print(f"размер от {X, Y} по {d}: {dist:.2f} м")


def rect_svg(r, **kw):
    return poly_svg(xyrect(*r), **kw)


HALO = dict(stroke="#5a9e6f", stroke_width=4, paint_order="stroke")
LS = []
# дорожка от калитки ко входу
LS.append(rect_svg(LANDING, fill="#d9d4c7", stroke="#9a927e", stroke_width=1))
LS.append(rect_svg(PATH, fill="#d9d4c7", stroke="#9a927e", stroke_width=1))
_k1, _k2 = sv((x_road(WICKET[0]), WICKET[0])), sv((x_road(WICKET[1]), WICKET[1]))
LS.append(f'<line x1="{_k1[0]:.1f}" y1="{_k1[1]:.1f}" x2="{_k2[0]:.1f}" y2="{_k2[1]:.1f}" stroke="#8a5a00" stroke-width="5"/>')
LS.append(text((PATH[2] - 1.0, PATH[3] + 0.3), "калитка", 9, fill="#4a4434", font_weight="bold"))
# кустарник / живая изгородь (центры ≥1 м от забора): у дороги (от улицы), у северного забора (за домом),
# у южного забора на лужайке и живая изгородь между лужайкой и парковкой
SHRUBS = ([(x_road(y) - 1.7, y, 0.5) for y in (9.0, 10.4, 11.8, 13.2, 14.6)]     # у дороги (за зоной отката ворот)
          + [(x, y_north(x) - 1.1, 0.55) for x in (12.6, 14.0, 15.4, 16.8, 18.2, 19.6, 21.0, 22.4, 23.8)]
          + [(x, 1.1, 0.55) for x in (19.4, 23.6)]                                       # у южного забора на лужайке
          + [(park_x0 - 0.6, y, 0.45) for y in (1.4, 2.6, 3.8, 5.0, 6.2)])               # изгородь лужайка | парковка
for X, Y, r in SHRUBS:
    cx, cy = sv((X, Y))
    LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * SC:.1f}" fill="#5f8a3a" stroke="#3d5e22" stroke-width="1" opacity="0.9"/>')
# спортплощадка (внутри — разметка бадминтона, парный корт 13.4 × 6.1 м)
sx0, sy0, sx1, sy1 = SPORT
scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
LS.append(rect_svg(SPORT, fill="#5a9e6f", stroke="#ffffff", stroke_width=2))
LS.append(rect_svg((scx - 3.05, scy - 6.7, scx + 3.05, scy + 6.7), fill="none", stroke="#ffffff", stroke_width=1.2))
LS.append(rect_svg((scx - 2.59, scy - 6.7, scx + 2.59, scy + 6.7), fill="none", stroke="#ffffff", stroke_width=0.8, opacity="0.7"))
(nx1, ny1), (nx2, ny2) = sv((sx0, scy)), sv((sx1, scy))
LS.append(f'<line x1="{nx1:.1f}" y1="{ny1:.1f}" x2="{nx2:.1f}" y2="{ny2:.1f}" stroke="#ffffff" stroke-width="3" stroke-dasharray="3 2"/>')
LS.append(text((scx, scy + 3.4), "СПОРТПЛОЩАДКА", 12, fill="#fff", font_weight="bold", **HALO))
LS.append(text((scx, scy + 2.7), f"{sx1 - sx0:.1f}×{sy1 - sy0:.1f} м · {(sx1 - sx0) * (sy1 - sy0):.0f} м²", 11, fill="#fff", **HALO))
LS.append(text((scx, scy + 1.95), "сетка поперёк", 9, fill="#fff", **HALO))
_net = [(sx1 + 0.15, sy1 + 0.15), (sx0 - 0.15, sy1 + 0.15), (sx0 - 0.15, sy0 - 0.15), (sx1 + 0.15, sy0 - 0.15)]
LS.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in map(sv, _net))}" fill="none" stroke="#2e5e3a" '
          f'stroke-width="2.5" stroke-dasharray="2 2"/>')
LS.append(text((scx, scy - 2.0), "бадминтон 13.4×6.1", 10, fill="#fff", **HALO))
LS.append(text((scx, scy - 2.6), "(парный корт, запас 0.25–0.3 м)", 9, fill="#fff", **HALO))
LS.append(text((scx, scy - 3.4), "мини-волейбол · турник", 9, fill="#fff", **HALO))
LS.append(text((scx, scy - 4.0), "сетка 3 м: запад, юг, север", 9, fill="#fff", **HALO))
LS.append(text((scx, scy - 4.5), "к террасе — низкое ограждение", 9, fill="#fff", **HALO))
# бассейн
x0p, y0p, x1p, y1p = POOL
LS.append(rect_svg((x0p - DECK, y0p - DECK, x1p + DECK, y1p + DECK), fill="#e9e1cf", stroke="#b8ab8a", stroke_width=1))
LS.append(rect_svg(POOL, fill="#5bb8e6", stroke="#1f7fb0", stroke_width=2))
LS.append(text(((x0p + x1p) / 2, (y0p + y1p) / 2 + 0.25), "бассейн", 10, fill="#fff", font_weight="bold"))
LS.append(text(((x0p + x1p) / 2, (y0p + y1p) / 2 - 0.45), f"{x1p - x0p:g}×{y1p - y0p:g} м", 9, fill="#fff"))
# купель
X, Y, r = TUB
cx, cy = sv((X, Y))
LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(r + TUB_DECK) * SC:.1f}" fill="#c9a36b" stroke="#6b4f1d" stroke-width="1"/>')
LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * SC:.1f}" fill="#7fd0e8" stroke="#1f7fb0" stroke-width="2"/>')
LS.append(text((X, Y + 0.1), "купель", 10, font_weight="bold", fill="#0d3b52"))
LS.append(text((X, Y - 0.5), f"Ø{2 * r:g} м", 9, fill="#0d3b52"))
# песочница и качели
LS.append(rect_svg(SWING_ZONE, fill="#f4c7a1", fill_opacity="0.35", stroke="#b0703a", stroke_width=1, stroke_dasharray="4 3"))
LS.append(text(((SWING_ZONE[0] + SWING[0]) / 2, SWING_ZONE[1] + 0.35), "зона", 8, fill="#6b3d17"))
LS.append(text(((SWING_ZONE[2] + SWING[2]) / 2, SWING_ZONE[1] + 0.35), "качания", 8, fill="#6b3d17"))
LS.append(rect_svg(SAND, fill="#f1d98a", stroke="#a8893a", stroke_width=1.5))
LS.append(text(((SAND[0] + SAND[2]) / 2, (SAND[1] + SAND[3]) / 2 + 0.1), "песочница", 9, font_weight="bold"))
LS.append(text(((SAND[0] + SAND[2]) / 2, (SAND[1] + SAND[3]) / 2 - 0.5), "2×2 м", 9))
LS.append(rect_svg(SWING, fill="#f4c7a1", stroke="#b0703a", stroke_width=1.5))
LS.append(text(((SWING[0] + SWING[2]) / 2, (SWING[1] + SWING[3]) / 2 + 0.1), "качели / горка", 9, font_weight="bold"))
LS.append(text(((SWING[0] + SWING[2]) / 2, (SWING[1] + SWING[3]) / 2 - 0.5), "детская зона", 9))

# ---------- проверки ----------
print("--- проверки ---")
in_build = {k: all(inside(BUILD, c) for c in OBJ[k]) for k in ("дом (основной объём)", "дом (доп. модуль)", "терраса у дороги", "терраса в сад")}
print("в пятне застройки (отступ 3 м):", in_build)
in_plot = {k: all(inside(P, c) for c in v) for k, v in OBJ.items()}
print("внутри участка:", in_plot)
for k in ("спортплощадка", "бассейн+настил", "купель+настил", "песочница", "качели/горка"):
    print(f"  {k}: мин. до забора {min(dist_to_line_any(c) for c in OBJ[k]):.2f} м")
names = list(OBJ)
pairs, hits = 0, []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        if {names[i], names[j]} == {"качели/горка", "зона качания"}:
            continue   # зона качания по определению включает сами качели
        pairs += 1
        if overlap(OBJ[names[i]], OBJ[names[j]]):
            hits.append((names[i], names[j]))
print(f"пересечения (попарно, {pairs} пар): {hits if hits else 'нет'}")
for a_, b_ in [("спортплощадка", "бассейн+настил"), ("бассейн+настил", "купель+настил"), ("бассейн+настил", "терраса в сад"),
               ("купель+настил", "дом (доп. модуль)"), ("спортплощадка", "качели/горка"), ("песочница", "терраса в сад"),
               ("парковка", "дом (основной объём)"), ("парковка", "терраса у дороги"), ("спортплощадка", "терраса в сад")]:
    print(f"  зазор {a_} — {b_}: {poly_gap(OBJ[a_], OBJ[b_]):.2f} м")
print("ворота / калитка в заборе у дороги:", inside(P, (x_road(0.5), 0.5)), inside(P, (PATH[2], PATH[3])))


def clip_left(poly, xl):
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        pin, qin = p[0] <= xl, q[0] <= xl
        if pin:
            out.append(p)
        if pin != qin:
            t = (xl - p[0]) / (q[0] - p[0])
            out.append((xl, p[1] + (q[1] - p[1]) * t))
    return out


BACKYARD = area(clip_left(P, TW))
print(f"сад западнее садовой террасы: {BACKYARD:.0f} м²")
LAWN = (park_x0 - 0.6 - 0.45 - (TUB[0] + TUB[2] + TUB_DECK)) * park_y1 - 2 * math.pi * 0.55 ** 2   # газон у гостиной

TERR_AREA = sum(abs((t[3] - t[1]) * (t[4] - t[2])) for t in TERRACES)
FREE = area(P) - HOUSE_AREA - TERR_AREA - area(PARK)
COV_H, COV_T = HOUSE_AREA / area(P) * 100, (HOUSE_AREA + TERR_AREA) / area(P) * 100

W, H = (maxx - minx) * SC, (maxy - miny) * SC + 112
pc = centroid(PARK)
el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" fill="#fff"/>',
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#0b5cad"/></marker></defs>',
]
# два машино-места (контуры авто ~4.7 × 1.9 м, носом на запад)
for cyc in CARS:
    (ax, ay), (bx, by) = sv((park_x0 + 0.9, cyc + 0.95)), sv((park_x0 + 0.9 + 4.7, cyc - 0.95))
    el.append(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" height="{by - ay:.1f}" rx="10" fill="#d4d4d4" '
              f'stroke="#888" stroke-width="1.2" stroke-dasharray="5 3"/>')
el += [
    *LS,
    *ROOMS_SVG,
    *DIM_SVG,
    text((pc[0], sum(CARS) / 2 + 0.3), "P · 2 авто рядом", 13, font_weight="bold"),
    text((pc[0], sum(CARS) / 2 - 0.35), f"{f1(PARK_W)}×{PARK_D:g} м · {area(PARK):.0f} м² · бетон", 11),
    text((pc[0], CARS[1] - 0.15), "место 2", 10, fill="#444"),
    text((pc[0], CARS[0] - 0.15), "место 1", 10, fill="#444"),
    text(mid(A, B, -0.9), f"{AB} м · ЮГ (солнце днём)", 14, fill="#8a5a00"),
    text(mid(C, D, 0.6), f"{CD} м · СЕВЕР", 14),
]
mx, my = sv(mid(D, A))
el.append(f'<text x="{mx - 30:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{DA} м</text>'
          f'<text x="{mx - 62:.1f}" y="{my:.1f}" font-size="14" font-weight="bold" text-anchor="middle" font-family="sans-serif" '
          f'transform="rotate(-86 {mx - 62:.1f} {my:.1f})">ЗАПАД</text>')
mx, my = sv(mid(B, C))
el.append(f'<text x="{mx + 38:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{BC} м</text>'
          f'<text x="{mx + 75:.1f}" y="{my:.1f}" font-size="15" font-weight="bold" text-anchor="middle" font-family="sans-serif" '
          f'transform="rotate(-90 {mx + 75:.1f} {my:.1f})">дорога · ВОСТОК</text>')
# ворота и въезд с дороги
g1, g2 = sv((x_road(GATE_Y0), GATE_Y0)), sv((x_road(GATE_ROLL[0]), GATE_ROLL[0]))
el.append(f'<line x1="{g1[0]:.1f}" y1="{g1[1]:.1f}" x2="{g2[0]:.1f}" y2="{g2[1]:.1f}" stroke="#333" stroke-width="5"/>')
r1, r2 = sv((x_road(GATE_ROLL[0]) - 0.35, GATE_ROLL[0])), sv((x_road(GATE_ROLL[1]) - 0.35, GATE_ROLL[1]))
el.append(f'<line x1="{r1[0]:.1f}" y1="{r1[1]:.1f}" x2="{r2[0]:.1f}" y2="{r2[1]:.1f}" stroke="#333" stroke-width="2" stroke-dasharray="7 4"/>')
_rm = sv((x_road(sum(GATE_ROLL) / 2) - 0.75, sum(GATE_ROLL) / 2))
el.append(f'<text x="{_rm[0]:.1f}" y="{_rm[1]:.1f}" font-size="10" text-anchor="middle" font-family="sans-serif" fill="#333" '
          f'transform="rotate(-90 {_rm[0]:.1f} {_rm[1]:.1f})">откат ворот ≈{GATE_ROLL[1] - GATE_ROLL[0]:.1f} м</text>')
gy = GATE_Y0 + GATE_W / 2
e1 = sv((x_road(gy) + 2.5, gy)); e2 = sv((x_road(gy) - 0.5, gy))
el.append(f'<line x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e2[0]:.1f}" y2="{e2[1]:.1f}" stroke="#222" stroke-width="2.5"/><circle cx="{e2[0]:.1f}" cy="{e2[1]:.1f}" r="4"/>')
el.append(text((x_road(gy) + 1.4, gy + 0.3), "ворота", 10, fill="#222", font_weight="bold"))
el.append(text((x_road(gy) + 1.4, gy - 0.9), f"откатные {GATE_W:g} м", 10, fill="#222"))
_lw = ((TUB[0] + TUB[2] + TUB_DECK + local(10.4, 0)[0]) / 2, 6.4)   # между купелью и размерной линией
el.append(text(_lw, "лужайка", 12, fill="#2f3b12", font_style="italic"))
el.append(text((_lw[0], _lw[1] - 0.55), "у гостиной", 12, fill="#2f3b12", font_style="italic"))
el.append(text((18.2, y_north(18.2) - 2.15), "кустарник / живая изгородь", 9, fill="#2f3b12", font_style="italic"))

# ---------- стороны света ----------
NORTH_DEG = -8.6  # север повёрнут на ~8.6° против часовой от «верха» схемы
cx, cy = 70, 80
el.append(f'<g transform="rotate({NORTH_DEG} {cx} {cy})">'
          f'<circle cx="{cx}" cy="{cy}" r="34" fill="#fff" stroke="#333" stroke-width="1.5"/>'
          f'<path d="M{cx},{cy - 30} L{cx + 9},{cy + 6} L{cx},{cy} L{cx - 9},{cy + 6} z" fill="#c0392b"/>'
          f'<path d="M{cx},{cy + 30} L{cx + 9},{cy - 6} L{cx},{cy} L{cx - 9},{cy - 6} z" fill="#999"/>'
          f'<text x="{cx}" y="{cy - 38}" font-size="16" font-weight="bold" text-anchor="middle" font-family="sans-serif">С</text></g>')
ly = (maxy - miny) * SC + 25
el.append(f'<line x1="20" y1="{ly - 5}" x2="50" y2="{ly - 5}" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<text x="58" y="{ly}" font-size="13" font-family="sans-serif">граница пятна застройки: отступ {SETBACK:g} м от всех границ</text>')
el.append(f'<text x="20" y="{ly + 24}" font-size="13" font-family="sans-serif">участок ≈{area(P):.0f} м² · дом {HOUSE_AREA:.1f} м² (7 модулей DP-Module) · '
          f'террасы {f1(TERR_AREA)} м² · парковка {area(PARK):.0f} м² · двор/сад ≈{FREE:.0f} м², из них спортплощадка {SP_W * SP_L:.0f} м², газон у гостиной ≈{LAWN:.0f} м²</text>')
el.append(f'<text x="20" y="{ly - 30}" font-size="14" font-weight="bold" font-family="sans-serif">ИЖС, участок 6 сот. по объявлению (≈593 м² по сторонам) · '
          f'ПЗЗ (обычно для ИЖС в МО): отступ 3 м, застройка ≤40% → дом {COV_H:.0f}%, с террасами {COV_T:.0f}% (уточнить по ГПЗУ)</text>')
el.append(f'<text x="20" y="{ly + 46}" font-size="13" fill="#0b5cad" font-family="sans-serif">синие размеры — расстояние от стены дома / края террасы до забора · площади комнат — по осям модулей (брутто)</text>')
el.append(f'<text x="20" y="{ly + 68}" font-size="13" fill="#555" font-family="sans-serif">терраса в {ROAD_GAP:g} м от дороги (≥5 м под красную линию) · '
          f'мастер-блок с юга · 2 авто рядом, бетон до входа · откатные ворота {GATE_W:g} м, калитка за откатом · '
          f'корт {SP_W:g}×{SP_L:g} м · детская зона на СЗ</text>')
el.append("</svg>")
open("plan6.svg", "w").write("\n".join(el))

print("--- итоги ---")
print("угол при A:", round(math.degrees(best_a), 1))
print("участок:", [tuple(round(c, 2) for c in p) for p in P], "площадь", round(area(P), 1))
print("пятно застройки:", round(area(BUILD), 1), "м²")
print(f"дом {HOUSE_AREA:.1f} м²; до дороги {min(dist_to_line(p, B, C) for p in HOUSE):.2f} м; "
      f"до юга {min(dist_to_line(p, A, B) for p in HOUSE):.2f}; до севера {min(dist_to_line(p, C, D) for p in HOUSE):.2f}; "
      f"до запада {min(dist_to_line(p, D, A) for p in HOUSE):.2f}")
print(f"терраса у дороги до забора {min(dist_to_line(p, B, C) for p in OBJ['терраса у дороги']):.2f} м; "
      f"садовая терраса до запада {min(dist_to_line(p, D, A) for p in OBJ['терраса в сад']):.2f} м")
print(f"застройка: дом {COV_H:.1f}%, с террасами {COV_T:.1f}% (террасы {TERR_AREA:.2f} м²)")
print(f"двор/сад (участок − дом − террасы − парковка): {FREE:.1f} м²")
print("сумма комнат:", sum(abs((r[3] - r[1]) * (r[4] - r[2])) for r in ROOMS))
print(f"спортплощадка {SP_W:g}×{SP_L:g} м = {SP_W * SP_L:.0f} м²: x {SPORT[0]:.2f}..{SPORT[2]:.2f}, y {SPORT[1]:.2f}..{SPORT[3]:.2f}")
print(f"бассейн x {POOL[0]:.2f}..{POOL[2]:.2f}, y {POOL[1]:.2f}..{POOL[3]:.2f}; купель центр ({TUB[0]:.2f}, {TUB[1]:.2f})")
