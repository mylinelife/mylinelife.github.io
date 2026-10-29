import os, random, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__))
from data_tarot import TAROT
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def page(c):
    random.seed(c['slug']); kws = eval(c['kw']) if isinstance(c['kw'],str) else c['kw']
    stars = ''.join(f'<i style="left:{random.randint(0,1000)}px;top:{random.randint(0,1500)}px;width:{random.choice([2,3,4])}px;height:{random.choice([2,3,4])}px;opacity:{random.random()*.6+.2}"></i>' for _ in range(90))
    return f'''<html><body style="margin:0"><div style="position:relative;width:1000px;height:1500px;overflow:hidden;background:radial-gradient(circle at 50% 40%,#2c2060,#1a1240 55%,#120c30);font-family:'DejaVu Serif',serif;text-align:center;color:#fff">
<style>i{{position:absolute;background:#fff;border-radius:50%}}</style>{stars}
<div style="position:absolute;top:100px;width:100%;font-size:84px;font-weight:700;color:#f3eeff">Карта Таро</div>
<div style="position:absolute;top:195px;width:100%;font-size:84px;font-weight:700;color:#e8c27a">{c['name']}</div>
<div style="position:absolute;top:300px;width:100%;font-size:34px;color:#c9bff0;font-family:sans-serif">Значение, любовь, работа, совет</div>
<div style="position:absolute;left:330px;top:430px;width:340px;height:545px;border:3px solid #e8c27a;border-radius:22px;background:radial-gradient(circle,#352870,#1c1445)"><div style="margin-top:165px;font-size:100px;color:#e8c27a">{c['num']}</div><div style="margin-top:20px;font-size:40px">{c['name']}</div></div>
<div style="position:absolute;top:1050px;width:100%;font-size:34px;font-family:sans-serif;line-height:64px"><div style="color:#f08cb4">♥ Любовь, работа, совет</div><div>{', '.join(kws[:3])}</div><div style="color:#e8c27a">Да или нет: {c['yesno']}</div></div>
<div style="position:absolute;left:250px;top:1370px;width:500px;height:68px;border-radius:34px;background:linear-gradient(90deg,#f6e0a8,#e8c27a);color:#1a1240;font:700 34px/68px sans-serif">mylinelife.ru</div>
</div></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1000,'height':1500})
    for c in TAROT:
        if c['slug'] in sys.argv[1:]:
            pg.set_content(page(c)); pg.screenshot(path=f"{ROOT}/assets/pins/pin-taro-{c['slug']}.jpg", type='jpeg', quality=90)
            print(c['slug'])
    b.close()
