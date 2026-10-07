"""Участок 4.5 сот. (Одинцово, ул. 1905 года) с домом DP-Module «Дабл» 160-2: 3 модуля 3×7 м на этаж (9×7 м),
терраса 9×2 м у входа (над ней балкон), 2 этажа, ≈160 м², ДxШxВ 9000×9000×5800 мм.
Дом в глубине участка, терраса и вход — на восток, к парковке; 2 авто РЯДОМ у дороги (откатные ворота 6 м со
встроенной калиткой); бассейн 8×4 м на солнечном юго-востоке, купель рядом; спортплощадка и газон на западе."""
import math

AB, BC, CD, DA, AREA = 30.7, 16.3, 24.2, 18.0, 450.0  # юг, дорога (восток), север, запад
SETBACK = 3.0
BODY, TERR, WIDTH = 7.0, 2.0, 9.0   # глубина дома, терраса, ширина фасада (3 модуля по 3 м)


def shape(a):
    A, B = (0.0, 0.0), (AB, 0.0)
    D = (DA * math.cos(a), DA * math.sin(a))
    dx, dy = B[0] - D[0], B[1] - D[1]
    L = math.hypot(dx, dy)
    x = (CD**2 - BC**2 + L**2) / (2 * L)
    h = math.sqrt(max(CD**2 - x**2, 0))
    ux, uy = dx / L, dy / L
    return [A, B, (D[0] + ux * x - uy * h, D[1] + uy * x + ux * h), D]


def area(p):
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2


lo, hi = math.radians(60), math.radians(120)
best_a = min((abs(area(shape(lo + (hi - lo) * i / 20000)) - AREA), lo + (hi - lo) * i / 20000) for i in range(20001))[1]
P = shape(best_a)
A, B, C, D = P


def inset(poly, d):
    n, lines, out = len(poly), [], []
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        lines.append(((p[0] - dy / L * d, p[1] + dx / L * d), (dx, dy)))
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / (d1[0] * d2[1] - d1[1] * d2[0])
        out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
    return out


def inside(poly, pt):
    return all((poly[(i + 1) % len(poly)][0] - poly[i][0]) * (pt[1] - poly[i][1])
               - (poly[(i + 1) % len(poly)][1] - poly[i][1]) * (pt[0] - poly[i][0]) >= -1e-9 for i in range(len(poly)))


def overlap(p1, p2):
    """Пересекаются ли два выпуклых многоугольника (касание — не пересечение)."""
    for poly in (p1, p2):
        for i in range(len(poly)):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
            nx, ny = y1 - y2, x2 - x1
            a = [x * nx + y * ny for x, y in p1]
            b = [x * nx + y * ny for x, y in p2]
            if max(a) <= min(b) + 1e-9 or max(b) <= min(a) + 1e-9:
                return False
    return True


def seg_dist(p, a, b):
    ex, ey = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / (ex * ex + ey * ey)))
    return math.hypot(p[0] - a[0] - ex * t, p[1] - a[1] - ey * t)


def poly_gap(p1, p2):
    return min(min(seg_dist(p, q[i], q[(i + 1) % len(q)]) for p in s for i in range(len(q))) for s, q in ((p1, p2), (p2, p1)))


def dist_to_line(p, a, b):
    return abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / math.hypot(b[0] - a[0], b[1] - a[1])


def dist_to_fence(p):
    return min(dist_to_line(p, P[i], P[(i + 1) % 4]) for i in range(4))


def x_road(y):
    return B[0] + (C[0] - B[0]) * y / C[1]


def x_west(y):
    return D[0] * y / D[1]


def y_north(x):
    return D[1] + (C[1] - D[1]) * (x - D[0]) / (C[0] - D[0])


def xyrect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle_poly(cx, cy, r, n=32):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


BUILD = inset(P, SETBACK)

# ---------- парковка: 2 авто РЯДОМ у дороги, в северо-восточном углу ----------
PARK_D, PARK_W = 6.5, 7.0
park_y0 = C[1] - PARK_W                      # площадка до северного забора
park_x0 = x_road(park_y0) - PARK_D
PARK = [(park_x0, park_y0), (x_road(park_y0), park_y0), C, (park_x0, y_north(park_x0))]
# откатные ворота 6 м по центру площадки, откат ≈1.5 проёма вдоль забора на юг; калитка — в полотне ворот
GATE_W = 6.0
GATE_Y0 = park_y0 + (PARK_W - GATE_W) / 2
GATE_ROLL = (GATE_Y0 - 1.5 * GATE_W, GATE_Y0)
CARS = (GATE_Y0 + 0.4 + 0.95, GATE_Y0 + GATE_W - 0.4 - 0.95)   # оси машин, по 0.4 м до столбов ворот

# ---------- бассейн 8×4 м на юго-востоке (≥0.5 м от зоны отката ворот) ----------
DECK = 0.4
_px1 = math.floor((x_road(0.5) - 0.35 - 0.5 - DECK) * 10) / 10
POOL = (_px1 - 8.0, 0.9, _px1, 4.9)

# ---------- дом: терраса и вход на восток, в 0.8 м от настила бассейна; в 3 м от южного забора ----------
HY0 = SETBACK
HX1 = POOL[0] - DECK - 0.8                   # восточный край террасы
HX0 = HX1 - BODY - TERR                      # западная стена
HB1 = HX0 + BODY                             # восточная стена дома (терраса — восточнее)
HOUSE_P = xyrect(HX0, HY0, HB1, HY0 + WIDTH)
TERR_P = xyrect(HB1, HY0, HX1, HY0 + WIDTH)
# помещения 1 этажа (по чертежу DP-Module; модули 3×7 м: север — прихожая и лестница, середина — техпом. и с/у,
# юг — кухня; кухня-гостиная открытая, смотрит на террасу)
V_BACK = 3.8                                 # глубина «задних» помещений (техпом., с/у, кухня) от западной стены
ROOMS = [
    ("Прихожая · лестница", [(HX0, HY0 + 6), (HB1, HY0 + 6), (HB1, HY0 + 9), (HX0, HY0 + 9)], "#eeeeee"),
    ("Техпом.", xyrect(HX0, HY0 + 3, HX0 + 1.6, HY0 + 6), "#e6e0f0"),
    ("Санузел", xyrect(HX0 + 1.6, HY0 + 3, HX0 + V_BACK, HY0 + 6), "#d6f0ee"),
    ("Кухня-гостиная", [(HX0, HY0), (HB1, HY0), (HB1, HY0 + 6), (HX0 + V_BACK, HY0 + 6), (HX0 + V_BACK, HY0 + 3), (HX0, HY0 + 3)],
     "#fbf1d6"),
]
STAIR = (HX0, HY0 + 7.8, HX0 + V_BACK, HY0 + 9)
DOOR_IN = (HB1, HY0 + 6.9)
PATH = (HX1, DOOR_IN[1] - 0.6, park_x0, DOOR_IN[1] + 0.6)        # дорожка терраса -> парковка
TUB_DECK = 0.3
TUB = (HX1 + 0.8 + TUB_DECK + 1.0, (POOL[3] + DECK + PATH[1]) / 2, 1.0)   # купель между бассейном и дорожкой

# ---------- спортплощадка на западе (С–Ю), 0.8 м до стены дома, ≥0.5 м до забора ----------
SP_X1 = round(HX0 - 0.8, 1)
SP_X0 = round(SP_X1 - 6.1, 1)
SP_Y1 = math.floor((SP_X0 - 0.5) / (D[0] / D[1]) * 10) / 10
SPORT = (SP_X0, 0.5, SP_X1, SP_Y1)

OBJ = {
    "дом": HOUSE_P, "терраса": TERR_P, "парковка": PARK, "дорожка": xyrect(*PATH),
    "бассейн+настил": xyrect(POOL[0] - DECK, POOL[1] - DECK, POOL[2] + DECK, POOL[3] + DECK),
    "купель+настил": circle_poly(TUB[0], TUB[1], TUB[2] + TUB_DECK),
    "спортплощадка": xyrect(*SPORT),
}
SHRUBS = ([(x, 1.2, 0.55) for x in (12.2, 15.9, 18.0)]                                    # у южного забора
          + [(x, y_north(x) - 1.1, 0.55) for x in (8.6, 10.6, 12.6, 17.0, 19.0, 21.0, 23.0)])  # у северного

print(f"дом x {HX0:.2f}..{HB1:.2f} + терраса до {HX1:.2f}, y {HY0:.2f}..{HY0 + WIDTH:.2f}")
print("--- проверки ---")
print("дом и терраса в пятне застройки:", all(inside(BUILD, c) for c in HOUSE_P + TERR_P))
print("внутри участка:", {k: all(inside(P, c) for c in v) for k, v in OBJ.items()})
names, hits = list(OBJ), []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        if overlap(OBJ[names[i]], OBJ[names[j]]):
            hits.append((names[i], names[j]))
print("пересечения:", hits or "нет")
for X, Y, r in SHRUBS:
    assert dist_to_fence((X, Y)) >= 1.0 - 1e-6, (X, Y)
    for k, v in OBJ.items():
        assert not overlap(circle_poly(X, Y, r, 12), v), (X, Y, k)
print("кусты: центры ≥1 м от заборов, без наложений")
for a_, b_ in [("терраса", "бассейн+настил"), ("купель+настил", "бассейн+настил"), ("купель+настил", "дорожка"),
               ("купель+настил", "терраса"), ("спортплощадка", "дом"), ("парковка", "терраса")]:
    print(f"  зазор {a_} — {b_}: {poly_gap(OBJ[a_], OBJ[b_]):.2f} м")
print(f"  настил бассейна до линии отката ворот: {x_road(POOL[1] - DECK) - 0.35 - (POOL[2] + DECK):.2f} м")
for k in ("спортплощадка", "бассейн+настил", "купель+настил"):
    print(f"  {k}: до забора {min(dist_to_fence(c) for c in OBJ[k]):.2f} м")
print(f"ворота y {GATE_Y0:.2f}..{GATE_Y0 + GATE_W:.2f}, откат y {GATE_ROLL[0]:.2f}..{GATE_ROLL[1]:.2f}; "
      f"машины y {CARS[0] - 0.95:.2f}..{CARS[0] + 0.95:.2f} и {CARS[1] - 0.95:.2f}..{CARS[1] + 0.95:.2f}")
print(f"парковка {PARK_W:g} × {PARK_D:g}–{x_road(C[1]) - park_x0:.2f} м = {area(PARK):.1f} м²; "
      f"спортплощадка {SP_X1 - SP_X0:.1f} × {SP_Y1 - 0.5:.1f} м; бассейн x {POOL[0]:.1f}..{POOL[2]:.1f}")

# ---------- SVG ----------
xs, ys = [p[0] for p in P], [p[1] for p in P]
minx, maxx, miny, maxy = min(xs) - 4, max(xs) + 8, min(ys) - 4, max(ys) + 4
SC = 32


def sv(p):
    return ((p[0] - minx) * SC, (maxy - p[1]) * SC)


def poly_svg(pts, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in map(sv, pts))}" {attrs}/>'


def rect_svg(r, **kw):
    return poly_svg(xyrect(*r), **kw)


def text(p, s, size=13, **kw):
    x, y = sv(p)
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="middle" font-family="sans-serif" {attrs}>{s}</text>'


def line_svg(p, q, **kw):
    (x1, y1), (x2, y2) = sv(p), sv(q)
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {attrs}/>'


def mid(a, b, off=0.0):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + off)


def ray_to_fence(p, d):
    best_k = None
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        k = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
        m = ((a[0] - p[0]) * d[1] - (a[1] - p[1]) * d[0]) / den
        if k > 1e-6 and -1e-9 <= m <= 1 + 1e-9 and (best_k is None or k < best_k):
            best_k = k
    return (p[0] + d[0] * best_k, p[1] + d[1] * best_k), best_k


HALO = dict(stroke="#5a9e6f", stroke_width=4, paint_order="stroke")
el = [
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    '<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#0b5cad"/></marker></defs>',
]
# две машины рядом (≈4.7 × 1.9 м, носом на запад), внутри створа ворот
for cyc in CARS:
    (ax, ay), (bx, by) = sv((park_x0 + 0.9, cyc + 0.95)), sv((park_x0 + 0.9 + 4.7, cyc - 0.95))
    el.append(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bx - ax:.1f}" height="{by - ay:.1f}" rx="10" fill="#d4d4d4" '
              f'stroke="#888" stroke-width="1.2" stroke-dasharray="5 3"/>')
# дорожка, кусты
el.append(rect_svg(PATH, fill="#d9d4c7", stroke="#9a927e", stroke_width=1))
for X, Y, r in SHRUBS:
    cx, cy = sv((X, Y))
    el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * SC:.1f}" fill="#5f8a3a" stroke="#3d5e22" stroke-width="1" opacity="0.9"/>')
# спортплощадка
sx0, sy0, sx1, sy1 = SPORT
scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
el.append(rect_svg(SPORT, fill="#5a9e6f", stroke="#ffffff", stroke_width=2))
el.append(rect_svg((sx0 + 0.3, sy0 + 0.3, sx1 - 0.3, sy1 - 0.3), fill="none", stroke="#ffffff", stroke_width=1.2))
el.append(line_svg((sx0, scy), (sx1, scy), stroke="#ffffff", stroke_width=3, stroke_dasharray="3 2"))
_net = [(sx1 + 0.15, sy1 + 0.15), (sx0 - 0.15, sy1 + 0.15), (sx0 - 0.15, sy0 - 0.15), (sx1 + 0.15, sy0 - 0.15)]
el.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in map(sv, _net))}" fill="none" stroke="#2e5e3a" '
          f'stroke-width="2.5" stroke-dasharray="2 2"/>')
for dy, s, fs, bold in ((2.6, "СПОРТПЛОЩАДКА", 12, True), (1.95, f"{sx1 - sx0:.1f}×{sy1 - sy0:.1f} м · {(sx1 - sx0) * (sy1 - sy0):.0f} м²", 11, False),
                        (-1.2, "бадминтон · пионербол", 9, False), (-1.8, "турник · батут", 9, False),
                        (-2.4, "сетка 3 м (пунктир)", 9, False)):
    el.append(text((scx, scy + dy), s, fs, fill="#fff", **({"font_weight": "bold"} if bold else {}), **HALO))
# бассейн и купель
el.append(rect_svg((POOL[0] - DECK, POOL[1] - DECK, POOL[2] + DECK, POOL[3] + DECK), fill="#e9e1cf", stroke="#b8ab8a", stroke_width=1))
el.append(rect_svg(POOL, fill="#5bb8e6", stroke="#1f7fb0", stroke_width=2))
el.append(text(((POOL[0] + POOL[2]) / 2, (POOL[1] + POOL[3]) / 2 + 0.3), "бассейн", 12, fill="#fff", font_weight="bold"))
el.append(text(((POOL[0] + POOL[2]) / 2, (POOL[1] + POOL[3]) / 2 - 0.45), "8×4 м", 11, fill="#fff"))
cx, cy = sv(TUB[:2])
el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{(TUB[2] + TUB_DECK) * SC:.1f}" fill="#c9a36b" stroke="#6b4f1d" stroke-width="1"/>')
el.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{TUB[2] * SC:.1f}" fill="#7fd0e8" stroke="#1f7fb0" stroke-width="2"/>')
el.append(text((TUB[0], TUB[1] + 0.1), "купель", 10, font_weight="bold", fill="#0d3b52"))
el.append(text((TUB[0], TUB[1] - 0.5), "Ø2 м", 9, fill="#0d3b52"))
# дом «Дабл»: терраса, помещения 1 этажа, лестница
el.append(poly_svg(TERR_P, fill="#c9a36b", stroke="#6b4f1d", stroke_width=1.5))
for k in (1, 2):   # стойки террасы на стыках модулей
    py = HY0 + 3 * k
    el.append(line_svg((HB1, py), (HX1, py), stroke="#6b4f1d", stroke_width=1, stroke_dasharray="3 3"))
tc = ((HB1 + HX1) / 2, HY0 + 2.2)
for dy, s in ((0.9, "терраса"), (0.3, "у входа"), (-0.3, "2×9 м"), (-0.9, "18 м²"), (-1.5, "над ней"), (-2.0, "балкон")):
    el.append(text((tc[0], tc[1] + dy), s, 9))
el.append(poly_svg(HOUSE_P, fill="#f3e6c8", stroke="#6b4f1d", stroke_width=3))
for name, pts, col in ROOMS:
    el.append(poly_svg(pts, fill=col, stroke="#6b4f1d", stroke_width=1.2))
el.append(rect_svg(STAIR, fill="#ffffff", stroke="#6b4f1d", stroke_width=1))
for k in range(1, 9):
    sx = STAIR[0] + (STAIR[2] - STAIR[0]) * k / 9
    el.append(line_svg((sx, STAIR[1]), (sx, STAIR[3]), stroke="#6b4f1d", stroke_width=0.8))
el.append(poly_svg(HOUSE_P, fill="none", stroke="#6b4f1d", stroke_width=3))
el.append(text((HX0 + V_BACK / 2, STAIR[1] + 0.45), "лестница", 9, fill="#6b4f1d"))
el.append(text((HX0 + BODY / 2 + 0.6, HY0 + 7.2), "Прихожая", 11, font_weight="bold"))
el.append(text((HX0 + BODY / 2 + 0.6, HY0 + 6.6), "21.0 м² (с лестницей)", 9))
el.append(text((HX0 + 0.8, HY0 + 4.6), "Тех-", 9, font_weight="bold"))
el.append(text((HX0 + 0.8, HY0 + 4.2), "пом.", 9, font_weight="bold"))
el.append(text((HX0 + 0.8, HY0 + 3.6), "4.8 м²", 8))
el.append(text((HX0 + 1.6 + (V_BACK - 1.6) / 2, HY0 + 4.6), "Санузел", 9, font_weight="bold"))
el.append(text((HX0 + 1.6 + (V_BACK - 1.6) / 2, HY0 + 4.0), "6.6 м²", 8))
el.append(text((HX0 + BODY / 2, HY0 + 2.0), "Кухня-гостиная", 12, font_weight="bold"))
el.append(text((HX0 + BODY / 2, HY0 + 1.35), "30.6 м²", 10))
el.append(text((HX0 + V_BACK + (BODY - V_BACK) / 2, HY0 + 4.5), "окна", 9, fill="#6b4f1d"))
el.append(text((HX0 + V_BACK + (BODY - V_BACK) / 2, HY0 + 4.05), "на террасу", 9, fill="#6b4f1d"))
dx_, dy_ = sv(DOOR_IN)
el.append(f'<circle cx="{dx_:.1f}" cy="{dy_:.1f}" r="5" fill="#c0392b"/>')
el.append(text((HB1 + 1.0, DOOR_IN[1] + 0.85), "вход", 10, fill="#c0392b", font_weight="bold"))
el.append(text(((HX0 + 3.5 + park_x0) / 2 + 0.3, HY0 + WIDTH + 0.95), "«Дабл» 160-2 · 9×9 м с террасой", 11, font_weight="bold"))
el.append(text(((HX0 + 3.5 + park_x0) / 2 + 0.3, HY0 + WIDTH + 0.4), "2 этажа · ≈160 м² · 6 модулей", 10))

# размерные линии: от стены дома / края террасы до забора
DIM_SVG = []
for (X, Y), d in (((HX0 + 3.5, HY0), (0, -1)), ((HX0 + 3.5, HY0 + WIDTH), (0, 1)), ((HX0, HY0 + 7.3), (-1, 0))):
    q, dist = ray_to_fence((X, Y), d)
    (x1, y1), (x2, y2) = sv((X, Y)), sv(q)
    DIM_SVG.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#0b5cad" stroke-width="1.6" '
                   f'marker-start="url(#arr)" marker-end="url(#arr)"/>')
    mx, my, lbl = (x1 + x2) / 2, (y1 + y2) / 2, f"{dist:.1f} м"
    if d[0] == 0:
        DIM_SVG.append(f'<rect x="{mx + 4:.1f}" y="{my - 9:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx + 8:.1f}" y="{my + 4:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" font-family="sans-serif">{lbl}</text>')
    else:
        DIM_SVG.append(f'<rect x="{mx - len(lbl) * 3.75:.1f}" y="{my - 20:.1f}" width="{len(lbl) * 7.5:.0f}" height="16" rx="3" fill="#fff" opacity="0.85"/>'
                       f'<text x="{mx:.1f}" y="{my - 7:.1f}" font-size="12" font-weight="bold" fill="#0b5cad" text-anchor="middle" font-family="sans-serif">{lbl}</text>')
    print(f"размер от ({X:.2f}, {Y:.2f}) по {d}: {dist:.2f} м")
el += DIM_SVG
ROAD_GAP = min(dist_to_line(c, B, C) for c in TERR_P)

# парковка, ворота, стороны
pc = (park_x0 + PARK_D / 2 + 0.2, sum(CARS) / 2)
el += [
    text((pc[0], pc[1] + 0.3), "P · 2 авто рядом", 13, font_weight="bold"),
    text((pc[0], pc[1] - 0.35), f"{PARK_W:g}×{PARK_D:g} м · {area(PARK):.0f} м² · бетон", 10),
    text((pc[0], CARS[1] - 0.15), "место 2", 10, fill="#444"),
    text((pc[0], CARS[0] - 0.15), "место 1", 10, fill="#444"),
    text(mid(A, B, -0.9), f"{AB} м · ЮГ (солнце днём)", 14, fill="#8a5a00"),
    text(mid(C, D, 0.6), f"{CD} м · СЕВЕР", 14),
]
el.append(line_svg((x_road(GATE_Y0), GATE_Y0), (x_road(GATE_Y0 + GATE_W), GATE_Y0 + GATE_W), stroke="#333", stroke_width=5))
el.append(line_svg((x_road(GATE_ROLL[0]) - 0.35, GATE_ROLL[0]), (x_road(GATE_ROLL[1]) - 0.35, GATE_ROLL[1]),
                   stroke="#333", stroke_width=2, stroke_dasharray="7 4"))
_rm = sv((x_road(sum(GATE_ROLL) / 2) - 0.8, sum(GATE_ROLL) / 2 - 1.2))
el.append(f'<text x="{_rm[0]:.1f}" y="{_rm[1]:.1f}" font-size="10" text-anchor="middle" font-family="sans-serif" fill="#333" '
          f'transform="rotate(-90 {_rm[0]:.1f} {_rm[1]:.1f})">откат ворот ≈{GATE_ROLL[1] - GATE_ROLL[0]:.1f} м</text>')
gy = GATE_Y0 + GATE_W / 2
el.append(line_svg((x_road(gy) + 2.5, gy), (x_road(gy) - 0.5, gy), stroke="#222", stroke_width=2.5))
ex2, ey2 = sv((x_road(gy) - 0.5, gy))
el.append(f'<circle cx="{ex2:.1f}" cy="{ey2:.1f}" r="4"/>')
el.append(text((x_road(gy) + 1.6, gy + 0.3), "ворота", 10, fill="#222", font_weight="bold"))
el.append(text((x_road(gy) + 1.6, gy - 0.9), f"откатные {GATE_W:g} м", 10, fill="#222"))
el.append(text((x_road(gy) + 1.6, gy - 1.5), "калитка в полотне", 10, fill="#222"))
mx, my = sv(mid(D, A))
el.append(f'<text x="{mx - 30:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{DA} м</text>')
mx, my = sv(mid(B, C))
el.append(f'<text x="{mx + 38:.1f}" y="{my:.1f}" font-size="14" text-anchor="middle" font-family="sans-serif">{BC} м</text>'
          f'<text x="{mx + 75:.1f}" y="{my:.1f}" font-size="15" font-weight="bold" text-anchor="middle" font-family="sans-serif" '
          f'transform="rotate(-90 {mx + 75:.1f} {my:.1f})">ул. 1905 года · ВОСТОК</text>')
el.append(text((7.4, 11.6), "газон", 14, fill="#2f3b12", font_style="italic"))
el.append(text((11.5, 13.6), "газон", 14, fill="#2f3b12", font_style="italic"))
el.append(text((15.2, 0.25), "кустарник / живая изгородь", 9, fill="#2f3b12", font_style="italic"))

# стороны света и окружение (как на plan.png)
NORTH_DEG = -4.6
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

HOUSE_A, TERR_A = BODY * WIDTH, TERR * WIDTH
FREE = area(P) - HOUSE_A - TERR_A - area(PARK)
W, H = (maxx - minx) * SC, (maxy - miny) * SC + 112
ly = (maxy - miny) * SC + 25
legend = [
    f'<text x="20" y="{ly - 30}" font-size="14" font-weight="bold" font-family="sans-serif">ИЖС, Одинцово, ул. 1905 года · ПЗЗ (обычно для ИЖС в МО): '
    f'отступ 3 м, застройка ≤40% → дом {HOUSE_A / area(P) * 100:.0f}%, с террасой {(HOUSE_A + TERR_A) / area(P) * 100:.0f}% (уточнить по ГПЗУ)</text>',
    f'<line x1="20" y1="{ly - 5}" x2="50" y2="{ly - 5}" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>',
    f'<text x="58" y="{ly}" font-size="13" font-family="sans-serif">граница пятна застройки: отступ {SETBACK:g} м от всех границ</text>',
    f'<text x="20" y="{ly + 24}" font-size="13" font-family="sans-serif">участок ≈{area(P):.0f} м² · дом «Дабл» 160-2: 9×7 м = {HOUSE_A:.0f} м² '
    f'+ терраса {TERR_A:.0f} м² · парковка {area(PARK):.0f} м² · двор/сад ≈{FREE:.0f} м² (бассейн 8×4, спортплощадка {(sx1 - sx0) * (sy1 - sy0):.0f} м²)</text>',
    f'<text x="20" y="{ly + 46}" font-size="13" fill="#0b5cad" font-family="sans-serif">синие размеры — расстояние от стены дома до забора · '
    f'помещения 1 этажа — по чертежу DP-Module (брутто)</text>',
    f'<text x="20" y="{ly + 68}" font-size="13" fill="#555" font-family="sans-serif">дом в глубине: терраса в {ROAD_GAP:.1f} м от дороги · '
    f'2 этаж: 2 спальни (юг), зона отдыха с балконом над террасой, санузел · 2 авто рядом, ворота 6 м с калиткой в полотне</text>',
]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
       '<rect width="100%" height="100%" fill="#fff"/>', *el, *legend, "</svg>"]
open("plan_dabl.svg", "w", encoding="utf-8").write("\n".join(svg))
print(f"терраса до дороги {ROAD_GAP:.2f} м; участок {area(P):.1f} м², дом {HOUSE_A:.0f} + терраса {TERR_A:.0f} м², двор/сад {FREE:.0f} м²")
