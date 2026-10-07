"""Собирает HTML 3D-визуализации: локальную версию для рендера кадров и страницу-артефакт (CDN)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
THREE_VER = "0.160.0"


def importmap(base):
    return json.dumps({"imports": {"three": f"{base}/build/three.module.js",
                                   "three/addons/": f"{base}/examples/jsm/"}})


def build(kind, out_path):
    scene_js = open(os.path.join(HERE, "scene.js"), encoding="utf-8").read()
    data = open(os.path.join(HERE, "scene.json"), encoding="utf-8").read()
    if kind == "pagelocal":                      # страница с интерфейсом, но three.js из node_modules — для проверки
        base = "/node_modules/three"
        page = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
        head, body, tail = "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>", page, ""
    elif kind == "local":
        base = "/node_modules/three"
        head = "<!doctype html><meta charset=utf-8><title>render</title>"
        body = ('<style>html,body{margin:0;height:100%;background:#cfdbe6}#c{display:block;width:100vw;height:100vh}</style>'
                '<canvas id="c"></canvas>')
        tail = ""
    else:
        base = f"https://cdn.jsdelivr.net/npm/three@{THREE_VER}"
        page = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
        head, body, tail = "", page, ""
    html = (head + body +
            f'<script type="importmap">{importmap(base)}</script>'
            f'<script>window.SCENE = {data};</script>'
            f'<script type="module">\n{scene_js}\n</script>' + tail)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("→", out_path, f"{len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    build("local", sys.argv[1])
    if len(sys.argv) > 2:
        build("artifact", sys.argv[2])
    if len(sys.argv) > 3:
        build("pagelocal", sys.argv[3])
