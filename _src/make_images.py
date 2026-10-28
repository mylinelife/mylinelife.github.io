#!/usr/bin/env python3
"""Генератор картинок 1200x630 для карт, рун и линий ладони (превью ссылок и поиск по картинкам).
Запуск: python3 _src/make_images.py (из корня репозитория). Нужен playwright + chromium."""
import os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from data_tarot import TAROT
from data_runes import RUNES
from data_palm import PALM
from data_minor import MINOR, SUITS
from playwright.sync_api import sync_playwright
import build as B

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
F = "file://" + os.path.join(ROOT, "assets/fonts") + "/"
E = html.escape
CSS = f"""
@font-face{{font-family:CG;font-weight:700;src:url({F}cormorant-garamond-cyrillic-700-normal.woff2);unicode-range:U+0400-04FF,U+2116}}
@font-face{{font-family:CG;font-weight:700;src:url({F}cormorant-garamond-latin-700-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F}}
@font-face{{font-family:MR;font-weight:400;src:url({F}manrope-cyrillic-400-normal.woff2);unicode-range:U+0400-04FF,U+2116}}
@font-face{{font-family:MR;font-weight:400;src:url({F}manrope-latin-400-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F}}
@font-face{{font-family:MR;font-weight:700;src:url({F}manrope-cyrillic-700-normal.woff2);unicode-range:U+0400-04FF,U+2116}}
@font-face{{font-family:MR;font-weight:700;src:url({F}manrope-latin-700-normal.woff2);unicode-range:U+0000-00FF,U+2000-206F}}
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;overflow:hidden;font-family:MR,'Inter',sans-serif;color:#efe9ff;
background:radial-gradient(900px 500px at 25% 30%,#2b1f55 0%,#1b1430 55%,#120d1f 100%);position:relative}}
.stars{{position:absolute;inset:0;background-image:radial-gradient(1.5px 1.5px at 8% 14%,#f5dca8aa,transparent),radial-gradient(1.5px 1.5px at 22% 82%,#fff8,transparent),radial-gradient(2px 2px at 61% 9%,#f5dca8aa,transparent),radial-gradient(1.5px 1.5px at 93% 26%,#fff8,transparent),radial-gradient(1.5px 1.5px at 87% 88%,#f5dca8aa,transparent),radial-gradient(1.5px 1.5px at 47% 93%,#fff6,transparent),radial-gradient(1.5px 1.5px at 74% 62%,#fff6,transparent)}}
.frame{{position:absolute;inset:22px;border:2px solid #e8c27a55;border-radius:26px}}
.glyph{{position:absolute;left:70px;top:70px;width:400px;height:490px;border:2px solid #e8c27a;border-radius:200px 200px 28px 28px;display:flex;align-items:center;justify-content:center;
background:linear-gradient(160deg,#2a2050,#1a1230);box-shadow:0 0 70px #9b7bff44 inset;color:#e8c27a;text-align:center}}
.glyph svg{{width:330px;height:430px}}.glyph .g{{font-family:'Noto Sans Runic',CG,serif;font-weight:700;font-size:250px;line-height:1}}
.glyph .n{{font-family:CG,serif;font-weight:700;font-size:210px;line-height:1}}
.glyph .w{{font-family:CG,serif;font-weight:700;font-size:96px;line-height:1.05;padding:0 24px}}
.txt{{position:absolute;left:530px;right:70px;top:90px}}
.eb{{font-size:25px;letter-spacing:.16em;text-transform:uppercase;color:#9b7bff;font-weight:700}}
h1{{font-family:CG,serif;font-weight:700;font-size:{{FS}}px;line-height:1.02;color:#e8c27a;margin:24px 0 22px}}
.kw{{font-size:32px;line-height:1.4;color:#b5abd1}}
.ft{{position:absolute;left:530px;right:70px;bottom:62px;display:flex;justify-content:space-between;align-items:center;font-size:25px;color:#b5abd1}}
.ft b{{color:#f5dca8;font-size:30px}}
"""
def card(kind, big, bigcls, eyebrow, title, kws, accent=None, slug=None):
    PALMHTML = B.palm_svg(slug) if slug else ""
    fs = 104 if len(title) <= 16 else (88 if len(title) <= 22 else 74)
    css = CSS.replace("{FS}", str(fs))
    if accent:
        css += f".glyph{{border-color:{accent}}}.kw{{border-left:6px solid {accent};padding-left:22px}}"
    return f"""<html><head><meta charset=utf-8><style>{css}</style></head><body><div class=stars></div><div class=frame></div>
<div class=glyph>{PALMHTML if bigcls=="pal" else f'<div class={bigcls}>{E(big)}</div>'}</div>
<div class=txt><div class=eb>{E(eyebrow)}</div><h1>{E(title)}</h1><div class=kw>{E(kws)}</div></div>
<div class=ft><b>MyLineLife</b><span>гадание в Telegram · @mylinelife_bot</span></div></body></html>"""

jobs = []
for c in TAROT:
    jobs.append((f"assets/img/taro/{c['slug']}.jpg", card("t", c["num"], "n", "Старший аркан · Таро", c["name"], " · ".join(c["kw"][:4]))))
suit_by = {s["slug"]: s for s in SUITS}
for c in MINOR:
    s = suit_by[c["suit"]]
    num = c["num"]
    bigcls = "n" if len(num) <= 2 else "w"
    jobs.append((f"assets/img/taro/{c['slug']}.jpg", card("t", num, bigcls, f"Младший аркан · {s['name']}", c["name"], " · ".join(c["kw"][:4]))))
for r in RUNES:
    jobs.append((f"assets/img/runy/{r['slug']}.jpg", card("r", r["sym"], "g", "Старший Футарк · руна", f"Руна {r['name']}", f"«{r['meaning']}» · " + " · ".join(r["kw"][:3]))))
jobs.append(("assets/img/runy/odin.jpg", card("r", "◯", "g", "Дополнительная руна", "Пустая руна Одина", "неизвестность · судьба · доверие")))
for p in PALM:
    jobs.append((f"assets/img/hiromantiya/{p['slug']}.jpg", card("p", "", "pal", "Хиромантия", f"{p['name']} на руке", "где находится · что означает · виды", accent=p["color"], slug=p["slug"])))

if __name__ == "__main__":
    only = sys.argv[1:]
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files"])
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        n = 0
        for path, h in jobs:
            if only and not any(o in path for o in only):
                continue
            out = os.path.join(ROOT, path)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            tmp = os.path.join(ROOT, "_src", "_tmp.html")
            open(tmp, "w", encoding="utf-8").write(h)
            pg.goto("file://" + tmp)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            pg.screenshot(path=out, type="jpeg", quality=80)
            n += 1
        b.close()
    if os.path.exists(os.path.join(ROOT, "_src", "_tmp.html")):
        os.remove(os.path.join(ROOT, "_src", "_tmp.html"))
    print("images:", n)
