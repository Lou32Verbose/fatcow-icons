"""Verify all source bytes, manifest entries, sprite pixels and CSS coordinates."""
import hashlib
import json
import re
from PIL import Image
from build import ROOT, VARIANTS

def verify():
    dist = ROOT / 'dist'
    manifest = json.loads((dist / 'icons.json').read_text(encoding='utf-8'))
    assert set(manifest['variants']) == set(VARIANTS)
    total = 0
    for variant, size in VARIANTS.items():
        group = manifest['variants'][variant]
        icons = group['icons']
        sources = {p.name for p in (ROOT / 'src' / variant).glob('*.png')}
        assert group['count'] == len(icons) == len(sources)
        assert {i['name'] + '.png' for i in icons} == sources
        assert {p.name for p in (dist / variant / 'png').glob('*')} == sources
        css = (dist / variant / 'sprite/fatcow.css').read_text(encoding='utf-8')
        compact = (dist / variant / 'sprite/fatcow.min.css').read_text(encoding='utf-8')
        assert compact == re.sub(r'\s*([{}:;])\s*', r'\1', css).strip() + '\n'
        with Image.open(dist / variant / 'sprite/fatcow.png') as sheet:
            for icon in icons:
                assert icon['source'] == f'src/{variant}/{icon["name"]}.png'
                source = ROOT / icon['source']
                data = source.read_bytes()
                assert data == (dist / icon['png']).read_bytes(), source
                assert hashlib.sha256(data).hexdigest() == icon['sha256'], source
                expected_size = 32 if size == 16 and icon['name'] == 'file_extension_png' else size
                assert (icon['width'], icon['height']) == (expected_size, expected_size)
                x, y = icon['x'], icon['y']
                with Image.open(source) as original:
                    assert original.size == (expected_size, expected_size)
                    assert sheet.crop((x, y, x + expected_size, y + expected_size)).tobytes() == original.convert('RGBA').tobytes(), source
                assert f'.fatcow-{variant}.fatcow-{icon["name"]} {{ width: {expected_size}px; height: {expected_size}px; background-position: -{x}px -{y}px; }}' in css
        total += len(icons)
    print(f'Verified {total} PNG copies, hashes, sprite crops, manifest entries and CSS rules')

if __name__ == '__main__':
    verify()
