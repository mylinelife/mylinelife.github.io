#!/usr/bin/env python3
"""Сборщик сайта LineLife. Запуск: python3 _src/build.py (из корня репозитория).
Генерирует HTML-страницы, sitemap.xml, robots.txt, 404.html и общий CSS."""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from data_tarot import TAROT
from data_runes import RUNES
from data_palm import PALM
from data_minor import MINOR, SUITS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://mylinelife.github.io"
BOT = "https://t.me/mylinelife_bot"
CHANNEL = "https://t.me/linelife_daily"
VK = "https://vk.ru/linelife_daily"
TODAY = "2026-10-18"
CSS_V = "10"
E = html.escape
pages = []  # (path, priority, changefreq)


PINS = {
    "/hiromantiya/": ("pin-linii-na-ruke", "Линии на руке и их значение — схема ладони: линия жизни, сердца, головы и судьбы"),
    "/hiromantiya/liniya-zhizni/": ("pin-liniya-zhizni", "Линия жизни на руке — схема и значение в хиромантии"),
    "/hiromantiya/liniya-serdca/": ("pin-liniya-serdca", "Линия сердца на руке — схема и значение в хиромантии"),
    "/hiromantiya/liniya-golovy/": ("pin-liniya-golovy", "Линия головы на руке — схема и значение в хиромантии"),
    "/hiromantiya/liniya-sudby/": ("pin-liniya-sudby", "Линия судьбы на руке — схема и значение в хиромантии"),
    "/taro/": ("pin-znachenie-kart-taro", "Значение карт Таро Уэйта — шпаргалка: любовь, работа, совет, да или нет"),
    "/taro/vlyublennye/": ("pin-taro-vlyublennye", "Карта Таро Влюблённые — значение в любви и отношениях"),
    "/runy/": ("pin-vse-runy", "Все руны Старшего Футарка и их значение — таблица 24 рун"),
}


def pin_block(url):
    if url not in PINS:
        return ""
    name, alt = PINS[url]
    return f"""<section class="pin-block card">
  <img src="/assets/pins/{name}.jpg" width="500" height="750" loading="lazy" alt="{E(alt)}" data-pin-description="{E(alt)} — LineLife">
  <div><h2>Шпаргалка</h2><p>Сохрани картинку себе в Pinterest или на телефон, чтобы она была под рукой.</p>
  <p><a class="btn btn-ghost btn-sm" href="https://www.pinterest.com/pin/create/button/?url={SITE}{url}&amp;media={SITE}/assets/pins/{name}.jpg&amp;description={E(alt)}" target="_blank" rel="noopener">Сохранить в Pinterest</a></p></div>
</section>"""


def write(path, content):
    full = os.path.join(ROOT, path.lstrip("/"))
    if full.endswith("/"):
        full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def bot(src):
    return f"{BOT}?start=src_{src}"


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def faq_ld(qa):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}


def article_ld(title, desc, url):
    return {"@type": "Article", "headline": title, "description": desc, "inLanguage": "ru",
            "datePublished": TODAY, "dateModified": TODAY, "mainEntityOfPage": SITE + url,
            "image": SITE + "/assets/og.png",
            "author": {"@type": "Organization", "name": "LineLife", "url": SITE + "/"},
            "publisher": {"@type": "Organization", "name": "LineLife",
                          "logo": {"@type": "ImageObject", "url": SITE + "/assets/icon-512.png"}}}


def page(url, title, desc, body, graph=(), og_type="article", priority="0.7", freq="monthly", robots="index, follow", sitemap=True):
    canon = SITE + url
    gr = {"@context": "https://schema.org", "@graph": list(graph)} if graph else None
    out = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="p:domain_verify" content="6ca9b9bec06086458cbe8ece2f7eb6d4">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="LineLife">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#120d1f">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Manrope:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={CSS_V}">
{ld(gr) if gr else ""}
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="logo" href="/">Line<span>Life</span></a>
  <nav class="nav" aria-label="Разделы">
    <a href="/taro/">Таро</a><a href="/runy/">Руны</a><a href="/hiromantiya/">Хиромантия</a>
  </nav>
  <a class="btn btn-gold btn-sm hide-sm" href="{bot('site_header')}">Открыть бота</a>
</header>
<main>
{body}
{pin_block(url)}
</main>
<footer>
  <nav class="foot-nav" aria-label="Карта сайта">
    <div><b>Таро</b><a href="/taro/">Значения карт</a><a href="/taro/{TAROT[0]['slug']}/">Шут</a><a href="/taro/smert/">Смерть</a><a href="/taro/zhezly/">Масть Жезлов</a><a href="/taro/kubki/">Масть Кубков</a><a href="/taro/mechi/">Масть Мечей</a><a href="/taro/pentakli/">Масть Пентаклей</a></div>
    <div><b>Руны</b><a href="/runy/">Значения рун</a><a href="/runy/fehu/">Феху</a><a href="/runy/algiz/">Альгиз</a><a href="/runy/gebo/">Гебо</a><a href="/runy/odin/">Руна Одина</a></div>
    <div><b>Хиромантия</b><a href="/hiromantiya/">Линии на руке</a>{''.join(f'<a href="/hiromantiya/{p["slug"]}/">{p["name"]}</a>' for p in PALM)}</div>
    <div><b>LineLife</b><a href="{bot('site_footer')}">Бот в Telegram</a><a href="{CHANNEL}">Канал с картой дня</a><a href="{VK}">Группа ВКонтакте</a><a href="/o-proekte/">О проекте</a><a href="/privacy.html">Политика конфиденциальности</a></div>
  </nav>
  <p class="disc"><span class="age">18+</span> LineLife — развлекательный сервис. Материалы сайта и бота не являются предсказанием, медицинской, психологической, юридической или финансовой консультацией.</p>
  <p class="disc">© 2026 LineLife</p>
</footer>
</div>
</body>
</html>
"""
    write(url if url.endswith((".html", "/")) else url, out)
    if sitemap:
        pages.append((url, priority, freq))


def breadcrumbs(items):
    parts = []
    for i, (n, u) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{E(n)}</span>')
        else:
            parts.append(f'<a href="{u}">{E(n)}</a>')
    return '<nav class="crumbs" aria-label="Навигация">' + ' <span class="sep">/</span> '.join(parts) + '</nav>'


def cta(title, text, src, label="🔮 Открыть LineLife в Telegram"):
    return f"""<aside class="final">
  <h2>{title}</h2>
  <p>{text}</p>
  <a class="btn btn-gold" href="{bot(src)}">{label}</a>
  <p class="note">Карта дня и руна дня — бесплатно. 18+</p>
</aside>"""


def faq_html(qa):
    return '<section class="faq"><h2>Частые вопросы</h2>' + ''.join(
        f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in qa) + '</section>'


PALM_HAND = 'M73.88 190.96 C68.18 182.41 61.34 169.3 56.78 156.76 C51.08 142.51 43.1 128.26 40.82 115.72 C39.68 105.46 51.08 103.18 54.5 111.16 C57.92 121.42 63.62 129.4 68.18 131.68 C68.18 116.86 68.18 88.36 68.18 66.7 C68.18 55.3 80.72 55.3 80.72 66.7 L80.72 105.46 C81.29 108.31 83 108.31 83.57 105.46 L83.57 56.44 C83.57 45.04 96.11 45.04 96.11 56.44 L96.11 104.32 C96.68 107.17 98.39 107.17 98.96 104.32 L98.96 63.28 C98.96 52.45 111.5 52.45 111.5 63.28 L111.5 108.88 C112.07 111.73 113.78 111.73 114.35 108.88 L114.35 82.66 C114.35 73.54 124.61 73.54 124.61 82.66 C125.75 111.16 126.32 142.51 121.76 162.46 C118.34 176.71 113.78 185.26 111.5 190.96'
PALM_SVG_PATHS = {
    "liniya-zhizni": '<path d="M86.42 141.94 C89.84 159.04 84.14 175 64.76 182.98" />',
    "liniya-golovy": '<path d="M68.18 132.82 C83 132.82 98.96 137.95 111.5 152.2" />',
    "liniya-serdca": '<path d="M69.89 123.7 C85.28 122.56 108.08 123.7 125.18 130.54" />',
    "liniya-sudby": '<path d="M100.67 189.82 C102.38 168.16 104.09 142.51 106.37 115.72" />',
}
PALM_COLORS = {p["slug"]: p["color"] for p in PALM}


def palm_svg(highlight=None, size_class="palm-svg"):
    lines = []
    for slug, path in PALM_SVG_PATHS.items():
        on = highlight is None or slug == highlight
        w = "3.4" if (highlight and on) else "2"
        op = "1" if on else ".25"
        lines.append(path.replace("/>", f'stroke="{PALM_COLORS[slug]}" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>'))
    return f"""<svg class="{size_class}" viewBox="0 0 200 200" fill="none" role="img" aria-label="Схема ладони с основными линиями">
<circle cx="100" cy="100" r="92" stroke="#3a2f5c"/>
<circle cx="100" cy="100" r="80" stroke="#e8c27a33" stroke-dasharray="2 6"/>
<g transform="translate(100 102) scale(1.18) translate(-83 -118)"><path d="{PALM_HAND}" stroke="#efe9ff" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/>{"".join(lines)}</g>

</svg>"""


# ---------------- ТАРО ----------------
def card_page(c, deck, i, eyebrow, crumbs_mid, others_title, others, hub_url, hub_label, sigil_top):
    n = len(deck)
    url = f"/taro/{c['slug']}/"
    title = f"{c['name']} — значение карты Таро, в любви и перевёрнутая | LineLife"
    desc = f"Значение карты {c['name']} в Таро: {', '.join(c['kw'][:3])}. Прямое и перевёрнутое положение, любовь, работа, совет и ответ «да или нет»."
    h1 = f"Карта Таро {c['name']}: значение и толкование"
    prev = deck[(i - 1) % n]; nxt = deck[(i + 1) % n]
    qa = [(f"Что означает карта {c['name']} в Таро?", c["general"]),
          (f"Что значит перевёрнутая карта {c['name']}?", c["reversed"]),
          (f"Что означает {c['name']} в любви и отношениях?", c["love"]),
          (f"{c['name']}: да или нет?", f"В раскладе «да или нет» карта {c['name']} обычно трактуется как «{c['yesno']}».")]
    cr = [("Главная", "/"), ("Значения карт Таро", "/taro/")] + crumbs_mid + [(c["name"], url)]
    chips = ''.join(f'<a class="chip" href="/taro/{t["slug"]}/">{t["name"]}</a>' for t in others if t is not c)
    body = f"""{breadcrumbs(cr)}
<article class="entry">
  <header class="entry-head">
    <div class="sigil tarot-sigil" aria-hidden="true"><span class="num{" word" if len(sigil_top)>4 else ""}">{sigil_top}</span><span class="nm">{c['name']}</span></div>
    <div>
      <div class="eyebrow">{eyebrow}</div>
      <h1>{h1}</h1>
      <p class="lead">{c['general']}</p>
      <ul class="kw">{''.join(f'<li>{k}</li>' for k in c['kw'])}</ul>
    </div>
  </header>
  <div class="entry-grid">
    <section class="card"><h2>Перевёрнутая карта {c['name']}</h2><p>{c['reversed']}</p></section>
    <section class="card"><h2>{c['name']} в любви и отношениях</h2><p>{c['love']}</p></section>
    <section class="card"><h2>{c['name']} в работе и финансах</h2><p>{c['work']}</p></section>
    <section class="card"><h2>Совет карты</h2><p>{c['advice']}</p></section>
    <section class="card yes"><h2>{c['name']}: да или нет</h2><p class="big">{c['yesno']}</p><p>Ответ зависит от вопроса и соседних карт в раскладе.</p></section>
  </div>
  <p class="muted">Значение карты в конкретном раскладе зависит от вопроса и позиции. Описание приведено по традиции колоды Райдера — Уэйта и носит развлекательный характер.</p>
</article>
{cta(f"Выпадет ли тебе {c['name']}?", "Задай свой вопрос в боте LineLife и получи расклад Таро прямо в Telegram.", f"seo_taro_{c['slug']}", "🎴 Сделать расклад")}
<nav class="pager" aria-label="Соседние карты">
  <a href="/taro/{prev['slug']}/">← {prev['name']}</a>
  <a href="{hub_url}">{hub_label}</a>
  <a href="/taro/{nxt['slug']}/">{nxt['name']} →</a>
</nav>
{faq_html(qa)}
<section><h2>{others_title}</h2><div class="chips">{chips}<a class="chip more" href="/taro/">Все 78 карт →</a></div></section>"""
    page(url, title, desc, body, [article_ld(h1, desc, url), crumbs_ld(cr), faq_ld(qa)], priority="0.8")


def tile(c, top):
    return f'<a class="card tile" href="/taro/{c["slug"]}/"><span class="tnum">{top}</span><h3>{c["name"]}</h3><p>{", ".join(c["kw"][:3])}</p></a>'


def tarot_pages():
    for i, c in enumerate(TAROT):
        card_page(c, TAROT, i, f"Старший аркан {c['num']}", [], "Другие старшие арканы", TAROT, "/taro/", "Все карты", c["num"])
    for s in SUITS:
        deck = [m for m in MINOR if m["suit"] == s["slug"]]
        hub = f"/taro/{s['slug']}/"
        for i, c in enumerate(deck):
            card_page(c, deck, i, f"Младший аркан · масть {s['gen']} · {s['element']}", [(s["name"], hub)],
                      f"Другие карты масти {s['gen']}", deck, hub, s["name"], {"Паж":"✦","Рыцарь":"♞","Королева":"♛","Король":"♚"}.get(c["num"], c["num"]))
        # хаб масти
        cr = [("Главная", "/"), ("Значения карт Таро", "/taro/"), (s["name"], hub)]
        qa = [(f"Что означает масть {s['gen']} в Таро?", s["intro"]),
              (f"Сколько карт в масти {s['gen']}?", f"14 карт: от Туза до Десятки и четыре придворные карты — Паж, Рыцарь, Королева и Король {s['gen']}."),
              (f"Какой стихии соответствует масть {s['gen']}?", f"Стихия масти — {s['element'].lower()}. Её темы: {s['theme']}.")]
        others = ''.join(f'<a class="chip" href="/taro/{o["slug"]}/">{o["name"]}</a>' for o in SUITS if o is not s)
        body = f"""{breadcrumbs(cr)}
<section class="hub-head">
  <div class="eyebrow">Младшие арканы · стихия: {s['element']}</div>
  <h1>Масть {s['gen']} в Таро: значение всех карт</h1>
  <p class="lead">{s['intro']}</p>
</section>
<section><div class="grid tiles">{''.join(tile(c, c['num']) for c in deck)}</div></section>
{cta("Задай вопрос картам", "Расклад Таро на любовь, работу или выбор — в боте LineLife. Карта дня бесплатно каждое утро.", f"seo_taro_{s['slug']}", "🎴 Сделать расклад")}
{faq_html(qa)}
<section><h2>Другие масти и старшие арканы</h2><div class="chips">{others}<a class="chip" href="/taro/">Старшие арканы</a></div></section>"""
        page(hub, f"Масть {s['gen']} в Таро: значение всех 14 карт — LineLife",
             f"Значение карт масти {s['gen']} в Таро: от Туза до Короля. Темы масти — {s['theme']}. Прямое и перевёрнутое положение, любовь и работа.",
             body, [crumbs_ld(cr), faq_ld(qa), {"@type": "CollectionPage", "name": f"Масть {s['gen']}", "url": SITE + hub, "inLanguage": "ru"}],
             og_type="website", priority="0.8", freq="monthly")

    # главный хаб Таро
    url = "/taro/"
    cr = [("Главная", "/"), ("Значения карт Таро", url)]
    suits_html = ''.join(f"""<section><h2><a href="/taro/{s['slug']}/" class="h-link">Масть {s['gen']}</a></h2><p class="muted">{s['element']}: {s['theme']}</p>
<div class="grid tiles">{''.join(tile(c, c['num']) for c in MINOR if c['suit']==s['slug'])}</div></section>""" for s in SUITS)
    qa = [("Сколько карт в колоде Таро?", "В классической колоде 78 карт: 22 старших аркана и 56 младших. Младшие арканы делятся на четыре масти: Жезлы, Кубки, Мечи и Пентакли."),
          ("Чем старшие арканы отличаются от младших?", "Старшие арканы описывают большие жизненные темы и этапы, а младшие — повседневные события, чувства и дела."),
          ("Как сделать расклад Таро онлайн?", "Открой бота @mylinelife_bot в Telegram, задай вопрос и выбери расклад. Карта дня — бесплатно каждый день.")]
    body = f"""{breadcrumbs(cr)}
<section class="hub-head">
  <div class="eyebrow">Справочник</div>
  <h1>Значение карт Таро: все 78 карт</h1>
  <p class="lead">Толкования всех карт колоды Таро: 22 старших аркана и 56 младших в четырёх мастях. Для каждой карты — прямое и перевёрнутое положение, любовь, работа, совет и ответ «да или нет».</p>
  <div class="daily" id="daily"></div>
</section>
<section><h2>Старшие арканы</h2><p class="muted">Большие жизненные темы и этапы</p><div class="grid tiles">{''.join(tile(c, c['num']) for c in TAROT)}</div></section>
{suits_html}
<section class="prose card">
  <h2>Как читать карты Таро</h2>
  <p>Каждая карта несёт несколько слоёв смысла. Прямое положение показывает основное значение, перевёрнутое — его ослабленную, задержанную или искажённую форму. В раскладе важна и позиция: одна и та же карта по-разному звучит в позиции «прошлое», «препятствие» или «совет».</p>
  <p>Если в раскладе много старших арканов, ситуация воспринимается как значимая. Преобладание одной масти подсказывает сферу: Жезлы — дела и энергия, Кубки — чувства, Мечи — мысли и конфликты, Пентакли — деньги и материальное. Помни, что Таро — это повод взглянуть на ситуацию по-новому, а не готовый ответ.</p>
</section>
{cta("Задай свой вопрос картам", "Расклад Таро на любовь, работу или выбор — в боте LineLife. Карта дня бесплатно каждое утро.", "seo_taro_hub", "🎴 Сделать расклад")}
{faq_html(qa)}
{daily_script()}"""
    page(url, "Значение карт Таро: все 78 карт с толкованием — LineLife",
         "Справочник значений всех 78 карт Таро: старшие арканы и масти Жезлов, Кубков, Мечей и Пентаклей. Прямое и перевёрнутое положение, любовь, работа, «да или нет».",
         body, [crumbs_ld(cr), faq_ld(qa), {"@type": "CollectionPage", "name": "Значение карт Таро", "url": SITE + url, "inLanguage": "ru"}],
         og_type="website", priority="0.9", freq="weekly")

def daily_script():
    data = [{"s": c["slug"], "n": c["name"], "k": c["kw"][:3], "a": c["advice"]} for c in TAROT + MINOR]
    return """<script>
(function(){var C=%s;var el=document.getElementById('daily');if(!el)return;
var d=new Date();var seed=d.getFullYear()*1000+(d.getMonth()+1)*40+d.getDate();var c=C[(seed*7919)%%C.length];
el.innerHTML='<div class="daily-in"><div class="eyebrow">Карта дня · '+d.toLocaleDateString('ru-RU',{day:'numeric',month:'long'})+'</div><h3><a href="/taro/'+c.s+'/">'+c.n+'</a></h3><p>'+c.a+'</p><p class="note">'+c.k.join(' · ')+' — <a href="/taro/'+c.s+'/">читать значение</a></p></div>';
})();
</script>""" % json.dumps(data, ensure_ascii=False)


# ---------------- РУНЫ ----------------
def rune_pages():
    n = len(RUNES)
    for i, r in enumerate(RUNES):
        url = f"/runy/{r['slug']}/"
        title = f"Руна {r['name']} ({r['sym']}): значение, перевёрнутая, в любви — LineLife"
        desc = f"Значение руны {r['name']} {r['sym']} — «{r['meaning']}»: {', '.join(r['kw'][:3])}. Прямое{' и перевёрнутое' if r['rev'] else ''} положение, любовь, работа и совет руны."
        h1 = f"Руна {r['name']}: значение и толкование"
        prev = RUNES[(i - 1) % n]; nxt = RUNES[(i + 1) % n]
        revtxt = r["reversed"] or f"Руна {r['name']} симметрична и не имеет перевёрнутого положения: она читается одинаково, как бы ни легла."
        qa = [(f"Что означает руна {r['name']}?", r["general"]),
              (f"Что значит перевёрнутая руна {r['name']}?", revtxt),
              (f"Что означает руна {r['name']} в любви?", r["love"])]
        cr = [("Главная", "/"), ("Значения рун", "/runy/"), (r["name"], url)]
        others = ''.join(f'<a class="chip" href="/runy/{t["slug"]}/"><b>{t["sym"]}</b> {t["name"]}</a>' for t in RUNES if t is not r)
        body = f"""{breadcrumbs(cr)}
<article class="entry">
  <header class="entry-head">
    <div class="sigil rune-sigil" aria-hidden="true">{r['sym']}</div>
    <div>
      <div class="eyebrow">Старший Футарк · Ætt {r['aett']} · звук «{r['lit']}»</div>
      <h1>{h1}</h1>
      <p class="lead">{r['general']}</p>
      <ul class="kw"><li>«{r['meaning']}»</li>{''.join(f'<li>{k}</li>' for k in r['kw'])}</ul>
    </div>
  </header>
  <div class="entry-grid">
    <section class="card"><h2>{'Перевёрнутая руна ' + r['name'] if r['rev'] else 'Перевёрнутое положение'}</h2><p>{revtxt}</p></section>
    <section class="card"><h2>Руна {r['name']} в любви</h2><p>{r['love']}</p></section>
    <section class="card"><h2>Руна {r['name']} в работе</h2><p>{r['work']}</p></section>
    <section class="card"><h2>Совет руны</h2><p>{r['advice']}</p></section>
  </div>
  <p class="muted">Толкование дано по традиции Старшего Футарка и носит развлекательный характер.</p>
</article>
{cta(f"Какая руна выпадет тебе сегодня?", "Руна дня бесплатно каждое утро и расклады на рунах — в боте LineLife.", f"seo_runa_{r['slug']}", "ᚠ Вытянуть руну")}
<nav class="pager" aria-label="Соседние руны">
  <a href="/runy/{prev['slug']}/">← {prev['name']}</a>
  <a href="/runy/">Все руны</a>
  <a href="/runy/{nxt['slug']}/">{nxt['name']} →</a>
</nav>
{faq_html(qa)}
<section><h2>Другие руны Футарка</h2><div class="chips">{others}</div></section>"""
        page(url, title, desc, body, [article_ld(h1, desc, url), crumbs_ld(cr), faq_ld(qa)], priority="0.8")

    # руна Одина (пустая)
    url = "/runy/odin/"
    cr = [("Главная", "/"), ("Значения рун", "/runy/"), ("Руна Одина", url)]
    qa = [("Что означает пустая руна?", "Пустую руну, или руну Одина, в современных наборах связывают с неизвестностью и судьбой, которая ещё не определена."),
          ("Есть ли пустая руна в Старшем Футарке?", "Нет. Её добавили в наборы в XX веке, в исторических рунических рядах её нет, поэтому многие гадающие её не используют.")]
    body = f"""{breadcrumbs(cr)}
<article class="entry">
  <header class="entry-head">
    <div class="sigil rune-sigil" aria-hidden="true">◯</div>
    <div>
      <div class="eyebrow">Дополнительная руна</div>
      <h1>Пустая руна (руна Одина): значение</h1>
      <p class="lead">Пустая руна — гладкий камень без знака, который есть во многих современных наборах. Её называют руной Одина и связывают с неизвестностью, судьбой и тем, что пока не может быть открыто.</p>
      <ul class="kw"><li>неизвестность</li><li>судьба</li><li>доверие</li><li>чистый лист</li></ul>
    </div>
  </header>
  <div class="entry-grid">
    <section class="card"><h2>Откуда она взялась</h2><p>В исторических рунических рядах пустой руны нет: её добавили в XX веке. Поэтому одни гадающие убирают её из набора, а другие считают важным знаком.</p></section>
    <section class="card"><h2>Как её читают</h2><p>Если пустая руна выпала в раскладе, её трактуют как знак, что ответ пока скрыт, а исход зависит от решений, которые ещё не приняты.</p></section>
    <section class="card"><h2>Совет</h2><p>Отпусти желание всё контролировать. Ситуация ещё не сложилась, и в этом её свобода.</p></section>
  </div>
</article>
{cta("Вытяни свою руну дня", "Руна дня бесплатно каждое утро — в боте LineLife.", "seo_runa_odin", "ᚠ Вытянуть руну")}
{faq_html(qa)}"""
    page(url, "Пустая руна (руна Одина): значение в раскладе — LineLife",
         "Что означает пустая руна Одина: откуда она взялась, как её трактуют в раскладе и стоит ли её использовать.",
         body, [article_ld("Пустая руна (руна Одина): значение", "Значение пустой руны Одина", url), crumbs_ld(cr), faq_ld(qa)], priority="0.6")

    # хаб
    url = "/runy/"
    cr = [("Главная", "/"), ("Значения рун", url)]
    groups = ""
    for aett in ["Фрейра", "Хеймдалля", "Тюра"]:
        tiles = ''.join(f'<a class="card tile rune-tile" href="/runy/{r["slug"]}/"><span class="rs">{r["sym"]}</span><h3>{r["name"]}</h3><p>{r["meaning"]}</p></a>' for r in RUNES if r["aett"] == aett)
        groups += f'<section><h2>Ætt {aett}</h2><div class="grid tiles rtiles">{tiles}</div></section>'
    qa = [("Сколько рун в Старшем Футарке?", "24 руны, разделённые на три группы по восемь — эттира: Фрейра, Хеймдалля и Тюра."),
          ("Какие руны не имеют перевёрнутого положения?", "Симметричные руны: Гебо, Хагалаз, Наутиз, Иса, Йера, Эйваз, Соулу, Ингуз и Дагаз. Они читаются одинаково в любом положении."),
          ("Как погадать на рунах онлайн?", "Открой бота @mylinelife_bot в Telegram: руна дня бесплатно, а также расклады на рунах на свой вопрос.")]
    body = f"""{breadcrumbs(cr)}
<section class="hub-head">
  <div class="eyebrow">Справочник</div>
  <h1>Значение рун Старшего Футарка</h1>
  <p class="lead">24 руны Старшего Футарка с толкованием: прямое и перевёрнутое положение, значение в любви и работе, совет руны. Руны разделены на три эттира по восемь знаков.</p>
</section>
{groups}
<section><a class="card tile" href="/runy/odin/"><span class="rs">◯</span><h3>Пустая руна (руна Одина)</h3><p>Современное дополнение к набору</p></a></section>
<section class="prose card">
  <h2>Как читать руны</h2>
  <p>Руна, выпавшая прямо, показывает своё основное значение. Перевёрнутая — ослабленное или противоположное. Девять рун симметричны и переворачиваться не могут. Самый простой расклад — одна руна на день или на вопрос: она подсказывает настроение и совет.</p>
</section>
{cta("Руна дня ждёт тебя", "Руна дня бесплатно каждое утро и расклады на рунах — в боте LineLife.", "seo_runy_hub", "ᚠ Вытянуть руну")}
{faq_html(qa)}"""
    page(url, "Значение рун: все 24 руны Старшего Футарка с толкованием — LineLife",
         "Справочник рун Старшего Футарка: значение всех 24 рун, прямое и перевёрнутое положение, любовь, работа, совет. Бесплатная руна дня в Telegram.",
         body, [crumbs_ld(cr), faq_ld(qa), {"@type": "CollectionPage", "name": "Значение рун", "url": SITE + url, "inLanguage": "ru"}],
         og_type="website", priority="0.9", freq="weekly")


# ---------------- ХИРОМАНТИЯ ----------------
def palm_pages():
    for p in PALM:
        url = f"/hiromantiya/{p['slug']}/"
        title = f"{p['name']} на руке: значение, где находится, виды — LineLife"
        desc = f"{p['name']} на ладони: где находится и как её читать в хиромантии. Длинная, короткая, прерывистая, раздвоенная — значения с примерами."
        h1 = f"{p['name']} на руке: где находится и что означает"
        cr = [("Главная", "/"), ("Хиромантия", "/hiromantiya/"), (p["name"], url)]
        variants = ''.join(f'<section class="card"><h3>{E(v)}</h3><p>{E(t)}</p></section>' for v, t in p["variants"])
        others = ''.join(f'<a class="chip" href="/hiromantiya/{o["slug"]}/">{o["name"]}</a>' for o in PALM if o is not p)
        body = f"""{breadcrumbs(cr)}
<article class="entry">
  <header class="entry-head">
    <div class="sigil palm-sigil">{palm_svg(p['slug'])}</div>
    <div>
      <div class="eyebrow">Хиромантия</div>
      <h1>{h1}</h1>
      <p class="lead">{p['where']}</p>
    </div>
  </header>
  <section class="prose card"><h2>Что означает {p['name'].lower()}</h2><p>{p['general']}</p></section>
  <h2>Как читать {p['name'].lower()}</h2>
  <div class="entry-grid">{variants}</div>
  <p class="muted">Хиромантия — традиция толкования линий руки, а не научный метод. Толкования приведены в развлекательных целях.</p>
</article>
{cta(f"Что говорит твоя {p['name'].lower()}?", "Пришли фото ладони в бот LineLife — и получи разбор линий прямо в Telegram.", f"seo_palm_{p['slug']}", "🖐 Прочитать мою ладонь")}
{faq_html(p['faq'])}
<section><h2>Другие линии на ладони</h2><div class="chips">{others}</div></section>"""
        page(url, title, desc, body, [article_ld(h1, desc, url), crumbs_ld(cr), faq_ld(p["faq"])], priority="0.8")

    url = "/hiromantiya/"
    cr = [("Главная", "/"), ("Хиромантия", url)]
    tiles = ''.join(f'<a class="card tile" href="/hiromantiya/{p["slug"]}/"><span class="dot" style="background:{p["color"]}"></span><h3>{p["name"]}</h3><p>{p["general"][:110].rsplit(" ",1)[0]}…</p></a>' for p in PALM)
    qa = [("Какую руку смотрят в хиромантии?", "Обычно смотрят ведущую руку: правую у правшей и левую у левшей. Вторую руку иногда читают как врождённые склонности."),
          ("Можно ли погадать по ладони по фото?", "Да. Пришли фото ладони в бот @mylinelife_bot: раскрытая ведущая рука, ровный свет, линии хорошо видны."),
          ("Меняются ли линии на руке?", "Да, со временем рисунок линий может меняться, поэтому ладонь стоит иногда разглядывать заново.")]
    body = f"""{breadcrumbs(cr)}
<section class="hub-head with-art">
  <div>
    <div class="eyebrow">Справочник</div>
    <h1>Хиромантия: значение линий на руке</h1>
    <p class="lead">Хиромантия читает характер и склонности по рисунку ладони. Любой разбор начинается с четырёх главных линий: жизни, сердца, головы и судьбы. Выбери линию, чтобы узнать, где она находится и как её трактуют.</p>
  </div>
  <div class="hub-art">{palm_svg()}</div>
</section>
<section><div class="grid tiles g2">{tiles}</div></section>
<section class="prose card">
  <h2>Как сфотографировать ладонь для гадания</h2>
  <ol>
    <li>Выбери ведущую руку: правую, если ты правша, левую — если левша.</li>
    <li>Раскрой ладонь, пальцы слегка разведи.</li>
    <li>Встань у окна или включи яркий ровный свет без резких теней.</li>
    <li>Держи телефон прямо над ладонью, чтобы она заняла почти весь кадр.</li>
    <li>Проверь, что линии чётко видны, и отправь фото в бот.</li>
  </ol>
</section>
{cta("Гадание по ладони по фото", "Пришли фото ладони в бот LineLife — и получи разбор основных линий прямо в Telegram.", "seo_palm_hub", "🖐 Прочитать мою ладонь")}
{faq_html(qa)}"""
    page(url, "Хиромантия онлайн: значение линий на руке с фото и схемой — LineLife",
         "Хиромантия для начинающих: линия жизни, сердца, головы и судьбы — где находятся и что означают. Гадание по ладони по фото в Telegram.",
         body, [crumbs_ld(cr), faq_ld(qa), {"@type": "CollectionPage", "name": "Хиромантия", "url": SITE + url, "inLanguage": "ru"}],
         og_type="website", priority="0.9", freq="weekly")


# ---------------- ГЛАВНАЯ ----------------
def home():
    qa = [("Как погадать по ладони по фото?", "Открой бота @mylinelife_bot в Telegram, нажми «Старт» и отправь фото ладони при хорошем освещении. Бот разберёт основные линии: жизни, сердца, головы и судьбы."),
          ("Это бесплатно?", "Карта дня и руна дня бесплатны каждый день. Подробные расклады и полный разбор ладони — платные."),
          ("Какую руку фотографировать?", "Ведущую: правую, если ты правша, и левую, если левша. Ладонь раскрыта, пальцы слегка разведены, свет ровный, без резких теней."),
          ("Что происходит с моим фото?", "Фото используется только для разбора ладони. Подробно — в политике обработки персональных данных на сайте."),
          ("Это настоящее предсказание?", "Нет. LineLife — развлекательный сервис. Расклады и разборы — повод взглянуть на ситуацию по-новому, а не прогноз будущего.")]
    tarot_chips = ''.join(f'<a class="chip" href="/taro/{c["slug"]}/">{c["name"]}</a>' for c in TAROT[:12])
    rune_chips = ''.join(f'<a class="chip" href="/runy/{r["slug"]}/"><b>{r["sym"]}</b> {r["name"]}</a>' for r in RUNES[:12])
    body = f"""<section class="hero">
  <div>
    <div class="eyebrow">Хиромантия · Таро · Руны</div>
    <h1>Гадание по ладони по фото онлайн</h1>
    <p class="lead">Сфотографируй свою ладонь — и узнай, что говорят линии жизни, сердца и головы. Расклады Таро и руны прямо в Telegram. Карта дня и руна дня — бесплатно каждое утро.</p>
    <div class="cta-row">
      <a class="btn btn-gold" href="{bot('site_hero')}">🖐 Прочитать мою ладонь</a>
      <a class="btn btn-ghost" href="{CHANNEL}">Канал с картой дня</a>
      <a class="btn btn-ghost" href="{VK}">Мы ВКонтакте</a>
    </div>
    <p class="note">Без регистрации и приложений — всё внутри Telegram. 18+</p>
  </div>
  <div class="palm">{palm_svg()}</div>
</section>

<section class="daily-wrap"><div class="daily" id="daily"></div></section>

<section id="features">
  <div class="sec-head">
    <div class="eyebrow">Что умеет LineLife</div>
    <h2>Подсказка на каждый день</h2>
    <p>Четыре способа взглянуть на ситуацию по-новому. Начни с бесплатного — карты и руны дня.</p>
  </div>
  <div class="grid g4">
    <a class="card tile" href="/hiromantiya/"><div class="ico">🖐</div><h3>Ладонь по фото</h3><p>Разбор главных линий руки по одной фотографии: жизни, сердца, головы и судьбы.</p></a>
    <a class="card tile" href="/taro/"><div class="ico">🎴</div><h3>Расклады Таро</h3><p>Расклад на твой вопрос: отношения, работа, выбор между вариантами.</p></a>
    <a class="card tile" href="/runy/"><div class="ico">ᚠ</div><h3>Руны</h3><p>Руна-совет и расклады на рунах Старшего Футарка.</p></a>
    <div class="card"><div class="ico">☀️</div><h3>Карта и руна дня</h3><p>Каждое утро — новая карта и руна с толкованием.</p><span class="free">Бесплатно</span></div>
  </div>
</section>

<section id="how">
  <div class="sec-head"><div class="eyebrow">Как это работает</div><h2>Три шага до разбора ладони</h2></div>
  <div class="grid g3">
    <div class="card step"><span class="n">1</span><h3>Открой бота</h3><p>Нажми кнопку на этой странице и «Старт» в Telegram. Сразу получишь карту дня в подарок.</p></div>
    <div class="card step"><span class="n">2</span><h3>Сфотографируй ладонь</h3><p>Ведущая рука, раскрытая ладонь, хороший свет. Линии должны быть хорошо видны.</p></div>
    <div class="card step"><span class="n">3</span><h3>Получи разбор</h3><p>Бот расскажет, что говорят линии твоей руки, и подскажет, на что обратить внимание.</p></div>
  </div>
</section>

<section id="lines">
  <div class="sec-head">
    <div class="eyebrow">Основы хиромантии</div>
    <h2>Главные линии на ладони</h2>
    <p>В хиромантии принято смотреть ведущую руку: правую у правшей и левую у левшей. Четыре линии, с которых начинается любой разбор:</p>
  </div>
  <div class="grid g2">{''.join(f'<a class="card tile" href="/hiromantiya/{p["slug"]}/"><span class="dot" style="background:{p["color"]}"></span><h3>{p["name"]}</h3><p>{p["where"]}</p></a>' for p in PALM)}</div>
</section>

<section>
  <div class="sec-head"><div class="eyebrow">Справочник</div><h2>Значения карт Таро и рун</h2>
  <p>Толкования всех 78 карт Таро и 24 рун Старшего Футарка: прямое и перевёрнутое положение, любовь, работа, совет.</p></div>
  <h3 class="sub">Карты Таро</h3><div class="chips">{tarot_chips}<a class="chip" href="/taro/zhezly/">Масть Жезлов</a><a class="chip" href="/taro/kubki/">Масть Кубков</a><a class="chip" href="/taro/mechi/">Масть Мечей</a><a class="chip" href="/taro/pentakli/">Масть Пентаклей</a><a class="chip more" href="/taro/">Все 78 карт →</a></div>
  <h3 class="sub">Руны</h3><div class="chips">{rune_chips}<a class="chip more" href="/runy/">Все руны →</a></div>
</section>

{faq_html(qa)}
{cta("Что скажет твоя ладонь?", "Открой бота — первая карта дня уже ждёт тебя.", "site_footer_cta", "🖐 Открыть LineLife в Telegram")}
{daily_script()}"""
    graph = [{"@type": "WebSite", "name": "LineLife", "alternateName": "Лайнлайф", "url": SITE + "/", "inLanguage": "ru"},
             {"@type": "Organization", "name": "LineLife", "url": SITE + "/", "logo": SITE + "/assets/icon-512.png",
              "sameAs": [BOT, CHANNEL, VK]},
             faq_ld(qa)]
    page("/", "Гадание по ладони по фото онлайн, Таро и руны — LineLife",
         "Гадание по ладони по фото в Telegram: сфотографируй руку и узнай, что говорят линии. Расклады Таро и руны. Карта дня и руна дня бесплатно. 18+",
         body, graph, og_type="website", priority="1.0", freq="daily")


def notfound():
    body = f"""<section class="hub-head" style="text-align:center;padding:60px 0">
  <div class="eyebrow">Ошибка 404</div>
  <h1>Эта страница затерялась среди звёзд</h1>
  <p class="lead" style="margin:16px auto 28px">Возможно, ссылка устарела. Загляни в справочники или открой бота.</p>
  <div class="cta-row" style="justify-content:center">
    <a class="btn btn-gold" href="/">На главную</a><a class="btn btn-ghost" href="/taro/">Карты Таро</a><a class="btn btn-ghost" href="/runy/">Руны</a>
  </div>
</section>"""
    page("/404.html", "Страница не найдена — LineLife", "Страница не найдена.", body, robots="noindex, follow", sitemap=False)



def privacy():
    url = "/privacy.html"
    cr = [("Главная", "/"), ("Политика конфиденциальности", url)]
    body = f"""{breadcrumbs(cr)}
<article class="prose legal">
<h1>Политика обработки персональных данных</h1>
<p class="muted">Редакция от 18 октября 2026 года</p>

<h2>1. Общие положения</h2>
<p>Настоящая Политика определяет порядок обработки и защиты персональных данных пользователей Telegram-бота LineLife (@mylinelife_bot, далее — «Бот») и сайта {SITE} (далее — «Сайт») в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных».</p>
<div class="card">
<p><strong>Оператор:</strong> Овчаренко Анастасия Дмитриевна, плательщик налога на профессиональный доход (самозанятый), ИНН 910236846388.<br>
<strong>Контакт для обращений:</strong> <a href="mailto:anikeevmaksim@yandex.ru">anikeevmaksim@yandex.ru</a></p>
</div>

<h2>2. Какие данные обрабатываются</h2>
<ul>
<li>идентификатор пользователя Telegram, имя и username, указанные в профиле Telegram;</li>
<li>фотографии ладони, которые пользователь сам отправляет в Бот;</li>
<li>текст вопросов и сообщений, отправленных в Бот;</li>
<li>сведения о покупках: дата, сумма, выбранная услуга, статус оплаты (данные банковских карт Оператор не получает — оплату обрабатывает платёжный сервис ЮKassa);</li>
<li>технические данные: дата первого запуска, источник перехода в Бот, настройки рассылки.</li>
</ul>

<h2>3. Цели обработки</h2>
<ul>
<li>предоставление развлекательных услуг Бота: разбор ладони по фото, расклады Таро и рун, карта и руна дня;</li>
<li>приём оплаты и выдача чеков в соответствии с законодательством;</li>
<li>отправка ежедневной карты дня и уведомлений — только с согласия пользователя;</li>
<li>улучшение работы Бота и анализ источников переходов в обезличенном виде.</li>
</ul>

<h2>4. Правовые основания</h2>
<p>Обработка осуществляется на основании согласия пользователя, которое он даёт, начиная пользоваться Ботом и отправляя в него фотографию, а также для исполнения договора (оказания оплаченной услуги).</p>

<h2>5. Фотографии ладони</h2>
<p>Фотография ладони используется только для выполнения разбора и не сохраняется в Боте после получения результата.</p>

<h2>6. Хранение и защита данных</h2>
<p>Оператор принимает необходимые меры для защиты данных от неправомерного доступа, изменения, распространения и уничтожения. Данные хранятся, пока пользователь пользуется Ботом, и удаляются по его запросу, кроме сведений, которые Оператор обязан хранить по закону (например, о платежах).</p>

<h2>7. Передача третьим лицам</h2>
<p>Оператор не продаёт персональные данные и передаёт их третьим лицам только в объёме, необходимом для оказания услуг:</p>
<ul>
<li>техническим сервисам, которые обеспечивают работу Бота и формирование ответов;</li>
<li>платёжному сервису ЮKassa — для проведения оплаты;</li>
<li>сервису «Мой налог» — для формирования чеков;</li>
<li>в случаях, прямо предусмотренных законодательством РФ.</li>
</ul>

<h2>8. Права пользователя</h2>
<p>Пользователь вправе получить сведения об обработке своих данных, потребовать их уточнения или удаления, отозвать согласие и отказаться от рассылки. Для этого достаточно написать на <a href="mailto:anikeevmaksim@yandex.ru">anikeevmaksim@yandex.ru</a> или отключить рассылку в настройках Бота. Запрос рассматривается в течение 10 рабочих дней.</p>

<h2>9. Возрастное ограничение</h2>
<p>Бот и Сайт предназначены для лиц старше 18 лет. Сервис носит развлекательный характер и не является предсказанием, медицинской, психологической, юридической или финансовой консультацией.</p>

<h2>10. Сайт</h2>
<p>Сайт не собирает персональные данные через формы. Хостинг Сайта предоставляет GitHub Pages, который может вести технические журналы посещений (IP-адрес, дата и время запроса).</p>

<h2>11. Изменения Политики</h2>
<p>Оператор может изменять Политику. Актуальная редакция всегда доступна по адресу {SITE}/privacy.html.</p>
</article>"""
    page(url, "Политика обработки персональных данных — LineLife",
         "Политика обработки персональных данных пользователей Telegram-бота LineLife (@mylinelife_bot) и сайта mylinelife.github.io.",
         body, [crumbs_ld(cr)], og_type="website", priority="0.3", freq="yearly")


def about():
    url = "/o-proekte/"
    cr = [("Главная", "/"), ("О проекте", url)]
    body = f"""{breadcrumbs(cr)}
<article class="prose">
<section class="hub-head">
  <div class="eyebrow">О проекте</div>
  <h1>LineLife — гадание по ладони, Таро и руны в Telegram</h1>
  <p class="lead">LineLife — развлекательный проект о хиромантии, Таро и рунах. Он состоит из Telegram-бота @mylinelife_bot, канала с ежедневной картой @linelife_daily и этого сайта-справочника.</p>
</section>
<div class="grid g3">
  <div class="card"><h3>Бот</h3><p>Разбор ладони по фото, расклады Таро на свой вопрос и руны. Карта дня и руна дня — бесплатно.</p><p><a href="{bot('site_about')}">Открыть бота →</a></p></div>
  <div class="card"><h3>Канал</h3><p>Каждое утро — карта Таро, руна и гороскоп для всех знаков зодиака.</p><p><a href="{CHANNEL}">Подписаться →</a> · <a href="{VK}">Группа ВКонтакте →</a></p></div>
  <div class="card"><h3>Справочник</h3><p>Значения всех 78 карт Таро, 24 рун Старшего Футарка и главных линий на ладони.</p><p><a href="/taro/">Перейти →</a></p></div>
</div>
<section class="card">
  <h2>На чём основаны толкования</h2>
  <p>Значения карт Таро приведены по традиции колоды Райдера — Уэйта, руны — по Старшему Футарку, линии ладони — по классической европейской хиромантии. Все тексты на сайте написаны специально для LineLife.</p>
  <p>Мы не пугаем и не обещаем: каждое толкование — это повод посмотреть на ситуацию с новой стороны, а не прогноз будущего.</p>
</section>
<section class="card">
  <h2>Важно знать</h2>
  <p>LineLife — развлекательный сервис для людей старше 18 лет. Материалы сайта и бота не являются предсказанием, медицинской, психологической, юридической или финансовой консультацией. В сложных жизненных ситуациях обращайся к профильным специалистам.</p>
</section>
<section class="card">
  <h2>Контакты</h2>
  <p>Вопросы и предложения: <a href="mailto:anikeevmaksim@yandex.ru">anikeevmaksim@yandex.ru</a>. Обработка данных описана в <a href="/privacy.html">политике конфиденциальности</a>.</p>
</section>
</article>"""
    page(url, "О проекте LineLife: гадание по ладони, Таро и руны в Telegram",
         "LineLife — развлекательный проект о хиромантии, Таро и рунах: Telegram-бот, канал с картой дня и справочник значений. Контакты и принципы.",
         body, [crumbs_ld(cr), {"@type": "AboutPage", "name": "О проекте LineLife", "url": SITE + url, "inLanguage": "ru"}],
         og_type="website", priority="0.5", freq="yearly")


def sitemap():
    xs = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr, fr in pages:
        xs.append(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{fr}</changefreq><priority>{pr}</priority></url>")
    xs.append("</urlset>")
    write("/sitemap.xml", "\n".join(xs) + "\n")
    write("/robots.txt", f"User-agent: *\nAllow: /\nDisallow: /404.html\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    home(); tarot_pages(); rune_pages(); palm_pages(); notfound(); privacy(); about(); sitemap()
    print(len(pages), "pages")
