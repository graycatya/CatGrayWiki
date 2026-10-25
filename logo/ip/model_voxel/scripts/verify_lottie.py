"""Verify all vector assets and render representative frames using local Chrome."""
import concurrent.futures
import json
from pathlib import Path
import re
import subprocess

from export_lottie import OUT


def inspect(animation):
    assets = {a['id']: a for a in animation['assets']}
    assert len(assets) == len(animation['assets'])
    def layers(items, end):
        for layer in items:
            assert layer['ty'] in (0, 4)
            assert 0 <= layer['ip'] < layer['op'] <= end
            if layer['ty'] == 0:
                assert layer['refId'] in assets
            else:
                assert layer['shapes']
    layers(animation['layers'], animation['op'])
    for asset in assets.values():
        assert 'p' not in asset and 'u' not in asset
        layers(asset['layers'], animation['op'])
    spans = sorted((l['ip'], l['op']) for l in animation['layers'])
    assert spans[0][0] == 0 and spans[-1][1] == animation['op']
    assert all(a[1] == b[0] for a,b in zip(spans, spans[1:]))
    return len(assets)


def main():
    dest = OUT / 'all_actions'
    qa = OUT / 'qa_all_actions'
    qa.mkdir(exist_ok=True)
    manifest = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
    chrome = Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
    report = {'clips': [], 'browser': str(chrome)}
    def check(clip):
        name = clip['name']
        animation = json.loads((dest / f'{name}.json').read_text(encoding='utf-8'))
        asset_count = inspect(animation)
        common = [str(chrome), '--headless', '--disable-gpu', '--no-sandbox',
                  '--allow-file-access-from-files', '--virtual-time-budget=2500', '--window-size=700,780']
        uri = (dest / f'{name}.html').as_uri()
        result = subprocess.run(common+['--dump-dom', uri+f'?frame={clip["frames"]-1}&qa=1'],
                                capture_output=True, timeout=90)
        html = result.stdout.decode('utf-8', errors='replace')
        match = re.search(r'<body[^>]*>(\{.*?\})</body>', html, re.S)
        assert result.returncode == 0 and match, (name, html[-1000:])
        state = json.loads(match[1])
        assert state['ready'] and state['totalFrames'] == clip['frames']
        assert state['frame'] == clip['frames']-1 and state['paths'] > 0 and state['images'] == 0
        screenshot = qa / f'{name}.png'
        shot = subprocess.run(common+['--screenshot='+str(screenshot),
                              uri+f'?frame={clip["poster"]-1}'], capture_output=True, timeout=90)
        assert shot.returncode == 0 and screenshot.exists()
        return {'name': name, 'assets': asset_count, 'bytes': (dest/f'{name}.json').stat().st_size,
                'browser_state': state, 'screenshot': screenshot.name}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(check, manifest['clips']):
            report['clips'].append(result)
            print(result['name']+' verified', flush=True)
    combined = json.loads((dest / 'CatGray_All_Actions.json').read_text(encoding='utf-8'))
    inspect(combined)
    assert combined['op'] == 852 and len(combined['markers']) == 12
    uri = (dest / 'CatGray_All_Actions.html').as_uri()+'?frame=851&qa=1'
    result = subprocess.run([str(chrome), '--headless', '--disable-gpu', '--no-sandbox',
                             '--allow-file-access-from-files', '--virtual-time-budget=4000', '--dump-dom', uri],
                            capture_output=True, timeout=120)
    html = result.stdout.decode('utf-8', errors='replace')
    match = re.search(r'<body[^>]*>(\{.*?\})</body>', html, re.S)
    assert result.returncode == 0 and match
    report['combined'] = json.loads(match[1])
    assert report['combined']['totalFrames'] == 852 and report['combined']['frame'] == 851
    assert report['combined']['paths'] > 0 and report['combined']['images'] == 0
    from PIL import Image, ImageDraw
    sheet = Image.new('RGB', (1400, 4*390), '#20242a')
    for i, clip in enumerate(manifest['clips']):
        with Image.open(qa / f'{clip["name"]}.png') as img:
            img.thumbnail((350,390))
            sheet.paste(img, ((i%4)*350,(i//4)*390))
    sheet = sheet.crop((0,0,1400,1170))
    sheet.save(qa / 'all_actions.png')
    (qa / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('All 12 clips and 852-frame combined animation verified.', flush=True)


if __name__ == '__main__':
    main()
