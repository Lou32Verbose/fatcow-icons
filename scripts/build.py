"""Build byte-preserving PNG distributions and padded CSS sprites."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = {'16x16': 16, '16x16-grey': 16, '32x32': 32, '32x32-grey': 32}

def build():
    manifest = {'name': 'fatcow', 'variants': {}}
    with tempfile.TemporaryDirectory(prefix='.icons-build-', dir=ROOT) as temporary:
        output = Path(temporary)
        for variant, size in VARIANTS.items():
            sources = sorted((ROOT / 'src' / variant).glob('*.png'))
            if not sources:
                raise ValueError(f'No icons in {variant}')
            folder = output / variant
            (folder / 'png').mkdir(parents=True)
            (folder / 'sprite').mkdir()
            columns = math.ceil(math.sqrt(len(sources)))
            # Two upstream 16px variants contain a 32px file_extension_png icon.
            stride = 34
            sheet = Image.new('RGBA', (columns * stride, math.ceil(len(sources) / columns) * stride))
            base = f'fatcow-{variant}'
            rules = [f'.{base} {{ display: inline-block; width: {size}px; height: {size}px; vertical-align: middle; background-image: url("fatcow.png"); background-repeat: no-repeat; }}']
            icons, names = [], set()
            for index, source in enumerate(sources):
                name = source.stem
                # Prefixing icon selectors also supports names beginning with digits.
                if not re.fullmatch(r'[a-zA-Z0-9_-]+', name) or name.lower() in names:
                    raise ValueError(f'Invalid or colliding name: {source}')
                names.add(name.lower())
                with Image.open(source) as original:
                    if original.format != 'PNG' or original.size != ((32, 32) if size == 16 and name == 'file_extension_png' else (size, size)) or getattr(original, 'n_frames', 1) != 1:
                        raise ValueError(f'Expected static {size}px PNG: {source}')
                    pixels = original.convert('RGBA')
                x, y = index % columns * stride + 1, index // columns * stride + 1
                sheet.paste(pixels, (x, y))
                shutil.copyfile(source, folder / 'png' / source.name)
                icons.append(dict(name=name, source=f'src/{variant}/{source.name}', png=f'{variant}/png/{source.name}', sha256=hashlib.sha256(source.read_bytes()).hexdigest(), width=pixels.width, height=pixels.height, x=x, y=y))
                rules.append(f'.{base}.fatcow-{name} {{ width: {pixels.width}px; height: {pixels.height}px; background-position: -{x}px -{y}px; }}')
            sheet.save(folder / 'sprite/fatcow.png')
            css = '\n'.join(rules) + '\n'
            (folder / 'sprite/fatcow.css').write_text(css, encoding='utf-8')
            (folder / 'sprite/fatcow.min.css').write_text(re.sub(r'\s*([{}:;])\s*', r'\1', css).strip() + '\n', encoding='utf-8')
            manifest['variants'][variant] = dict(count=len(icons), icons=icons)
        (output / 'icons.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        cards = ''.join(f'<li data-variant="{v}"><img src="{html.escape(i["png"])}" width="{i["width"]}" height="{i["height"]}" loading="lazy" alt=""><code>{html.escape(i["name"])}</code></li>' for v, group in manifest['variants'].items() for i in group['icons'])
        preview = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>FatCow icons</title>
<style>body{max-width:1100px;margin:30px auto;padding:16px;font:15px system-ui;color:#243026;background:#f7f8f4}h1{color:#346037}input,select{font:inherit;padding:8px;margin:4px}ul{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));padding:0}li{display:flex;align-items:center;gap:12px;padding:8px;background:white;border:1px solid #ddd;min-width:0}li[hidden]{display:none}code{overflow-wrap:anywhere}img{flex-shrink:0}</style>
<h1>FatCow Farm-Fresh icons</h1><p>Icons by <a href="http://www.fatcow.com/free-icons">FatCow</a>. <a href="../LICENSE.md">License</a> · <a href="../README.md">Installation</a> · <a href="icons.json">Manifest</a></p>
<label>Search <input type="search" id="search"></label><label>Variant <select id="variant">OPTIONS</select></label><p id="count" aria-live="polite"></p><ul>CARDS</ul>
<script>const rows=[...document.querySelectorAll('li')],search=document.querySelector('#search'),variant=document.querySelector('#variant');function filter(){let count=0;for(const row of rows){row.hidden=row.dataset.variant!==variant.value||!row.textContent.toLowerCase().includes(search.value.toLowerCase());if(!row.hidden)count++}document.querySelector('#count').textContent=count+' icons'}search.addEventListener('input',filter);variant.addEventListener('change',filter);filter();</script></html>'''
        (output / 'index.html').write_text(preview.replace('OPTIONS', ''.join(f'<option>{v}</option>' for v in VARIANTS)).replace('CARDS', cards), encoding='utf-8')
        target = ROOT / 'dist'
        target.mkdir(exist_ok=True)
        for variant in VARIANTS:
            if (target / variant).exists():
                shutil.rmtree(target / variant)
        shutil.copytree(output, target, dirs_exist_ok=True)
    print('Built ' + ', '.join(f'{v}: {g["count"]}' for v, g in manifest['variants'].items()))

def archive():
    version = json.loads((ROOT / 'package.json').read_text())['version']
    destination = ROOT / 'artifacts' / f'fatcow-{version}.zip'
    destination.parent.mkdir(exist_ok=True)
    files = sorted(p for p in (ROOT / 'dist').rglob('*') if p.is_file())
    files += [ROOT / name for name in ('README.md', 'LICENSE.md', 'NOTICE.md', 'docs/upstream/readme-fatcow.txt', 'docs/upstream/filename-list.txt', 'docs/contributing.md', 'CHANGELOG.md', 'package.json')]
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for file in files:
            entry = zipfile.ZipInfo(f'fatcow-{version}/{file.relative_to(ROOT).as_posix()}', (2000, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, file.read_bytes())
    print(f'Created {destination.relative_to(ROOT)}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', action='store_true')
    args = parser.parse_args()
    build()
    if args.archive:
        archive()
