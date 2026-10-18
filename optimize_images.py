"""Фото Айнуры (photos/own/pNNN.jpg, номера как в экспорте WhatsApp) -> лёгкие WebP + размытые заглушки (lqip.json).

Запуск:  ../chef-site-template/.venv/bin/python optimize_images.py
Потом:   закоммитить и запушить img/, и только затем python3 build.py (см. шапку build.py).
Какое фото к какому блюду: словарь DISHES ниже, ключ = id из site.json (третий элемент блюда).
"""
from PIL import Image, ImageOps
import os, json, io, base64, glob

SRC = 'photos/own'
HERO, HERO_WIDE, BANNER, ABOUT, OG = 'p137', 'p084', 'p104', 'p136', 'p084'
GALLERY = ['p131', 'p129', 'p130', 'p127', 'p139', 'p110', 'p121', 'p108', 'p087']
DISHES = {
    'bru-salmon': 'p051', 'bru-caprese': 'p055', 'bru-kazy': 'p056',
    'can-mozz': 'p058', 'can-caesar': 'p060',
    'burger': 'p062', 'club': 'p065', 'skewer': 'p067', 'blini': 'p070', 'tortilla': 'p071', 'eggplant': 'p072',
    'tart-shrimp': 'p074', 'tart-julien': 'p075', 'tart-mini': 'p077',
    'baursak': 'p079', 'samsa': 'p080', 'croissant': 'p081', 'cheburek': 'p082',
    'trifle': 'p089', 'cupcake': 'p090', 'whoopie': 'p091', 'oreshki': 'p093', 'fruittart': 'p094',
    'pavlova': 'p096', 'cakepop': 'p097', 'fruitcup': 'p099', 'kazsweets': 'p101',
    'meat': 'p102', 'fish': 'p103', 'veg': 'p105',
    'mango': 'p109', 'kiwi': 'p112', 'teacoffee': 'p113', 'water': 'p115', 'cups': 'p120',
}

lq = {}
def load(n): return ImageOps.exif_transpose(Image.open(f'{SRC}/{n}.jpg')).convert('RGB')
def save(im, name, w, q):
    w = min(w, im.width); h = round(im.height * w / im.width)
    im.resize((w, h), Image.LANCZOS).save(f'img/{name}-{w}.webp', 'WEBP', quality=q, method=6)
    return w
def lqip(im, name):
    t = im.copy(); t.thumbnail((28, 28 * 4)); b = io.BytesIO(); t.save(b, 'WEBP', quality=35, method=6)
    lq[name] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def square(im):
    s = min(im.size); l = (im.width - s) // 2; t = (im.height - s) // 2
    return im.crop((l, t, l + s, t + s))
def crop_ratio(im, r, ytop=0.5):
    H = min(im.height, round(im.width / r)); W = round(H * r); l = (im.width - W) // 2; t = int((im.height - H) * ytop)
    return im.crop((l, t, l + W, t + H))

os.makedirs('img', exist_ok=True)
for f in glob.glob('img/*'): os.remove(f)
im = load(HERO); print('hero', [save(im, 'hero', w, 55) for w in (480, 750, 900)]); lqip(im, 'hero')
im = crop_ratio(load(HERO_WIDE), 16 / 9, 0.45); print('hero-wide', [save(im, 'hero-wide', w, 58) for w in (1280, 1600)])
im = crop_ratio(load(BANNER), 2, 0.4); print('banner', [save(im, 'banner', w, 58) for w in (480, 960)]); lqip(im, 'banner')
im = square(load(ABOUT)); print('about', [save(im, 'about', w, 70) for w in (480, 800)]); lqip(im, 'about')
for i, n in enumerate(GALLERY, 1):
    im = load(n)
    if i == 1: ws = [save(im, f'g{i}', w, 58) for w in (480, 800, 1200)]
    else: im = square(im); ws = [save(im, f'g{i}', w, 60) for w in (360, 600)]
    lqip(im, f'g{i}'); print(f'g{i}', n, ws)
for k, n in DISHES.items():
    im = load(n); sq = square(im)
    save(sq, f'd-{k}', 160, 62); save(sq, f'd-{k}', 320, 62)
    big = im.copy(); big.thumbnail((720, 720)); big.save(f'img/d-{k}-big.webp', 'WEBP', quality=66, method=6)
print('dishes', len(DISHES))
im = crop_ratio(load(OG), 1200 / 630, 0.45).resize((1200, 630), Image.LANCZOS); im.save('img/og.jpg', 'JPEG', quality=80)
json.dump(lq, open('lqip.json', 'w'))
print('готово:', len(os.listdir('img')), 'файлов,', sum(os.path.getsize('img/' + f) for f in os.listdir('img')) // 1024, 'КБ')
