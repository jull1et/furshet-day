"""Урезает шрифты до букв, которые есть на сайте (экономит ~45 КБ). Нужен только если в тексты добавили редкие символы
(казахские буквы Ә Ғ Қ Ң Ө Ұ Ү Һ І и т.п.): добавьте их в EXTRA и запустите  ./.venv/bin/python subset_fonts.py
Исходные полные файлы лежат в fonts-src/ (скачать: Google Fonts, Onest и Unbounded, cyrillic + latin, woff2)."""
import subprocess, os, json
EXTRA = ''  # например 'ӘәҒғҚқҢңӨөҰұҮүҺһІі'
html = open('index.tpl.html', encoding='utf-8').read() + json.dumps(json.load(open('site.json', encoding='utf-8')), ensure_ascii=False)
base = set(html) | set(chr(c) for c in range(0x20, 0x7f)) | set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя«»№–…·•°') | set(EXTRA)
cyr = sorted(c for c in base if 0x0400 <= ord(c) <= 0x04FF or ord(c) == 0x2116 or c in EXTRA)
lat = sorted(c for c in base if ord(c) < 0x250 or ord(c) in (0x2013, 0x2014, 0x2019, 0x201C, 0x201D, 0x2026, 0x2022, 0xA0))
u = lambda cs: ','.join(f'U+{ord(c):04X}' for c in cs)
for fam in ('onest', 'unbounded'):
    for kind, cs in (('cyrillic', cyr), ('latin', lat)):
        subprocess.run(['./.venv/bin/pyftsubset', f'fonts-src/{fam}-{kind}.woff2', '--unicodes=' + u(cs), '--flavor=woff2',
                        '--layout-features=kern,liga,calt,ccmp,locl,mark,mkmk', f'--output-file=fonts/{fam}-{kind}.woff2'], check=True)
        print(fam, kind, os.path.getsize(f'fonts/{fam}-{kind}.woff2') // 1024, 'KB')
