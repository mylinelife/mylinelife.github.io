#!/usr/bin/env python3
"""Проверка собранного сайта: python3 _src/check_site.py (из корня репозитория).
Падает с кодом 1, если есть проблема: битые внутренние ссылки, невалидный JSON-LD,
не 1 H1, повтор заголовков H2, мало текста на целевых страницах, неверный lastmod."""
import glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://mylinelife.ru"
# минимум слов на страницах, которые углубляем (путь -> порог)
MIN_WORDS = {
    **{f"runy/{s}": 850 for s in ("turisaz", "yera", "otala")},
    **{f"taro/{s}": 800 for s in ("troyka-zhezlov", "dvoyka-zhezlov", "desyatka-mechey", "desyatka-zhezlov")},
    "runy/runa-dnya": 700, "taro/karta-dnya": 700, "hiromantiya": 750,
    # пачка 11.11.2026
    **{f"taro/{s}": 850 for s in ("ierofant", "smert", "umerennost", "imperator", "sila")},
    **{f"runy/{s}": 850 for s in ("mannaz", "hagalaz", "dagaz", "nautiz")},
    "hiromantiya/liniya-braka": 750,
    "sovmestimost-po-date-rozhdeniya": 1000,
    # аудит 14.11.2026: ключевые страницы хиромантии и хабы мастей
    "hiromantiya/liniya-golovy": 800, "hiromantiya/liniya-sudby": 800,
    **{f"taro/{x}": 700 for x in ("zhezly", "kubki", "mechi", "pentakli")},
    # 15.11.2026: самые тонкие карты Пентаклей (были ~350 слов)
    **{f"taro/{s}-pentakley": 750 for s in ("troyka", "semerka", "vosmerka", "devyatka", "desyatka", "pazh", "korol")},
    # 17.11.2026: остальные карты Пентаклей
    **{f"taro/{s}-pentakley": 750 for s in ("tuz", "dvoyka", "chetverka", "pyaterka", "shesterka", "rycar", "koroleva")},
}
# страницы, правленные после 24.10: lastmod в sitemap должен быть новее общего
MODIFIED_AFTER_BASE = list(MIN_WORDS) + ["hiromantiya/liniya-serdca", "hiromantiya/liniya-zhizni", "runy/odin"]


sys.path.insert(0, os.path.dirname(__file__))
from bot_links import check_start  # noqa: E402


# страницы хиромантии, где у каждого варианта линии своя схема ладони
VARIANT_SVG = {"hiromantiya/liniya-serdca": 6, "hiromantiya/liniya-zhizni": 6}

# инструменты, на которые должна вести каждая страница (подвал) и контент главной
TOOLS = ["/taro/karta-dnya/", "/runy/runa-dnya/", "/taro/da-ili-net/", "/taro/arkan-po-date-rozhdeniya/", "/sovmestimost-po-date-rozhdeniya/"]


def path_points(d, steps=12):
    """Точки SVG-пути из команд M/L/C (абсолютные координаты), кривые Безье разбиты на отрезки."""
    nums = lambda t: [float(x) for x in re.findall(r"-?[\d.]+", t)]
    pts, cur = [], (0.0, 0.0)
    for cmd, args in re.findall(r"([MLC])([^MLC]*)", d):
        a = nums(args)
        if cmd in "ML":
            for i in range(0, len(a), 2):
                cur = (a[i], a[i + 1]); pts.append(cur)
        else:
            for i in range(0, len(a), 6):
                p0, p1, p2, p3 = cur, (a[i], a[i + 1]), (a[i + 2], a[i + 3]), (a[i + 4], a[i + 5])
                for k in range(1, steps + 1):
                    t = k / steps; u = 1 - t
                    pts.append(tuple(u**3 * p0[j] + 3 * u * u * t * p1[j] + 3 * u * t * t * p2[j] + t**3 * p3[j] for j in (0, 1)))
                cur = p3
    return pts


def inside(pt, poly):
    x, y, res = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            res = not res
    return res


def near_edge(pt, poly, tol=1.5):
    """Точка на контуре с допуском: линии вроде линии сердца по задумке доходят до края ладони."""
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        dx, dy = x2 - x1, y2 - y1
        t = max(0, min(1, ((pt[0] - x1) * dx + (pt[1] - y1) * dy) / (dx * dx + dy * dy or 1)))
        if (pt[0] - x1 - t * dx) ** 2 + (pt[1] - y1 - t * dy) ** 2 <= tol * tol:
            return True
    return False


def palm_lines_outside(h):
    """Линии на схемах ладони, которые выходят за контур руки (первый path в группе — контур)."""
    bad = []
    for svg in re.findall(r'<svg class="(?:palm-svg|variant-svg)[^"]*".*?</svg>', h, re.S):
        ds = re.findall(r'<path d="([^"]+)"', svg)
        if len(ds) < 2:
            continue
        hand = path_points(ds[0])
        bad += [d[:30] for d in ds[1:] if not all(inside(pt, hand) or near_edge(pt, hand) for pt in path_points(d))]
    return bad


def text_of(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"<[^>]+>", " ", h)


def pages():
    for p in glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True):
        if "/_src/" in p or "/assets/" in p:
            continue
        yield os.path.relpath(os.path.dirname(p), ROOT).replace("\\", "/").replace(".", "") or "", p


def exists(path):
    path = path.split("#")[0].split("?")[0]
    if path.startswith(SITE):
        path = path[len(SITE):]
    if not path.startswith("/"):
        return True
    fs = os.path.join(ROOT, path.lstrip("/"))
    return os.path.isfile(fs) or os.path.isfile(os.path.join(fs, "index.html"))


def main():
    errs, titles = [], {}
    for rel, p in pages():
        h = open(p, encoding="utf8").read()
        name = rel or "/"
        if len(re.findall(r"<h1[ >]", h)) != 1:
            errs.append(f"{name}: H1 не один")
        t = re.search(r"<title>(.*?)</title>", h, re.S)
        if not t or t.group(1) in titles:
            errs.append(f"{name}: title пустой или повторяется ({titles.get(t.group(1)) if t else ''})")
        elif t:
            titles[t.group(1)] = name
        if t and len(t.group(1)) > 70:
            errs.append(f"{name}: title {len(t.group(1))} симв. (макс. 70)")
        d = re.search(r'<meta name="description" content="([^"]*)"', h)
        if not d or not 70 <= len(d.group(1)) <= 160:
            errs.append(f"{name}: description {len(d.group(1)) if d else 0} симв. (нужно 70–160)")
        indexable = "noindex" not in (re.search(r'<meta name="robots" content="([^"]*)"', h) or [0, ""])[1]
        if indexable and "max-image-preview:large" not in h:
            errs.append(f"{name}: нет max-image-preview:large в meta robots")
        mainh = (re.search(r"<main[^>]*>(.*?)</main>", h, re.S) or [0, h])[1]
        lv = [int(x) for x in re.findall(r"<h([1-6])[ >]", mainh)]
        if any(b - a > 1 for a, b in zip(lv, lv[1:])):
            errs.append(f"{name}: пропуск уровня заголовков {lv[:6]}")
        for tool in TOOLS:
            if indexable and f'href="{tool}"' not in h and name.strip("/") != tool.strip("/"):
                errs.append(f"{name}: нет ссылки на инструмент {tool}")
        if name == "/":
            for tool in TOOLS:
                if f'href="{tool}"' not in mainh:
                    errs.append(f"/: в контенте главной нет ссылки на {tool}")
        h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", h, re.S)
        for d in {x for x in h2 if h2.count(x) > 1}:
            errs.append(f"{name}: повтор H2 «{d}»")
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(m)
            except ValueError as e:
                errs.append(f"{name}: битый JSON-LD ({e})")
        nojs = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
        for href in set(re.findall(r'href="([^"]+)"', nojs)):
            if (href.startswith("/") or href.startswith(SITE)) and not exists(href):
                errs.append(f"{name}: битая ссылка {href}")
        for pl in set(re.findall(r"t\.me/mylinelife_bot\?start=([^\"'& <]+)", h)):
            e = check_start(pl)
            if e:
                errs.append(f"{name}: ссылка на бота start={pl}: {e}")
        if rel in VARIANT_SVG:
            n = len(re.findall(r'<svg class="variant-svg"[^>]*role="img" aria-label="[^"]{10,}"', h))
            if n != VARIANT_SVG[rel]:
                errs.append(f"{name}: схем вариантов {n}, нужно {VARIANT_SVG[rel]}")
        for d in set(palm_lines_outside(h)):
            errs.append(f"{name}: линия на схеме ладони выходит за контур ({d}…)")
        need = MIN_WORDS.get(rel)
        if need:
            n = len(text_of(h).split())
            if n < need:
                errs.append(f"{name}: {n} слов, нужно не меньше {need}")
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf8").read()
    base = re.search(r"<lastmod>(.*?)</lastmod>", sm).group(1)
    for rel in MODIFIED_AFTER_BASE:
        m = re.search(rf"<loc>{SITE}/{rel}/</loc><lastmod>(.*?)</lastmod>", sm)
        if not m or m.group(1) <= "2026-10-24":
            errs.append(f"{rel}: lastmod в sitemap не обновлён ({m.group(1) if m else 'нет'})")
    print("\n".join(errs) or "OK")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
