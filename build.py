"""Сборка сайта-меню для повара: index.tpl.html + site.json -> index.html

Что менять от повара к повару: ТОЛЬКО site.json, фото в photos/ (см. optimize_images.py) и при желании тексты.
Режим макета: "demo": true  -> заявки идут автору (phone_author), плашка-ватермарк сверху, noindex.
Рабочий сайт:  "demo": false -> заявки идут повару (phone_owner). Плашку .demo убрать из index.tpl.html.
Порядок публикации: 1) закоммитить и запушить img/ и fonts/  2) python3 build.py  3) закоммитить и запушить index.html
(build.py закрепляет CDN-адрес за коммитом, где менялись img/ или fonts/).
"""
import re, glob, os, json, subprocess, html

C = json.load(open('site.json', encoding='utf-8'))
DEMO = C['demo']
phone = C['phone_author'] if DEMO else C['phone_owner']
src = open('index.tpl.html', encoding='utf-8').read()

# повторяющиеся блоки из site.json
stats = ''.join(f'    <div class="stat rv"><b>{s["num"]}</b><span>{s["label"]}</span></div>\n' for s in C['stats']).rstrip('\n')
included = '\n'.join(f'        <li><div class="ic"><svg class="i"><use href="#{i["icon"]}"/></svg></div><div><strong>{i["title"]}</strong><span>{i["text"]}</span></div></li>' for i in C['included'])
extras = '\n'.join(f'          <li><svg class="i"><use href="#{e["icon"]}"/></svg>{e["label"]}</li>' for e in C['extras'])
tokens = {
 'TITLE': C['title'], 'DESCRIPTION': C['description'], 'OG_DESCRIPTION': C['og_description'], 'SITE_URL': C['site_url'],
 'AUTHOR': C['author'], 'BRAND': C['brand'], 'BRAND_SUB': C['brand_sub'], 'H1_HTML': C['h1_html'], 'HERO_SUB': C['hero_sub'],
 'STATS': stats, 'INCL_TITLE': C['incl_title'], 'INCL_LEAD': C['incl_lead'], 'INCLUDED': included,
 'EXTRA_TITLE': C['extra_title'], 'EXTRA_TEXT': C['extra_text'], 'EXTRAS': extras,
 'ALT_HERO': C['alt_hero'], 'ALT_BANNER': C['alt_banner'], 'GALLERY_TITLE': C['gallery_title'], 'GALLERY_LEAD': C['gallery_lead'], 'GALLERY_NOTE': C['gallery_note'],
 'FOOTER_TEXT': C['footer_text'], 'PHONE_OWNER': C['phone_owner'], 'PHONE_OWNER_PRETTY': C['phone_owner_pretty'],
 'INSTAGRAM_URL': C['instagram_url'], 'INSTAGRAM_HANDLE': C['instagram_handle'], 'AREA_LABEL': C['area_label'],
 'MIN_GUESTS': str(C['min_guests']),
 'MENU_JSON': json.dumps(C['menu'], ensure_ascii=False, indent=2), 'FORMATS_JSON': json.dumps(C['formats'], ensure_ascii=False),
}
for i, a in enumerate(C['alt_gallery']): tokens[f'ALT_G{i}'] = a
for k, v in tokens.items(): src = src.replace('{{' + k + '}}', v)
left = re.findall(r'\{\{[A-Z_0-9]+\}\}', src)
assert not left, f'не заполнены токены: {sorted(set(left))}'

# иконки
used = set(re.findall(r'<use href="#([a-z-]+)"', src)) | {'plus', 'minus', 'check'}
sym = []
for f in sorted(glob.glob('icons/*.svg')):
    n = os.path.basename(f)[:-4]
    if n not in used: continue
    s = open(f).read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = re.sub(r'^<svg[^>]*>|</svg>\s*$', '', s.strip())
    sym.append(f'<symbol id="{n}" viewBox="{vb}">{inner}</symbol>')
missing = sorted(n for n in used if not os.path.exists(f'icons/{n}.svg'))
assert not missing, f'нет иконок: {missing} (скачать с https://unpkg.com/@phosphor-icons/core@2.1.1/assets/regular/<имя>.svg)'
out = src.replace('<!--SPRITE-->', '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(sym) + '</svg>')

# размытые заглушки
lq = json.load(open('lqip.json'))
out = re.sub(r'<!--LQ:([a-z0-9-]+)-->', lambda m: 'style="background-image:url(' + lq[m.group(1)] + ')"', out)

# CDN jsDelivr: на GitHub Pages у части клиентов очень медленно
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout.strip()
sha = os.environ.get('CDN_SHA') or sh('git', 'log', '-1', '--format=%H', '--', 'img', 'fonts')
dirty = sh('git', 'status', '--porcelain', 'img', 'fonts')
CDN = f'https://cdn.jsdelivr.net/gh/{C["repo"]}@{sha}/' if sha and (os.environ.get('CDN_SHA') or not dirty) else ''
out = out.replace('__CDN__', CDN)
if CDN: out = re.sub(r'(?<![\w/.@-])img/(?=[a-z0-9-]+\.webp)', CDN + 'img/', out)

out = out.replace('__PHONE__', phone).replace('__SRC__', 'макета сайта' if DEMO else 'сайта')
if DEMO:
    out = out.replace('<!--ROBOTS-->', '<meta name="robots" content="noindex, nofollow">')
    out = out.replace('<!--DEMONOTE-->', '<p class="fine demo-note">Это макет сайта. Заявка из макета придёт его автору, а не повару. После запуска сайта заявки будут приходить повару.</p>')
    out = re.sub(r'<a href="tel:\+7[0-9]+">(.*?)</a>', r'<span class="telx">\1</span>', out)
else:
    out = out.replace('<!--ROBOTS-->', '').replace('<!--DEMONOTE-->', '')
open('index.html', 'w', encoding='utf-8').write(out)
bad = [c for c in ('—', '–') if c in out]
print('cdn', CDN or 'LOCAL', '| mode', 'DEMO' if DEMO else 'LIVE', '| заявки на', phone, '| тире:', bad or 'нет', '| байт', len(out))
