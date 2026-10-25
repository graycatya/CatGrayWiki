"""Export a front orthographic, vector-only head from the existing VOX source.

Uses the original facial pixel functions without importing Blender. No tracing,
bitmap assets, third-party Python modules, or changes to the 3D files.
"""
import ast
import json
import math
from pathlib import Path

from voxel_model import (ROOT, HEAD, face_color, read_vox, settings,
                         in_loft, profile_at, triangle_contains)

OUT = ROOT / 'lottie'
SCALE = 112
FPS = 24
END = 120


def facial_functions():
    tree = ast.parse((ROOT / 'scripts/facial_voxel.py').read_text(encoding='utf-8'))
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in ('eye_pixel', 'mouth_pixel')]
    scope = {'math': math, 'face_color': face_color}
    exec(compile(tree, 'facial_voxel.py', 'exec'), scope)
    return scope['eye_pixel'], scope['mouth_pixel']


def transform():
    return {'o': {'a': 0, 'k': 100}, 'r': {'a': 0, 'k': 0},
            'p': {'a': 0, 'k': [0, 0, 0]}, 'a': {'a': 0, 'k': [0, 0, 0]},
            's': {'a': 0, 'k': [100, 100, 100]}}


def rectangles(pixels):
    """Merge equal-color horizontal runs, keeping exact voxel silhouettes."""
    runs = []
    for k in sorted({k for i, k in pixels}):
        row = sorted(i for i, z in pixels if z == k)
        start = prev = row[0]
        color = pixels[start, k]
        for i in row[1:] + [10000]:
            if i != prev + 1 or pixels.get((i, k)) != color:
                x = 256 + start * .1 * SCALE
                y = 256 - ((k + 1) * .1 - 3.2) * SCALE
                runs.append((color, x, y, (prev + 1 - start) * .1 * SCALE, .1 * SCALE))
                if i == 10000:
                    break
                start, color = i, pixels[i, k]
            prev = i
    return runs


def layers_for(runs, palette):
    layers = []
    for color in sorted({r[0] for r in runs}):
        shapes = []
        for c, x, y, w, h in runs:
            if c != color:
                continue
            vertices = [[round(x, 4), round(y, 4)], [round(x+w, 4), round(y, 4)],
                        [round(x+w, 4), round(y+h, 4)], [round(x, 4), round(y+h, 4)]]
            shapes.append({'ty': 'sh', 'ks': {'a': 0, 'k': {
                'i': [[0, 0]]*4, 'o': [[0, 0]]*4, 'v': vertices, 'c': True}}})
        shapes.append({'ty': 'fl', 'c': {'a': 0, 'k': [v/255 for v in palette[color-1][:3]]},
                       'o': {'a': 0, 'k': 100}, 'r': 1})
        layers.append({'ddd': 0, 'ind': color, 'ty': 4, 'nm': f'Palette {color}',
                       'sr': 1, 'ks': transform(), 'ao': 0, 'shapes': shapes,
                       'ip': 0, 'op': END, 'st': 0, 'bm': 0})
    return layers


def main():
    OUT.mkdir(exist_ok=True)
    config = settings()
    info = json.loads((ROOT / 'model_info.json').read_text(encoding='utf-8'))
    _, voxels, palette = read_vox(ROOT / 'CatGray_Voxel.vox')
    offset = info['grid_minimum']
    front = {}
    for p, color in voxels.items():
        i, j, k = (p[a]+offset[a] for a in range(3))
        x, y, z = ((v+.5)*.1 for v in (i, j, k))
        ear = (-.12 <= y <= .38 and triangle_contains(
            abs(x), z, (.90, 3.70), (1.83, 3.75), (1.62, 4.76)))
        if not (in_loft(x, y, profile_at(HEAD, z)) or ear):
            continue
        if (i, k) not in front or j < front[i, k][0]:
            front[i, k] = j, color
    eye, mouth = facial_functions()
    states = {'Neutral': ('Open', 'Neutral'), 'Half': ('Half', 'Closed'),
              'Blink': ('Closed', 'Neutral'), 'Joy': ('Joy', 'Joy')}
    assets, previews = [], {}
    for name, (eyes, lips) in states.items():
        pixels = {}
        for (i, k), (j, color) in front.items():
            x, z = (i+.5)*.1, (k+.5)*.1
            # Remove the source's static eyes/mouth, retain the fixed nose.
            if (face_color(x, z) is not None and z < 2.65) or (
                    any(math.hypot(x-cx, z-3) <= .455 for cx in (-.8, .8))):
                color = 1
            color = eye(eyes, x, z) or mouth(lips, x, z) or color
            pixels[i, k] = color
        runs = rectangles(pixels)
        assets.append({'id': name, 'w': 512, 'h': 512, 'layers': layers_for(runs, palette)})
        previews[name] = runs
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">']
        for c, x, y, w, h in runs:
            svg.append(f'<path fill="#{config["palette"][c-1]["hex"]}" d="M{x} {y}h{w}v{h}h{-w}z"/>')
        (OUT / f'{name}.svg').write_text(''.join(svg)+'</svg>', encoding='utf-8')
    timeline = [(0, 24, 'Neutral'), (24, 26, 'Half'), (26, 29, 'Blink'),
                (29, 31, 'Half'), (31, 48, 'Neutral'), (48, 52, 'Half'),
                (52, 96, 'Joy'), (96, 100, 'Half'), (100, END, 'Neutral')]
    animation = {'v': '5.12.2', 'fr': FPS, 'ip': 0, 'op': END, 'w': 512, 'h': 512,
                 'nm': 'CatGray Head — Blink and Joy', 'ddd': 0, 'assets': assets,
                 'layers': [{'ddd': 0, 'ind': n+1, 'ty': 0, 'nm': name, 'refId': name,
                             'sr': 1, 'ks': transform(), 'ao': 0, 'w': 512, 'h': 512,
                             'ip': a, 'op': b, 'st': 0, 'bm': 0}
                            for n, (a, b, name) in enumerate(timeline)],
                 'markers': [{'tm': 0, 'cm': 'Neutral', 'dr': 24},
                             {'tm': 24, 'cm': 'Blink', 'dr': 7},
                             {'tm': 52, 'cm': 'Joy', 'dr': 44}]}
    path = OUT / 'CatGray_Head_Blink_Joy.json'
    path.write_text(json.dumps(animation, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    # Offline, single-file preview. The player itself is vendored beside this file.
    player = (OUT / 'lottie.min.js').read_text(encoding='utf-8')
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>CatGray 矢量 Lottie</title>
<style>body{margin:0;background:#20242a;color:#eee;font:16px system-ui;text-align:center}main{max-width:640px;margin:40px auto}#animation{width:min(90vw,512px);height:min(90vw,512px);margin:auto;background:repeating-conic-gradient(#30363e 0% 25%,#292e35 0% 50%) 0/32px 32px;border-radius:24px}button{margin:20px 6px;padding:10px 22px;cursor:pointer}p{color:#abb4bf}</style>
<main><h1>CatGray · 头部表情</h1><p>默认 → 眨眼 → 开心 → 默认 · 5 秒 · 24 FPS · 纯矢量 · 透明背景</p><div id="animation"></div><button onclick="anim.togglePause()">播放 / 暂停</button><button onclick="anim.goToAndPlay(0,true)">重新播放</button></main><script>'''
    html += player + '</script><script>const anim=lottie.loadAnimation({container:document.getElementById("animation"),renderer:"svg",loop:true,autoplay:true,animationData:'
    html += json.dumps(animation, ensure_ascii=False) + '});</script></html>'
    (OUT / 'preview.html').write_text(html, encoding='utf-8')
    from PIL import Image, ImageDraw
    sheet = Image.new('RGB', (1024, 512), '#e8eaed')
    draw = ImageDraw.Draw(sheet)
    for n, (name, runs) in enumerate(previews.items()):
        ox, oy = n % 2 * 512, n // 2 * 256
        draw.text((ox+16, oy+12), name, fill='#292928')
        for c, x, y, w, h in runs:
            draw.rectangle((ox+x*.5+128, oy+y*.5, ox+(x+w)*.5+128, oy+(y+h)*.5), fill=tuple(palette[c-1][:3]))
    sheet.save(OUT / 'states.png')
    print(f'Exported {path.name}: {path.stat().st_size:,} bytes; {len(front)} front cells; {len(assets)} vector states')


if __name__ == '__main__':
    main()
