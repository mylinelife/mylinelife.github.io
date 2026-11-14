#!/usr/bin/env python3
"""Полный SEO-аудит собранного сайта: python3 _src/audit.py (из корня репозитория).
Только отчёт, ничего не меняет. Разделы: мета, контент и схожесть, перелинковка, картинки, разметка, sitemap."""
import collections, glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://mylinelife.ru"


def load():
    pages = {}
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if rel.startswith(("_src/", "assets/", "yandex_", "google", "zen_")) or "/node_modules/" in rel:
            continue
        url = "/" + rel[:-len("index.html")] if rel.endswith("index.html") else "/" + rel
        pages[url] = open(p, encoding="utf8").read()
    return pages


def strip(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def main_part(h):
    m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S)
    return m.group(1) if m else h


def shingles(text, n=5):
    w = re.findall(r"[а-яёa-z0-9]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def meta(h, name):
    m = re.search(rf'<meta name="{name}" content="([^"]*)"', h)
    return m.group(1) if m else None


def main():
    pages = load()
    out = []
    P = lambda *a: out.append(" ".join(str(x) for x in a))
    idx = {u: h for u, h in pages.items() if "noindex" not in (meta(h, "robots") or "")}
    P(f"# Страниц: {len(pages)}, индексируемых: {len(idx)}")

    # --- 1. Мета
    P("\n## 1. Title и description")
    tl, dl, bad = [], [], []
    seen_d = collections.defaultdict(list)
    for u, h in idx.items():
        t = (re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1]
        d = meta(h, "description") or ""
        tl.append(len(t)); dl.append(len(d)); seen_d[d].append(u)
        if len(t) > 70: bad.append(f"title {len(t)} симв.: {u}")
        if len(t) < 25: bad.append(f"title короткий {len(t)}: {u}")
        if not d: bad.append(f"нет description: {u}")
        elif len(d) > 170: bad.append(f"description {len(d)} симв.: {u}")
        elif len(d) < 70: bad.append(f"description короткий {len(d)}: {u}")
        for tag in ("og:title", "og:description", "og:image", "og:url"):
            if f'property="{tag}"' not in h: bad.append(f"нет {tag}: {u}")
        if 'rel="canonical"' not in h: bad.append(f"нет canonical: {u}")
        elif f'<link rel="canonical" href="{SITE}{u}"' not in h: bad.append(f"canonical не на себя: {u}")
        if not re.search(r'<html[^>]*lang="ru"', h): bad.append(f"нет lang=ru: {u}")
        if 'name="viewport"' not in h: bad.append(f"нет viewport: {u}")
    for d, us in seen_d.items():
        if d and len(us) > 1: bad.append(f"дубль description ({len(us)}): {us[:3]}")
    P(f"title: мин {min(tl)}, макс {max(tl)}; >60 симв.: {sum(1 for x in tl if x > 60)}; >70: {sum(1 for x in tl if x > 70)}")
    P(f"description: мин {min(dl)}, макс {max(dl)}; >160: {sum(1 for x in dl if x > 160)}")
    cnt = collections.Counter(re.sub(r"[\d]+ симв\.|: /.*|\(\d+\).*", "", b) for b in bad)
    for k, v in cnt.most_common(): P(f"  {v:3d} × {k}")
    for b in bad[:12]: P("   ·", b)

    # --- 2. Контент
    P("\n## 2. Контент: объём и схожесть")
    words, sh = {}, {}
    for u, h in idx.items():
        t = strip(main_part(h)); words[u] = len(t.split()); sh[u] = shingles(t)
    thin = sorted((n, u) for u, n in words.items() if n < 500)
    P(f"слов в <main>: медиана {sorted(words.values())[len(words)//2]}, <500: {len(thin)}, <700: {sum(1 for n in words.values() if n < 700)}")
    for n, u in thin[:15]: P(f"   · {n} {u}")
    groups = {"младшие арканы": [u for u in idx if re.search(r"/taro/(tuz|dvoyka|troyka|chetverka|pyaterka|shesterka|semerka|vosmerka|devyatka|desyatka|pazh|rycar|koroleva|korol)-", u)],
              "руны": [u for u in idx if re.fullmatch(r"/runy/[a-z]+/", u) and "runa-dnya" not in u],
              "старшие арканы": []}
    rest = [u for u in idx if re.fullmatch(r"/taro/[a-z-]+/", u) and u not in groups["младшие арканы"]]
    groups["старшие арканы"] = [u for u in rest if not re.search(r"zhezly|kubki|mechi|pentakli|karta-dnya|da-ili-net|arkan-po", u)]
    for g, us in groups.items():
        if len(us) < 2: continue
        common = set.intersection(*[sh[u] for u in us])
        # шаблонная доля: шинглы, встречающиеся более чем на половине страниц группы
        c = collections.Counter(s for u in us for s in sh[u])
        tpl = {s for s, k in c.items() if k > len(us) / 2}
        share = sorted(len(sh[u] & tpl) / max(1, len(sh[u])) for u in us)
        uniq = sorted((len([w for w in sh[u] if c[w] == 1]) , u) for u in us)
        P(f"{g}: {len(us)} стр., шаблонного текста: медиана {share[len(share)//2]:.0%}, макс {share[-1]:.0%}; слов: {min(words[u] for u in us)}–{max(words[u] for u in us)}")
        P(f"   меньше всего уникального: " + ", ".join(f"{u.split('/')[-2]}({n})" for n, u in uniq[:5]))
    # попарные почти-дубли
    us = list(idx)
    dups = []
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            a, b = sh[us[i]], sh[us[j]]
            if not a or not b: continue
            jac = len(a & b) / len(a | b)
            if jac > 0.5: dups.append((jac, us[i], us[j]))
    P(f"пар страниц со схожестью > 50%: {len(dups)}")
    for jac, a, b in sorted(dups, reverse=True)[:8]: P(f"   · {jac:.0%} {a} ~ {b}")

    # --- 3. Перелинковка
    P("\n## 3. Перелинковка")
    inl = collections.defaultdict(set); outl = {}
    for u, h in pages.items():
        body = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
        hs = set()
        for href in re.findall(r'<a [^>]*href="([^"#?]+)', body):
            if href.startswith(SITE): href = href[len(SITE):]
            if href.startswith("/") and not href.startswith("/assets"):
                hs.add(href)
        outl[u] = hs
        for x in hs:
            if x != u: inl[x].add(u)
    # входящие из контента (без шапки/подвала): ссылки внутри <main>
    inl_main = collections.defaultdict(set)
    for u, h in pages.items():
        m = re.sub(r"<script.*?</script>", " ", main_part(h), flags=re.S)
        m = re.sub(r'<nav class="crumbs".*?</nav>', " ", m, flags=re.S)
        for href in re.findall(r'<a [^>]*href="(/[^"#?]*)', m):
            if href != u: inl_main[href].add(u)
    orphans = [u for u in idx if not inl[u] and u != "/"]
    weak = sorted((len(inl_main[u]), u) for u in idx if u != "/")
    P(f"сирот (нет входящих ссылок): {len(orphans)} {orphans[:5]}")
    P(f"входящих из текста страниц: мин {weak[0][0]}, медиана {weak[len(weak)//2][0]}; страниц с ≤2: {sum(1 for n, _ in weak if n <= 2)}")
    for n, u in weak[:12]: P(f"   · {n} {u}")
    # глубина кликов от главной
    depth = {"/": 0}; q = ["/"]
    while q:
        u = q.pop(0)
        for x in outl.get(u, ()):
            if x in pages and x not in depth: depth[x] = depth[u] + 1; q.append(x)
    dc = collections.Counter(depth.get(u, 99) for u in idx)
    P(f"глубина от главной: {dict(sorted(dc.items()))}")
    ext = collections.Counter()
    for u, h in idx.items():
        for a in re.findall(r'<a [^>]*href="https?://[^"]+"[^>]*>', h):
            dom = re.search(r'href="https?://([^/"]+)', a).group(1)
            if "mylinelife.ru" in dom: continue
            ext[(dom, "nofollow" in a, "noopener" in a)] += 1
    P("внешние ссылки (домен, nofollow, noopener):", dict(ext.most_common(8)))

    # --- 4. Картинки
    P("\n## 4. Картинки")
    noalt = nodim = nolazy = total = 0; big = []
    imgs = set()
    for u, h in idx.items():
        for im in re.findall(r"<img[^>]*>", h):
            if "mc.yandex.ru" in im:
                continue
            total += 1
            if not re.search(r'alt="[^"]+"', im): noalt += 1
            if "width=" not in im or "height=" not in im: nodim += 1
            if 'loading="lazy"' not in im and "fetchpriority" not in im: nolazy += 1
            s = re.search(r'src="(/[^"]+)"', im)
            if s: imgs.add(s.group(1))
    for s in imgs:
        f = os.path.join(ROOT, s.lstrip("/"))
        if not os.path.exists(f): big.append(("НЕТ ФАЙЛА", s))
        elif os.path.getsize(f) > 150_000: big.append((os.path.getsize(f) // 1024, s))
    P(f"всего <img>: {total}; без alt: {noalt}; без width/height: {nodim}; без lazy/priority: {nolazy}; файлов: {len(imgs)}; >150 КБ или нет файла: {big[:6]}")
    fmt = collections.Counter(os.path.splitext(s)[1] for s in imgs)
    P("форматы:", dict(fmt))
    pg_noimg = [u for u, h in idx.items() if "<img" not in main_part(h)]
    P(f"страниц без картинок в контенте: {len(pg_noimg)}", pg_noimg[:8])

    # --- 5. Разметка
    P("\n## 5. Структурированные данные и заголовки")
    types = collections.Counter(); nold = []; hbad = []
    for u, h in idx.items():
        ts = set()
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            d = json.loads(m)
            for x in d.get("@graph", [d]):
                t = x.get("@type"); ts.update(t if isinstance(t, list) else [t])
                if t == "Article":
                    for k in ("headline", "datePublished", "dateModified", "author", "publisher", "image", "mainEntityOfPage"):
                        if k not in x: hbad.append(f"Article без {k}: {u}")
                    if len(x.get("headline", "")) > 110: hbad.append(f"headline > 110: {u}")
        types.update(ts)
        if not ts: nold.append(u)
        lv = [int(x) for x in re.findall(r"<h([1-6])[ >]", main_part(h))]
        for a, b in zip(lv, lv[1:]):
            if b - a > 1: hbad.append(f"скачок заголовков h{a}→h{b}: {u}"); break
    P("типы:", dict(types.most_common()))
    P(f"без JSON-LD: {nold}")
    c = collections.Counter(re.sub(r": /.*", "", x) for x in hbad)
    for k, v in c.most_common(): P(f"  {v:3d} × {k}")

    # --- 6. Sitemap и служебное
    P("\n## 6. Sitemap, robots, служебное")
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf8").read()
    locs = {x[len(SITE):] for x in re.findall(r"<loc>([^<]+)</loc>", sm)}
    P(f"в sitemap: {len(locs)}; индексируемых нет в sitemap: {sorted(set(idx) - locs)[:6]}; в sitemap лишнее: {sorted(locs - set(idx))[:6]}")
    P("robots.txt:", open(os.path.join(ROOT, "robots.txt")).read().strip().replace("\n", " | "))
    for f in ("favicon.ico", "apple-touch-icon.png", "manifest.webmanifest", "site.webmanifest", "404.html", "llms.txt", "CNAME", ".nojekyll"):
        P(f"  {f}: {'есть' if os.path.exists(os.path.join(ROOT, f)) else 'НЕТ'}")
    h = pages["/"]
    P("иконки в <head>:", re.findall(r'<link rel="(?:icon|apple-touch-icon|manifest)"[^>]*>', h))
    P("размер HTML: медиана", sorted(len(x) for x in idx.values())[len(idx)//2] // 1024, "КБ, макс", max(len(x) for x in idx.values()) // 1024, "КБ")
    print("\n".join(out))


if __name__ == "__main__":
    main()
