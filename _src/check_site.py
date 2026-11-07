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
}
# страницы, правленные после 24.10: lastmod в sitemap должен быть новее общего
MODIFIED_AFTER_BASE = list(MIN_WORDS) + ["hiromantiya/liniya-serdca", "hiromantiya/liniya-zhizni", "runy/odin"]


sys.path.insert(0, os.path.dirname(__file__))
from bot_links import check_start  # noqa: E402


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
