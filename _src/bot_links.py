"""Ссылки на бота @mylinelife_bot: deep link «<функция>__src_<источник>».
Бот сохраняет источник и сразу открывает экран функции; без префикса — главное меню."""
import re

BOT = "https://t.me/mylinelife_bot"
# ключи, которые поддерживает обработчик /start в боте
BOT_FEATURES = {"palm", "tarot", "card_day", "rune_day", "compat", "numerology"}
# источник -> функция (первое совпадение по префиксу); не найдено — главное меню
FEATURE_BY_SRC = [
    ("seo_taro_karta_dnya", "card_day"), ("seo_taro_arkan_compat", "compat"), ("seo_taro_arkan", "numerology"), ("arkan_result", "numerology"),
    ("seo_taro_", "tarot"), ("kd_result", "tarot"), ("daily_result", "tarot"),
    ("seo_runa_", "rune_day"), ("seo_runy_", "rune_day"), ("rd_result", "rune_day"),
    ("seo_palm_", "palm"), ("site_hero", "palm"),
    ("llm_palm", "palm"), ("llm_tarot", "tarot"), ("llm_card", "card_day"), ("llm_rune", "rune_day"),
    ("llm_compat", "compat"), ("llm_num", "numerology"),
    ("seo_compat", "compat"), ("compat_result", "compat"),
]
START_RE = re.compile(r"^(?:([a-z_]+)__)?src_([A-Za-z0-9_-]+)$")


def feature_for(src):
    return next((f for pre, f in FEATURE_BY_SRC if src.startswith(pre)), None)


def start_payload(src):
    fn = feature_for(src)
    return f"{fn}__src_{src}" if fn else f"src_{src}"


def check_start(payload):
    """Ошибка для параметра start или None: лимит Telegram 64 символа [A-Za-z0-9_-], формат, ключ."""
    if len(payload) > 64 or not re.fullmatch(r"[A-Za-z0-9_-]+", payload):
        return "длина > 64 или недопустимые символы"
    m = START_RE.match(payload)
    if not m:
        return "не формат [функция__]src_источник"
    fn, src = m.groups()
    if fn and fn not in BOT_FEATURES:
        return f"неизвестная функция {fn}"
    if feature_for(src) != fn:
        return f"ожидалась функция {feature_for(src)}, в ссылке {fn}"
    return None


def bot_url(src):
    p = start_payload(src)
    err = check_start(p)
    if err:
        raise ValueError(f"start={p}: {err}")
    return f"{BOT}?start={p}"
