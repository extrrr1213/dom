"""Быстрая модель размещения дома (~105 м²) и парковки на 2 машины на участке 4.5 сот."""
import math

AB, BC, CD, DA, AREA = 30.7, 16.3, 24.2, 18.0, 450.0  # низ, дорога, верх, лево
SETBACK = 3.0          # отступ дома от границ (по запросу)
HOUSE_AREA = 105.0
PARK_W, PARK_D = 5.5, 5.5  # 2 машины рядом: 2×2.75 × 5.5 м


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


# парковка: у дороги, у нижнего угла (въезд с дороги)
park_s = 0.0
while not all(inside(P, c) for c in rect(park_s, 0, PARK_W, PARK_D)):
    park_s += 0.1
park_s += 0.5
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
    ("терраса", 14.0, 1.2, 16.0, 4.8),   # у дороги, на стыке кухни-столовой и гостиной
    ("терраса", -2.0, 2.8, 0.0, 6.5),    # в сад, на стыке спальни, коридора и мастер-спальни
]
DOORS = [("вход", 14.0, 3.8, 15.0, 5.3), ("выход в сад", 0.0, 4.65, -1.0, 7.0)]


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
for yi in range(30, 80):
    y0 = yi * 0.1
    for xi in range(320, 100, -1):
        xe = xi * 0.1
        loc = place(xe, y0)
        blocks = [[loc(x0, b0), loc(x1, b0), loc(x1, b1), loc(x0, b1)] for x0, b0, x1, b1 in HOUSE_BLOCKS]
        road_t, garden_t = ([loc(x0, b0), loc(x1, b0), loc(x1, b1), loc(x0, b1)] for _, x0, b0, x1, b1 in TERRACES)
        if (all(inside(BUILD, loc(*p)) for p in OUTLINE)
                and all(inside(BUILD, c) for c in road_t)
                and all(inside(P, c) for c in garden_t)
                and not any(overlap(bl, PARK, 1.0) for bl in blocks)
                and not overlap(road_t, PARK)):  # терраса может примыкать к парковке
            if best is None or xe > best[0]:
                best = (xe, y0)
            break
xe, y0 = best
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
    c = centroid(pts)
    ROOMS_SVG.append(text((c[0], c[1] + 0.2), name, 10))
    ROOMS_SVG.append(text((c[0], c[1] - 0.5), f"{abs((x1 - x0) * (y1 - y0)):.1f} м²", 9))
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

W, H = (maxx - minx) * SC, (maxy - miny) * SC + 70
el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" fill="#fff"/>',
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    *ROOMS_SVG,
    text(centroid(PARK), "P · 2 авто", 13, font_weight="bold"),
    text((centroid(PARK)[0], centroid(PARK)[1] - 1.0), f"{PARK_W:g}×{PARK_D:g} м", 11),
    text(mid(A, B, -1.5), f"{AB} м", 14),
    text(mid(C, D, 1.0), f"{CD} м", 14),
    text(mid(D, A, 0), f"{DA} м", 14, transform=""),
    text(mid(B, C, 0), "", 14),
]
mx, my = sv(mid(D, A)); el[-2] = f'<text x="{mx-30:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{DA} м</text>'
mx, my = sv(mid(B, C)); el[-1] = f'<text x="{mx+38:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{BC} м</text><text x="{mx+75:.1f}" y="{my:.1f}" font-size="15" font-weight="bold" text-anchor="middle" font-family="sans-serif" transform="rotate(-90 {mx+75:.1f} {my:.1f})">ДОРОГА</text>'
# стрелка въезда
e1 = sv(to_xy(park_s + PARK_W / 2, -2.5)); e2 = sv(to_xy(park_s + PARK_W / 2, 0.5))
el.append(f'<line x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e2[0]:.1f}" y2="{e2[1]:.1f}" stroke="#222" stroke-width="2.5"/><circle cx="{e2[0]:.1f}" cy="{e2[1]:.1f}" r="4"/>')
garden = ((A[0] + D[0]) / 2 + 4, (A[1] + D[1]) / 2 - 5)
el.append(text(garden, "сад / двор", 15, fill="#2f3b12", font_style="italic"))
y0 = (maxy - miny) * SC + 25
el.append(f'<rect x="20" y="{y0-12}" width="28" height="0" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<line x1="20" y1="{y0-5}" x2="50" y2="{y0-5}" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<text x="58" y="{y0}" font-size="13" font-family="sans-serif">граница пятна застройки: отступ {SETBACK:g} м от всех границ</text>')
el.append(f'<text x="20" y="{y0+24}" font-size="13" font-family="sans-serif">участок ≈{area(P):.0f} м² · дом {HOUSE_AREA:.1f} м² (7 модулей DP-Module) · застройка {HOUSE_AREA/area(P)*100:.0f}% · масштаб: 1 м = {SC}px</text>')
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
