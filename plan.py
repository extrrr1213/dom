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
for w10 in range(70, 151, 5):            # ширина дома вдоль дороги 7..15 м
    w = w10 / 10
    h = round(HOUSE_AREA / w, 2)
    if not 7 <= h <= 15:
        continue
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

# ---------- SVG ----------
xs = [p[0] for p in P]; ys = [p[1] for p in P]
minx, maxx, miny, maxy = min(xs) - 4, max(xs) + 8, min(ys) - 4, max(ys) + 4
SC = 22


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


W, H = (maxx - minx) * SC, (maxy - miny) * SC + 70
el = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
    f'<rect width="100%" height="100%" fill="#fff"/>',
    poly_svg(P, fill="#9caf5a", stroke="#3d4a1c", stroke_width=2),
    poly_svg(BUILD, fill="none", stroke="#c0392b", stroke_width=1.5, stroke_dasharray="6 4"),
    poly_svg(PARK, fill="#bdbdbd", stroke="#555", stroke_width=1.5),
    poly_svg(HOUSE, fill="#e8d3a9", stroke="#6b4f1d", stroke_width=2.5),
    text(centroid(HOUSE), f"ДОМ {hw:g}×{hh:g} м", 15, font_weight="bold"),
    text((centroid(HOUSE)[0], centroid(HOUSE)[1] - 1.0), f"≈{hw*hh:.0f} м²", 13),
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
garden = centroid([A, D, HOUSE[3], HOUSE[0]])
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
