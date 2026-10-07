"""Быстрая модель размещения дома (~105 м²) и парковки на 2 машины на участке 4.5 сот."""
import math

AB, BC, CD, DA, AREA = 30.7, 16.3, 24.2, 18.0, 450.0  # низ, дорога, верх, лево
SETBACK = 3.0          # отступ дома от границ (по запросу)
HOUSE_AREA = 105.0
PARK_W, PARK_D = 6.0, 6.0  # 2 машины рядом с комфортом: 2 места по 3.0 × 6.0 м (36 м²)


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


def area(p):
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2


# подбираем угол при A так, чтобы площадь = 450 м²
lo, hi = math.radians(60), math.radians(120)
best = min((abs(area(shape(lo + (hi - lo) * i / 20000)) - AREA), lo + (hi - lo) * i / 20000) for i in range(20001))
best_a = best[1]
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
# система координат вдоль дороги: u — вдоль дороги от B к C, n — вглубь участка
L = math.hypot(C[0] - B[0], C[1] - B[1])
u = ((C[0] - B[0]) / L, (C[1] - B[1]) / L)
nrm = (-u[1], u[0])


def to_xy(s, t):
    return (B[0] + u[0] * s + nrm[0] * t, B[1] + u[1] * s + nrm[1] * t)


def rect(s, t, w, h):
    return [to_xy(s, t), to_xy(s + w, t), to_xy(s + w, t + h), to_xy(s, t + h)]


# парковка: у дороги, в верхнем углу — в нише над санузлом/гостиной (въезд с дороги)
PARK_MARGIN = 0.1  # до забора
park_s = BC - PARK_W
while not all(inside(P, c) for c in rect(park_s, 0, PARK_W, PARK_D)) and park_s > 0:
    park_s -= 0.05
park_s -= PARK_MARGIN
PARK = rect(park_s, 0, PARK_W, PARK_D)

# DP-Module «Модерн 105»: 14 × 7.5 м (6 модулей 7 × 2.5 м) + 1 модуль 7 × 2.5 м под мастер-спальню.
# Локальные координаты дома: X — вдоль длинной стороны (0 = торец в сад, 14 = торец к дороге),
# Y — поперёк (0 = сторона парковки).
HOUSE_L = 14.0
OUTLINE = [(0, 0), (14, 0), (14, 7.5), (7, 7.5), (7, 10), (0, 10)]  # Г-образный контур, 122.5 м²

ROOMS = [
    # мастер-блок (доп. модуль)
    ("Мастер-спальня", 0.0, 5.3, 3.6, 10.0, "#cfe0f3"),
    ("Гардеробная", 3.6, 5.3, 7.0, 7.5, "#e6e0f0"),
    ("С/у мастер", 3.6, 7.5, 7.0, 10.0, "#d6f0ee"),
    # коридор между спальнями -> выход в сад
    ("Коридор", 0.0, 4.0, 7.0, 5.3, "#eeeeee"),
    ("Спальня", 0.0, 0.0, 3.6, 4.0, "#dfe9f5"),
    ("Детская", 3.6, 0.0, 7.0, 4.0, "#f6e0ea"),
    # общая зона (вход — с террасы у дороги, отдельной прихожей нет)
    ("Холл", 7.0, 3.0, 9.5, 5.3, "#eeeeee"),
    ("Санузел", 7.0, 5.3, 9.5, 7.5, "#d6f0ee"),
    ("Кухня-столовая", 7.0, 0.0, 14.0, 3.0, "#fde7c4"),
    ("Гостиная", 9.5, 3.0, 14.0, 7.5, "#fbf1d6"),
]
TERRACES = [
    ("терраса", 14.0, 0.0, 15.5, 7.5),   # у дороги, во всю стену кухни-столовой и гостиной
    ("терраса", -2.0, 0.0, 0.0, 10.0),   # в сад, во всю стену спальни, коридора и мастер-спальни
]
DOORS = [("вход", 14.0, 3.8, 14.75, 2.6), ("в сад", 0.0, 4.65, -1.0, 3.4)]


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


# дом ставим параллельно нижней границе (30.7 м): так 10-метровая ширина помещается в отступы
def place(xe, y0):
    return lambda X, Y: (xe - (HOUSE_L - X), y0 + Y)


HOUSE_BLOCKS = [(0, 0, 14, 7.5), (0, 7.5, 7, 10)]
best = None
# терраса у дороги при необходимости чуть короче сверху, чтобы рядом встала парковка 6×6
for rt_top in (7.5, 7.25, 7.0, 6.75, 6.5):
    TERRACES[0] = ("терраса", 14.0, 0.0, 15.5, rt_top)
    for yi in range(30, 80):
        y0 = yi * 0.1
        for xi in range(320, 100, -1):
            xe = xi * 0.1
            loc = place(xe, y0)
            blocks = [[loc(x0, b0), loc(x1, b0), loc(x1, b1), loc(x0, b1)] for x0, b0, x1, b1 in HOUSE_BLOCKS]
            road_t, garden_t = ([loc(x0, b0), loc(x1, b0), loc(x1, b1), loc(x0, b1)] for _, x0, b0, x1, b1 in TERRACES)
            if (all(inside(BUILD, loc(*p)) for p in OUTLINE)
                    and all(inside(BUILD, c) for c in road_t)
                    and all(inside(BUILD, c) for c in garden_t)
                    and not any(overlap(bl, PARK, 0.15) for bl in blocks)
                    and not overlap(road_t, PARK, 0.1)):  # с парковки сразу на террасу
                if best is None or xe > best[0]:
                    best = (xe, y0)
                break
    if best:
        break
xe, y0 = best
print("терраса у дороги до Y =", rt_top, "| xe =", round(xe, 2), "y0 =", round(y0, 2))
local = place(xe, y0)


def lrect(x0, y0, x1, y1):
    return [local(x0, y0), local(x1, y0), local(x1, y1), local(x0, y1)]


HOUSE = [local(*p) for p in OUTLINE]
HOUSE_AREA = area(HOUSE)

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
for name, x0, y0, x1, y1 in TERRACES:
    pts = lrect(x0, y0, x1, y1)
    ROOMS_SVG.append(poly_svg(pts, fill="#c9a36b", stroke="#6b4f1d", stroke_width=1.5))
    c = local((x0 + x1) / 2, y1 - 1.6)
    ROOMS_SVG.append(text((c[0], c[1] + 0.2), name, 9))
    ROOMS_SVG.append(text((c[0], c[1] - 0.5), f"{abs(x1 - x0):g}×{abs(y1 - y0):g} м", 9))
    ROOMS_SVG.append(text((c[0], c[1] - 1.1), f"{abs((x1 - x0) * (y1 - y0)):.1f} м²", 9))
ROOMS_SVG.append(poly_svg(HOUSE, fill="#f3e6c8", stroke="#6b4f1d", stroke_width=3))
for name, x0, y0, x1, y1, col in ROOMS:
    ROOMS_SVG.append(poly_svg(lrect(x0, y0, x1, y1), fill=col, stroke="#6b4f1d", stroke_width=1.2))
ROOMS_SVG.append(poly_svg(HOUSE, fill="none", stroke="#6b4f1d", stroke_width=3))
for name, x0, y0, x1, y1, col in ROOMS:
    c = centroid(lrect(x0, y0, x1, y1))
    a = abs((x1 - x0) * (y1 - y0))
    fs = 11 if a > 12 else 9
    ROOMS_SVG.append(text((c[0], c[1] + 0.15), name, fs, font_weight="bold"))
    ROOMS_SVG.append(text((c[0], c[1] - 0.45), f"{a:.1f} м²", fs - 1))
for name, X, Y, LX, LY in DOORS:
    dx, dy = sv(local(X, Y))
    ROOMS_SVG.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="5" fill="#c0392b"/>')
    if name:
        ROOMS_SVG.append(text(local(LX, LY), name, 10, fill="#c0392b", font_weight="bold"))

def dist_to_line_any(p):
    return min(abs((P[(i + 1) % 4][0] - P[i][0]) * (P[i][1] - p[1]) - (P[i][0] - p[0]) * (P[(i + 1) % 4][1] - P[i][1]))
               / math.hypot(P[(i + 1) % 4][0] - P[i][0], P[(i + 1) % 4][1] - P[i][1]) for i in range(4))


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


DIMS = [  # (точка в координатах дома, направление) — от стены/террасы до забора
    ((-2.0, 0.4), (-1, 0)),    # сад-терраса, низ
    ((-2.0, 9.9), (-1, 0)),    # сад-терраса, верх
    ((6.2, 0.0), (0, -1)),     # спальни -> нижний забор
    ((2.0, 10.0), (0, 1)),     # мастер-блок -> верхний забор
    ((15.5, 1.0), (1, 0)),     # терраса у дороги -> забор у дороги
]
DIM_SVG = []
for (X, Y), d in DIMS:
    p = local(X, Y)
    q, dist = ray_to_fence(p, d)
    (x1, y1), (x2, y2) = sv(p), sv(q)
    DIM_SVG.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#0b5cad" stroke-width="1.6" '
                   f'marker-start="url(#arr)" marker-end="url(#arr)"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    lbl = f"{dist:.1f} м"
    if d[0] == 0:  # вертикальная размерная — подпись сбоку
        DIM_SVG.append(f'<rect x="{mx + 4:.1f}" y="{my - 9:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx + 8:.1f}" y="{my + 4:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" font-family="sans-serif">{lbl}</text>')
    else:
        DIM_SVG.append(f'<rect x="{mx - len(lbl) * 3.75:.1f}" y="{my - 20:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx:.1f}" y="{my - 7:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" text-anchor="middle" font-family="sans-serif">{lbl}</text>')
    print(f"размер от {X, Y} по {d}: {dist:.2f} м")

# ---------- жизнь на участке (координаты от дома: X вдоль дома, Y поперёк) ----------
def lrect_svg(x0, y0, x1, y1, **kw):
    return poly_svg(lrect(x0, y0, x1, y1), **kw)


def lbl(X, Y, s, size=10, **kw):
    return text(local(X, Y), s, size, **kw)


LEISURE = {
    "pool": (-4.9, 1.6, -2.4, 6.6),      # бассейн 2.5 × 5 м у садовой террасы
    "tub": (-3.4, 8.4, 1.0),             # купель Ø2 м у мастер-спальни (центр X, Y, радиус)
    "sport": (7.3, 7.8, 13.8, 13.0),     # спортплощадка в нише над санузлом/гостиной
    "sand": (8.0, -2.5, 10.0, -0.5),     # песочница 2 × 2 м под окнами кухни
    "swing": (10.6, -2.6, 13.4, -0.5),   # качели/горка
    "path": (15.5, 2.8, 19.9, 4.0),      # дорожка от калитки ко входу
}
LS = []
x0, y0_, x1, y1 = LEISURE["path"]
LS.append(lrect_svg(x0, y0_, x1, y1, fill="#d9d4c7", stroke="#9a927e", stroke_width=1))
gx, gy = local(x1 - 0.4, (y0_ + y1) / 2)
LS.append(text(local(x1 - 1.0, y1 + 0.35), "калитка", 9, fill="#4a4434", font_weight="bold"))
# кустарник / живая изгородь у южного забора (≥1 м от забора; высокие деревья — не ближе 4 м к соседу)
for X, Y, r in [(-9.0, -1.6, 0.6), (-7.4, -1.6, 0.6), (-5.8, -1.6, 0.6), (1.5, -1.8, 0.6), (3.1, -1.8, 0.6),
                (4.7, -1.8, 0.6), (16.8, -1.6, 0.6)]:
    cx, cy = sv(local(X, Y))
    LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * SC:.1f}" fill="#5f8a3a" stroke="#3d5e22" stroke-width="1" opacity="0.9"/>')
# спортплощадка
x0, y0_, x1, y1 = LEISURE["sport"]
LS.append(lrect_svg(x0, y0_, x1, y1, fill="#5a9e6f", stroke="#ffffff", stroke_width=2))
LS.append(lrect_svg(x0 + 0.4, y0_ + 0.4, x1 - 0.4, y1 - 0.4, fill="none", stroke="#ffffff", stroke_width=1.2))
(nx1, ny1), (nx2, ny2) = sv(local((x0 + x1) / 2, y0_)), sv(local((x0 + x1) / 2, y1))
LS.append(f'<line x1="{nx1:.1f}" y1="{ny1:.1f}" x2="{nx2:.1f}" y2="{ny2:.1f}" stroke="#ffffff" stroke-width="3" stroke-dasharray="3 2"/>')
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 + 1.0, "СПОРТПЛОЩАДКА", 11, fill="#fff", font_weight="bold", stroke="#5a9e6f", stroke_width=4, paint_order="stroke"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 + 0.35, f"{x1 - x0:g}×{y1 - y0_:g} м", 10, fill="#fff", stroke="#5a9e6f", stroke_width=4, paint_order="stroke"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 - 0.9, "бадминтон · волейбол", 9, fill="#fff", stroke="#5a9e6f", stroke_width=4, paint_order="stroke"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 - 1.5, "турник · батут", 9, fill="#fff", stroke="#5a9e6f", stroke_width=4, paint_order="stroke"))
# бассейн
x0, y0_, x1, y1 = LEISURE["pool"]
LS.append(lrect_svg(x0 - 0.4, y0_ - 0.4, x1 + 0.4, y1 + 0.4, fill="#e9e1cf", stroke="#b8ab8a", stroke_width=1))
LS.append(lrect_svg(x0, y0_, x1, y1, fill="#5bb8e6", stroke="#1f7fb0", stroke_width=2))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 + 0.3, "бассейн", 10, fill="#fff", font_weight="bold"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 - 0.4, f"{x1 - x0:g}×{y1 - y0_:g} м", 9, fill="#fff"))
# купель
X, Y, r = LEISURE["tub"]
cx, cy = sv(local(X, Y))
LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(r + 0.3) * SC:.1f}" fill="#c9a36b" stroke="#6b4f1d" stroke-width="1"/>')
LS.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * SC:.1f}" fill="#7fd0e8" stroke="#1f7fb0" stroke-width="2"/>')
LS.append(lbl(X, Y + 0.1, "купель", 10, font_weight="bold", fill="#0d3b52"))
LS.append(lbl(X, Y - 0.5, f"Ø{2 * r:g} м", 9, fill="#0d3b52"))
# песочница и качели
x0, y0_, x1, y1 = LEISURE["sand"]
LS.append(lrect_svg(x0, y0_, x1, y1, fill="#f1d98a", stroke="#a8893a", stroke_width=1.5))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 + 0.1, "песочница", 9, font_weight="bold"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 - 0.5, "2×2 м", 9))
x0, y0_, x1, y1 = LEISURE["swing"]
LS.append(lrect_svg(x0, y0_, x1, y1, fill="#f4c7a1", stroke="#b0703a", stroke_width=1.5))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 + 0.1, "качели / горка", 9, font_weight="bold"))
LS.append(lbl((x0 + x1) / 2, (y0_ + y1) / 2 - 0.5, "детская зона", 9))

# проверка: всё внутри участка, не пересекается с домом/террасами/парковкой
_house_blocks = [lrect(*b) for b in HOUSE_BLOCKS] + [lrect(*t[1:]) for t in TERRACES]
for k, v in LEISURE.items():
    poly = lrect(v[0] - v[2], v[1] - v[2], v[0] + v[2], v[1] + v[2]) if k == "tub" else lrect(*v)
    ok_in = all(inside(P, c) for c in poly)
    hits = [i for i, b in enumerate(_house_blocks) if overlap(b, poly, 0.0)] if k != "path" else []
    print(f"{k}: внутри участка={ok_in}, пересечения с домом/террасами={hits}, с парковкой={overlap(PARK, poly)}, "
          f"мин. до забора={min(min(dist_to_line_any(c) for c in poly) for _ in [0]):.2f} м")

TERR_AREA = sum(abs((t[3] - t[1]) * (t[4] - t[2])) for t in TERRACES)
FREE = area(P) - HOUSE_AREA - TERR_AREA - PARK_W * PARK_D

W, H = (maxx - minx) * SC, (maxy - miny) * SC + 90
el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" fill="#fff"/>',
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#0b5cad"/></marker></defs>',
    *LS,
    *ROOMS_SVG,
    *DIM_SVG,
    text(centroid(PARK), "P · 2 авто", 13, font_weight="bold"),
    text((centroid(PARK)[0], centroid(PARK)[1] - 1.0), f"{PARK_W:g}×{PARK_D:g} м", 11),
    text(mid(A, B, -0.9), f"{AB} м · ЮГ (солнце днём)", 14, fill="#8a5a00"),
    text(mid(C, D, 0.6), f"{CD} м · СЕВЕР", 14),
    text(mid(D, A, 0), f"{DA} м", 14, transform=""),
    text(mid(B, C, 0), "", 14),
]
mx, my = sv(mid(D, A)); el[-2] = f'<text x="{mx-30:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{DA} м</text>'
mx, my = sv(mid(B, C)); el[-1] = f'<text x="{mx+38:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{BC} м</text><text x="{mx+75:.1f}" y="{my:.1f}" font-size="15" font-weight="bold" text-anchor="middle" font-family="sans-serif" transform="rotate(-90 {mx+75:.1f} {my:.1f})">ул. 1905 года · ВОСТОК</text>'
# стрелка въезда
e1 = sv(to_xy(park_s + PARK_W / 2, -2.5)); e2 = sv(to_xy(park_s + PARK_W / 2, 0.5))
el.append(f'<line x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e2[0]:.1f}" y2="{e2[1]:.1f}" stroke="#222" stroke-width="2.5"/><circle cx="{e2[0]:.1f}" cy="{e2[1]:.1f}" r="4"/>')
el.append(text((3.9, 2.4), "газон", 14, fill="#2f3b12", font_style="italic"))
el.append(text((8.6, 0.45), "кустарник / живая изгородь", 9, fill="#2f3b12", font_style="italic"))

# ---------- стороны света и окружение (по Яндекс.Картам: участок на западной стороне ул. 1905 года) ----------
NORTH_DEG = -4.6  # север повёрнут на ~5° против часовой от «верха» схемы (по направлению улицы)
cx, cy = 70, 80
el.append(f'<g transform="rotate({NORTH_DEG} {cx} {cy})">'
          f'<circle cx="{cx}" cy="{cy}" r="34" fill="#fff" stroke="#333" stroke-width="1.5"/>'
          f'<path d="M{cx},{cy - 30} L{cx + 9},{cy + 6} L{cx},{cy} L{cx - 9},{cy + 6} z" fill="#c0392b"/>'
          f'<path d="M{cx},{cy + 30} L{cx + 9},{cy - 6} L{cx},{cy} L{cx - 9},{cy - 6} z" fill="#999"/>'
          f'<text x="{cx}" y="{cy - 38}" font-size="16" font-weight="bold" text-anchor="middle" font-family="sans-serif">С</text></g>')
ax, ay = sv((1.0, 17.8))
el.append(f'<text x="{ax:.1f}" y="{ay:.1f}" font-size="12" fill="#5a2d82" font-weight="bold" font-family="sans-serif">↖ ж/д МЦД-1 (Баковка) ≈50 м — шум</text>')
lx, ly = sv((1.2, 9.0))
el.append(f'<text x="{lx - 70:.1f}" y="{ly:.1f}" font-size="12" fill="#1f7fb0" font-weight="bold" text-anchor="middle" font-family="sans-serif" '
          f'transform="rotate(-66 {lx - 70:.1f} {ly:.1f})">ЗАПАД · ручей ≈10–20 м · вечернее солнце</text>')
mx2, my2 = sv((30.2, -1.2))
el.append(f'<text x="{mx2:.1f}" y="{my2:.1f}" font-size="12" fill="#555" font-family="sans-serif">↘ Минское ш. ≈100 м</text>')
y0 = (maxy - miny) * SC + 25
el.append(f'<rect x="20" y="{y0-12}" width="28" height="0" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<line x1="20" y1="{y0-5}" x2="50" y2="{y0-5}" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<text x="58" y="{y0}" font-size="13" font-family="sans-serif">граница пятна застройки: отступ {SETBACK:g} м от всех границ</text>')
el.append(f'<text x="20" y="{y0+24}" font-size="13" font-family="sans-serif">участок ≈{area(P):.0f} м² · дом {HOUSE_AREA:.1f} м² (7 модулей DP-Module) · террасы {TERR_AREA:.0f} м² · парковка {PARK_W*PARK_D:.0f} м² · двор/сад ≈{FREE:.0f} м² (в т.ч. бассейн, купель, площадки)</text>')
el.append(f'<text x="20" y="{y0-30}" font-size="14" font-weight="bold" font-family="sans-serif">ИЖС, Одинцово, ул. 1905 года · ПЗЗ (обычно для ИЖС в МО): отступ 3 м, застройка ≤40% → дом {HOUSE_AREA/area(P)*100:.0f}%, с террасами {(HOUSE_AREA+TERR_AREA)/area(P)*100:.0f}% (уточнить по ГПЗУ)</text>')
el.append(f'<text x="20" y="{y0+46}" font-size="13" fill="#0b5cad" font-family="sans-serif">синие размеры — расстояние от стены дома / края террасы до забора</text>')
el.append("</svg>")
open("plan.svg", "w").write("\n".join(el))

print("угол при A:", round(math.degrees(best_a), 1))
print("участок:", [tuple(round(c, 2) for c in p) for p in P], "площадь", round(area(P), 1))
print("пятно застройки:", round(area(BUILD), 1), "м²")
def dist_to_line(p, a, b):
    return abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / math.hypot(b[0] - a[0], b[1] - a[1])


print(f"дом {HOUSE_AREA:.1f} м²; до дороги {min(dist_to_line(p, B, C) for p in HOUSE):.2f} м; "
      f"до низа {min(dist_to_line(p, A, B) for p in HOUSE):.2f}; до верха {min(dist_to_line(p, C, D) for p in HOUSE):.2f}; "
      f"до левой {min(dist_to_line(p, D, A) for p in HOUSE):.2f}")
print("террасы внутри пятна:", [all(inside(BUILD, c) for c in lrect(*t[1:])) for t in TERRACES], "внутри участка:", [all(inside(P, c) for c in lrect(*t[1:])) for t in TERRACES])
print("сумма комнат:", sum(abs((r[3]-r[1])*(r[4]-r[2])) for r in ROOMS))
print("парковка s=", round(park_s, 1))
