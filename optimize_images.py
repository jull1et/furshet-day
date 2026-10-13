"""Фото -> лёгкие WebP разных размеров + размытые заглушки (lqip.json).

Положить исходники в photos/ с ФИКСИРОВАННЫМИ именами (любой размер, лучше от 1400 px по ширине):
  hero.jpg         главное фото первого экрана, вертикальное или квадратное (на телефоне обрезается по центру)
  table.jpg        большое фото галереи (горизонтальное, 3:2)
  g-hall.jpg, g-canape.jpg, g-fetamelon.jpg, g-stand.jpg   4 фото галереи (g-fetamelon вертикальное, остальные горизонтальные)
  banner.jpg       фото над меню (любое, обрежется до 2:1)
Запуск:  ./.venv/bin/python optimize_images.py
Потом:   закоммитить и запушить img/, и только затем python3 build.py (см. шапку build.py).
"""
from PIL import Image
import os, json, io, base64

lq = {}
def save(im, name, w, q):
    h = round(im.height * w / im.width)
    p = f'img/{name}-{w}.webp'
    im.resize((w, h), Image.LANCZOS).save(p, 'WEBP', quality=q, method=6)
    return os.path.getsize(p) // 1024
def lqip(im, name):
    t = im.copy(); t.thumbnail((28, 28 * 4)); b = io.BytesIO(); t.save(b, 'WEBP', quality=35, method=6)
    lq[name] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

SPEC = {  # имя: (ширины, качество)  hero: телефон до 1000 px, компьютер 1400 px
    'hero': ([480, 750, 1000], 52), 'table': ([480, 800, 1200], 58),
    'g-hall': ([360, 600], 60), 'g-canape': ([360, 600], 60), 'g-fetamelon': ([360, 600], 60), 'g-stand': ([360, 600], 60),
}
os.makedirs('img', exist_ok=True)
for n, (ws, q) in SPEC.items():
    im = Image.open(f'photos/{n}.jpg').convert('RGB')
    kb = [(w, save(im, n, min(w, im.width), q)) for w in ws]
    lqip(im, n)
    if n == 'hero': kb.append((1400, save(im, 'hero', min(1400, im.width), 58)))
    print(n, kb, 'KB')
im = Image.open('photos/banner.jpg').convert('RGB')
W = im.width; H = W // 2; top = int((im.height - H) * 0.5)
im = im.crop((0, top, W, top + H))
print('banner', [(w, save(im, 'banner', w, 58)) for w in (480, 960)], 'KB'); lqip(im, 'banner')
# картинка для превью ссылки в мессенджерах 1200x630
h = Image.open('photos/hero.jpg').convert('RGB'); h = h.resize((1200, round(h.height * 1200 / h.width)), Image.LANCZOS)
top = max(0, (h.height - 630) // 3); h.crop((0, top, 1200, top + 630)).save('img/og.jpg', 'JPEG', quality=78)
json.dump(lq, open('lqip.json', 'w'))
print('готово: img/ и lqip.json обновлены')
