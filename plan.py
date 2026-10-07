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

best = None
# DP-Module «Модерн 105»: 14 × 7.5 м, 6 модулей 7 × 2.5 м
HOUSE_L, HOUSE_W = 14.0, 7.5
for w, h in [(HOUSE_W, HOUSE_L), (HOUSE_L, HOUSE_W)]:  # (вдоль дороги, вглубь участка)
    for si in range(0, 200):
        s = si * 0.1
        for ti in range(30, 250):
            t = ti * 0.1
            # не пересекаться с парковкой (зазор 1 м)
            if not (s >= park_s + PARK_W + 1 or t >= PARK_D + 1):
                continue
            R = rect(s, t, w, h)
            if all(inside(BUILD, c) for c in R):
                score = (t, abs(w - h))  # ближе к дороге => больше сада сзади, форма поквадратнее
                if best is None or score < best[0]:
                    best = (score, s, t, w, h)
                break

_, hs, ht, hw, hh = best
HOUSE = rect(hs, ht, hw, hh)


def local(X, Y):
    """Локальные координаты дома: X — вдоль длинной стороны (0 = дальний от дороги торец), Y — поперёк."""
    if hh > hw:  # длинная сторона вглубь участка
        return to_xy(hs + Y, ht + (HOUSE_L - X))
    return to_xy(hs + X, ht + Y)


def lrect(x0, y0, x1, y1):
    return [local(x0, y0), local(x1, y0), local(x1, y1), local(x0, y1)]


# Реконструкция планировки «Модерн 105» (комнаты из описания DP-Module, размеры ориентировочные)
ROOMS = [
    ("Спальня 1", 0.0, 3.75, 3.8, 7.5, "#dfe9f5"),
    ("Спальня 2", 0.0, 0.0, 3.8, 3.75, "#dfe9f5"),
    ("Детская", 3.8, 4.5, 7.0, 7.5, "#f6e0ea"),
    ("Коридор", 3.8, 2.8, 7.0, 4.5, "#eeeeee"),
    ("Санузел", 3.8, 0.0, 7.0, 2.8, "#d6f0ee"),
    ("Прихожая", 7.0, 0.0, 9.5, 3.0, "#eeeeee"),
    ("Кухня-столовая", 9.5, 0.0, 14.0, 3.0, "#fde7c4"),
    ("Гостиная", 7.0, 3.0, 14.0, 7.5, "#fbf1d6"),
]
TERRACE = lrect(9.0, 7.5, 14.0, 10.0)  # выход из гостиной, внутри пятна застройки

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
for name, x0, y0, x1, y1, col in ROOMS:
    pts = lrect(x0, y0, x1, y1)
    ROOMS_SVG.append(poly_svg(pts, fill=col, stroke="#6b4f1d", stroke_width=1.2))
for name, x0, y0, x1, y1, col in ROOMS:
    c = centroid(lrect(x0, y0, x1, y1))
    a = abs((x1 - x0) * (y1 - y0))
    fs = 11 if a > 12 else 9
    ROOMS_SVG.append(text(c, name, fs, font_weight="bold"))
    ROOMS_SVG.append(text((c[0], c[1] - 0.6), f"{a:.1f} м²", fs - 1))
# входная дверь
d = centroid(lrect(7.6, -0.2, 8.9, 0.2))
dx, dy = sv(d)
ROOMS_SVG.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="5" fill="#c0392b"/>')
ROOMS_SVG.append(text((d[0], d[1] - 1.0), "вход", 10, fill="#c0392b", font_weight="bold"))

W, H = (maxx - minx) * SC, (maxy - miny) * SC + 70
el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" fill="#fff"/>',
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    poly_svg(TERRACE, fill="#c9a36b", stroke="#6b4f1d", stroke_width=1.5),
    text(centroid(TERRACE), "терраса", 10),
    poly_svg(HOUSE, fill="#f3e6c8", stroke="#6b4f1d", stroke_width=3),
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
garden = ((A[0] + D[0]) / 2 + 5, (A[1] + D[1]) / 2 - 4)
el.append(text(garden, "сад / двор", 15, fill="#2f3b12", font_style="italic"))
y0 = (maxy - miny) * SC + 25
el.append(f'<rect x="20" y="{y0-12}" width="28" height="0" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<line x1="20" y1="{y0-5}" x2="50" y2="{y0-5}" stroke="#c0392b" stroke-dasharray="6 4" stroke-width="1.5"/>')
el.append(f'<text x="58" y="{y0}" font-size="13" font-family="sans-serif">граница пятна застройки: отступ {SETBACK:g} м от всех границ</text>')
el.append(f'<text x="20" y="{y0+24}" font-size="13" font-family="sans-serif">участок ≈{area(P):.0f} м² · дом {hw*hh:.0f} м² · застройка {hw*hh/area(P)*100:.0f}% · масштаб: 1 м = {SC}px</text>')
el.append("</svg>")
open("plan.svg", "w").write("\n".join(el))

print("угол при A:", round(math.degrees(best_a), 1))
print("участок:", [tuple(round(c, 2) for c in p) for p in P], "площадь", round(area(P), 1))
print("пятно застройки:", round(area(BUILD), 1), "м²")
print(f"дом {hw}×{hh} = {hw*hh:.1f} м², отступ от дороги {ht:.1f} м, s={hs:.1f}")
print("парковка s=", round(park_s, 1))
