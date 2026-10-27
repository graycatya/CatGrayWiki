"""Bake every original GLB clip into vector Lottie paths at 24 fps.

Requires numpy and shapely. Set CATGRAY_LOTTIE_DEPS to an optional package folder.
No bitmap tracing: mesh planes are merged before orthographic projection.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import zipfile

if os.environ.get('CATGRAY_LOTTIE_DEPS'):
    sys.path.insert(0, os.environ['CATGRAY_LOTTIE_DEPS'])
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union

from export_lottie import OUT, ROOT, transform


def matrix(t, q, s):
    x, y, z, w = q / np.linalg.norm(q)
    r = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    m = np.eye(4)
    m[:3, :3] = r * s
    m[:3, 3] = t
    return m


class Model:
    def __init__(self):
        data = (ROOT / 'CatGray_Voxel.glb').read_bytes()
        length = struct.unpack_from('<I', data, 12)[0]
        self.g = json.loads(data[20:20+length])
        self.binary = data[28+length:]
        self.cache = {}
        self.accessors = {}
        self.parents = {child: i for i, n in enumerate(self.g['nodes']) for child in n.get('children', [])}
        self.skin = self.g['skins'][0]
        self.bind = self.access(self.skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
        self.primitives = []
        for ni, node in enumerate(self.g['nodes']):
            if 'mesh' not in node:
                continue
            for primitive in self.g['meshes'][node['mesh']]['primitives']:
                attr = primitive['attributes']
                self.primitives.append((ni, primitive, self.access(attr['POSITION']),
                                        self.access(primitive['indices']).astype(int).reshape(-1, 3),
                                        self.access(attr['NORMAL']), self.access(attr['JOINTS_0'])[:, 0]))

    def access(self, index):
        if index in self.accessors:
            return self.accessors[index]
        a = self.g['accessors'][index]
        dtype = {5126:'<f4', 5125:'<u4', 5123:'<u2', 5121:'u1', 5122:'<i2'}[a['componentType']]
        width = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4, 'MAT4':16}[a['type']]
        item = np.dtype(dtype).itemsize
        array = np.zeros((a['count'], width))
        if 'bufferView' in a:
            b = self.g['bufferViews'][a['bufferView']]
            offset = a.get('byteOffset', 0)+b.get('byteOffset', 0)
            array = np.ndarray((a['count'], width), dtype=dtype, buffer=self.binary,
                               offset=offset, strides=(b.get('byteStride', width*item), item)).astype(float)
        if 'sparse' in a:
            sparse = a['sparse']
            ix, val = sparse['indices'], sparse['values']
            ib, vb = self.g['bufferViews'][ix['bufferView']], self.g['bufferViews'][val['bufferView']]
            idtype = {5121:'u1',5123:'<u2',5125:'<u4'}[ix['componentType']]
            indices = np.frombuffer(self.binary, dtype=idtype, count=sparse['count'],
                                    offset=ib.get('byteOffset',0)+ix.get('byteOffset',0))
            values = np.frombuffer(self.binary, dtype=dtype, count=sparse['count']*width,
                                   offset=vb.get('byteOffset',0)+val.get('byteOffset',0)).reshape(-1,width)
            array[indices] = values
        if width == 1:
            array = array[:, 0]
        self.accessors[index] = array
        return array

    def sample(self, animation, time):
        nodes = self.g['nodes']
        values = {i: {p: np.array(n.get(p, default), dtype=float) for p, default in
                      [('translation', [0, 0, 0]), ('rotation', [0, 0, 0, 1]), ('scale', [1, 1, 1])]}
                  for i, n in enumerate(nodes)}
        weights = {}
        for channel in animation['channels']:
            node, path = channel['target']['node'], channel['target']['path']
            sampler = animation['samplers'][channel['sampler']]
            times = self.access(sampler['input'])
            output = self.access(sampler['output']).reshape(len(times), -1)
            left = max(0, min(len(times)-1, int(np.searchsorted(times, time+1e-7, side='right')-1)))
            right = min(left+1, len(times)-1)
            f = 0 if sampler['interpolation'] == 'STEP' or left == right else (time-times[left])/(times[right]-times[left])
            a, b = output[left], output[right]
            if path == 'rotation':
                if a.dot(b) < 0:
                    b = -b
                dot = np.clip(a.dot(b), -1, 1)
                angle = math.acos(dot)
                v = ((1-f)*a+f*b if angle < 1e-5 else
                     (math.sin((1-f)*angle)*a+math.sin(f*angle)*b)/math.sin(angle))
            else:
                v = a+(b-a)*f
            if path == 'weights':
                weights[node] = v
            else:
                values[node][path] = v
        world = {}
        def visit(i):
            if i not in world:
                v = values[i]
                local = matrix(v['translation'], v['rotation'], v['scale'])
                world[i] = visit(self.parents[i]) @ local if i in self.parents else local
            return world[i]
        skins = np.array([visit(i) @ inverse for i, inverse in zip(self.skin['joints'], self.bind)])
        return skins, weights

    def geometry(self, weights, head_only):
        key = (head_only, tuple((i, tuple(np.round(w, 4))) for i, w in sorted(weights.items())))
        if key in self.cache:
            return self.cache[key]
        result = []
        for ni, p, base, triangles, normals, joints in self.primitives:
            if head_only and self.g['nodes'][ni]['name'] not in ('Voxel_Head', 'Voxel_Ear.L', 'Voxel_Ear.R', 'Voxel_Face'):
                continue
            positions = base.copy()
            if 'targets' in p:
                w = weights.get(ni, self.g['meshes'][self.g['nodes'][ni]['mesh']]['weights'])
                moved = np.zeros(len(positions), dtype=bool)
                for weight, target in zip(w, p['targets']):
                    if weight > .5 and 'POSITION' in target:
                        delta = self.access(target['POSITION'])
                        moved |= np.linalg.norm(delta, axis=1) > .1
                        positions += weight*delta
                triangles = triangles[moved[triangles].all(axis=1)]
            groups = {}
            for ids in triangles.astype(int):
                normal = normals[ids[0]]
                axis = int(np.argmax(abs(normal)))
                axes = [i for i in range(3) if i != axis]
                pts = positions[ids]
                plane = round(float(pts[0, axis]), 5)
                group = (int(joints[ids[0]]), axis, int(np.sign(normal[axis])), plane)
                polygon = Polygon(pts[:, axes])
                if polygon.area > 1e-10:
                    groups.setdefault(group, []).append(polygon)
            material = self.g['materials'][p.get('material', 0)]['pbrMetallicRoughness'].get('baseColorFactor', [1,1,1,1])[:3]
            # glTF stores linear colors; Lottie fills use display RGB.
            rgb = np.array([12.92*c if c <= .0031308 else 1.055*c**(1/2.4)-.055 for c in material])
            for (joint, axis, sign, plane), polygons in groups.items():
                merged = unary_union(polygons).simplify(.00001, preserve_topology=True)
                pieces = [merged] if merged.geom_type == 'Polygon' else list(merged.geoms)
                normal = np.zeros(3)
                normal[axis] = sign
                axes = [i for i in range(3) if i != axis]
                for piece in pieces:
                    if piece.geom_type != 'Polygon' or piece.area < 1e-9:
                        continue
                    rings = []
                    for ring in [piece.exterior, *piece.interiors]:
                        coords = np.array(ring.coords)[:-1]
                        points = np.full((len(coords), 4), 1.)
                        points[:, axis] = plane
                        points[:, axes] = coords
                        rings.append(points)
                    result.append((joint, normal, rgb, rings))
        self.cache[key] = result
        return result


def front_half_plane(delta, bounds):
    """Clip a bounding rectangle to dx*x + dy*y + dc >= 0."""
    x0, y0, x1, y1 = bounds
    corners = [(x0-1, y0-1), (x1+1, y0-1), (x1+1, y1+1), (x0-1, y1+1)]
    result = []
    for a, b in zip(corners, corners[1:]+corners[:1]):
        da, db = np.dot(delta, [*a, 1]), np.dot(delta, [*b, 1])
        if da >= 0:
            result.append(a)
        if (da >= 0) != (db >= 0):
            f = da/(da-db)
            result.append((a[0]+f*(b[0]-a[0]), a[1]+f*(b[1]-a[1])))
    return Polygon(result) if len(result) >= 3 else Polygon()


def occlusion_cuts(polygons, planes):
    """Use affine depth over the entire overlap, including intersecting planes."""
    pairs = shapely.STRtree(polygons).query(polygons, predicate='intersects')
    pairs = pairs[:, pairs[0] < pairs[1]]
    intersections = shapely.intersection(polygons[pairs[0]], polygons[pairs[1]])
    keep = shapely.area(intersections) > .00001
    pairs, intersections = pairs[:, keep], intersections[keep]
    cuts = {}
    for (a, b), overlap in zip(pairs.T, intersections):
        delta = planes[a]-planes[b]
        coords = shapely.get_coordinates(overlap)
        depths = coords @ delta[:2]+delta[2]
        lo, hi = depths.min(), depths.max()
        if max(abs(lo), abs(hi)) < .000001:
            continue  # Coplanar faces do not occlude one another.
        if lo >= 0:
            cuts.setdefault(b, []).append(overlap)
        elif hi <= 0:
            cuts.setdefault(a, []).append(overlap)
        else:
            # Each face is in front on one side of the depth equality line.
            front_a = overlap.intersection(front_half_plane(delta, overlap.bounds))
            front_b = overlap.difference(front_a)
            cuts.setdefault(b, []).append(front_a)
            cuts.setdefault(a, []).append(front_b)
    return cuts


def projected(model, animation, frame, head_only):
    skins, weights = model.sample(animation, frame/24)
    camera = np.array([.34, .14, 1.] if not head_only else [0., .08, 1.])
    camera /= np.linalg.norm(camera)
    right = np.cross([0, 1, 0], camera)
    right /= np.linalg.norm(right)
    up = np.cross(camera, right)
    scale = 73 if not head_only else 111
    center = np.array([0, 2.75, 0] if not head_only else [0, 3.2, 0])
    light = np.array([-.35, .65, 1.])
    light /= np.linalg.norm(light)
    faces = []
    depth_planes = []
    for joint, normal, rgb, rings in model.geometry(weights, head_only):
        transform = skins[joint]
        n = transform[:3, :3] @ normal
        if n.dot(camera) <= .00001:
            continue
        transformed = [r @ transform.T for r in rings]
        depth = transformed[0][:, :3].mean(axis=0).dot(camera)
        shade = .74+.26*max(0, n.dot(light))
        paths = []
        for pts in transformed:
            relative = pts[:, :3]-center
            xy = np.column_stack((256+relative @ right*scale, 256-relative @ up*scale))
            paths.append(xy.tolist())
        color = np.round(rgb*shade, 4).tolist()
        faces.append((depth, color, paths))
        # Exact affine depth at every projected point of this plane.
        denominator = n.dot(camera)
        dx = -n.dot(right)/scale/denominator
        dy = n.dot(up)/scale/denominator
        dc = n.dot(transformed[0][0, :3]-center)/denominator-256*dx-256*dy
        depth_planes.append([dx, dy, dc])
    # Use a shared precision grid during Boolean operations. Near-coincident
    # voxel edges otherwise produce unstable slivers and even whole-face holes.
    polygons = shapely.set_precision(
        np.array([Polygon(rings[0], rings[1:]) for _,_,rings in faces], dtype=object), .00001)
    # Clip each plane by overlapping planes that are closer to the camera.
    # Merged faces cannot be sorted correctly by a single centroid depth.
    cuts = occlusion_cuts(polygons, np.array(depth_planes))
    by_color = {}
    for i, (_, color, _) in enumerate(faces):
        visible = polygons[i].difference(unary_union(cuts[i])) if i in cuts else polygons[i]
        if not visible.is_empty:
            by_color.setdefault(tuple(color), []).append(visible)
    visible_faces = []
    for color, pieces in by_color.items():
        merged = unary_union(pieces).simplify(.00001, preserve_topology=True)
        parts = shapely.get_parts(merged)
        for part in parts:
            if part.geom_type == 'Polygon' and part.area > .005:
                # Keep precision until after clipping to avoid intersecting rounding slivers.
                part = shapely.geometry.polygon.orient(part, sign=-1)
                rings = [np.round(np.array(r.coords)[:-1], 5).tolist()
                         for r in [part.exterior, *part.interiors]]
                visible_faces.append((0, list(color), rings))
    return visible_faces


def shapes_for(faces):
    groups = []
    last = None
    shapes = []
    def close_group(color):
        if shapes:
            groups.append({'ty': 'gr', 'it': shapes+[
                {'ty': 'fl', 'c': {'a': 0, 'k': color}, 'o': {'a': 0, 'k': 100}, 'r': 1},
                {'ty': 'tr', **transform()}]})
    for _, color, paths in faces:
        if last != color:
            close_group(last)
            shapes = []
            last = color
        for points in paths:
            shapes.append({'ty': 'sh', 'ks': {'a': 0, 'k': {
                'i': [[0, 0]]*len(points), 'o': [[0, 0]]*len(points), 'v': points, 'c': True}}})
    close_group(last)
    return groups


def base(name, frames):
    return {'v': '5.12.2', 'fr': 24, 'ip': 0, 'op': frames, 'w': 512, 'h': 512,
            'nm': name, 'ddd': 0, 'assets': [], 'layers': [], 'markers': []}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def write_preview(path, animation, title):
    player = (OUT / 'lottie.min.js').read_text(encoding='utf-8')
    data = json.dumps(animation, ensure_ascii=False, separators=(',', ':'))
    path.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'''+title+'''</title>
<style>body{margin:0;background:#20242a;color:#eee;font:15px system-ui;text-align:center}h2{margin:12px}#a{width:min(80vh,92vw,512px);aspect-ratio:1;margin:auto;background:repeating-conic-gradient(#30363e 0% 25%,#292e35 0% 50%) 0/32px 32px;border-radius:18px}button,input{margin:10px}input{width:220px}p{margin:8px;color:#aeb8c3}</style>
<h2>'''+title+'''</h2><p>纯矢量 · 透明背景 · 512 × 512 · 24 FPS</p><div id="a"></div><button onclick="anim.togglePause()">播放 / 暂停</button><button onclick="anim.goToAndPlay(0,true)">重播</button><br><input id="seek" type="range" min="0" max="'''+str(animation['op']-1)+'''" value="0" oninput="anim.goToAndStop(+this.value,true)"><span id="frame"></span><script>'''+player+'''</script><script>
var anim=lottie.loadAnimation({container:document.getElementById('a'),renderer:'svg',loop:true,autoplay:true,animationData:'''+data+'''});
anim.addEventListener('enterFrame',()=>{document.getElementById('seek').value=anim.currentFrame;document.getElementById('frame').textContent=Math.floor(anim.currentFrame)+' / '+anim.totalFrames;});
anim.addEventListener('DOMLoaded',()=>{document.body.dataset.ready='true';const params=new URLSearchParams(location.search);const f=params.get('frame');if(f!==null)anim.goToAndStop(+f,true);if(params.has('qa')){anim.pause();const result={ready:true,totalFrames:anim.totalFrames,frame:anim.currentFrame,paths:document.querySelectorAll('#a svg path').length,images:document.querySelectorAll('#a svg image').length};document.body.textContent=JSON.stringify(result);}});
</script></html>''', encoding='utf-8')


def svg_for(faces):
    paths = []
    for _, color, rings in faces:
        fill = '#'+''.join(f'{max(0,min(255,round(c*255))):02x}' for c in color)
        d = ' '.join('M'+' L'.join(f'{x},{y}' for x,y in ring)+'Z' for ring in rings)
        paths.append(f'<path fill="{fill}" d="{d}"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'+''.join(paths)+'</svg>'


def main():
    dest = OUT / 'all_actions'
    dest.mkdir(exist_ok=True)
    model = Model()
    metadata = json.loads((ROOT / 'model_info.json').read_text(encoding='utf-8'))
    clips = metadata['rig']['clips']
    animations = {a['name']: a for a in model.g['animations']}
    combined = base('CatGray All Actions', sum(c['frames']*c['repeat'] for c in clips))
    manifest = []
    start = 0
    for clip in clips:
        name, count = clip['name'], clip['frames']
        head_only = clip['group'] != 'body'
        animation = base(name, count)
        frame_assets = {}
        visible_counts = []
        bounds = []
        for frame in range(count):
            faces = projected(model, animations[name], frame, head_only)
            visible_counts.append(len(faces))
            coords = [p for _,_,rings in faces for ring in rings for p in ring]
            bounds.append([min(p[0] for p in coords), min(p[1] for p in coords),
                           max(p[0] for p in coords), max(p[1] for p in coords)])
            shapes = shapes_for(faces)
            digest = hashlib.sha256(json.dumps(shapes, separators=(',', ':')).encode()).hexdigest()
            if digest not in frame_assets:
                ref = name+'_frame_'+str(len(frame_assets))
                layer = {'ddd': 0, 'ind': 1, 'ty': 4, 'nm': ref, 'sr': 1, 'ks': transform(),
                         'ao': 0, 'ip': 0, 'op': count, 'st': 0, 'bm': 0, 'shapes': shapes}
                asset = {'id': ref, 'w': 512, 'h': 512, 'layers': [layer]}
                frame_assets[digest] = ref
                animation['assets'].append(asset)
            animation['layers'].append({'ddd': 0, 'ind': frame+1, 'ty': 0, 'nm': f'{name} frame {frame}',
                'refId': frame_assets[digest], 'w': 512, 'h': 512,
                'sr': 1, 'ks': transform(), 'ao': 0, 'ip': frame, 'op': frame+1, 'st': 0, 'bm': 0})
            if frame == min(count-1, clip['poster']-1):
                (dest / f'{name}.svg').write_text(svg_for(faces), encoding='utf-8')
        path = dest / f'{name}.json'
        write_json(path, animation)
        write_preview(dest / f'{name}.html', animation, clip['label']+' · '+name)
        combined['assets'].append({'id': name, 'w': 512, 'h': 512, 'layers': animation['layers']})
        combined['assets'].extend(animation['assets'])
        for repeat in range(clip['repeat']):
            a = start+repeat*count
            combined['layers'].append({'ddd': 0, 'ind': len(combined['layers'])+1, 'ty': 0,
                'nm': name, 'refId': name, 'sr': 1, 'ks': transform(), 'ao': 0,
                'w': 512, 'h': 512, 'ip': a, 'op': a+count, 'st': a, 'bm': 0})
        combined['markers'].append({'tm': start, 'cm': clip['label']+' / '+name, 'dr': count*clip['repeat']})
        start += count*clip['repeat']
        entry = dict(clip, file=path.name, bytes=path.stat().st_size, view='head' if head_only else 'body',
                     visible_polygons=[min(visible_counts), max(visible_counts)],
                     bounds=[min(b[0] for b in bounds), min(b[1] for b in bounds),
                             max(b[2] for b in bounds), max(b[3] for b in bounds)])
        assert all(0 <= v <= 512 for v in entry['bounds']), (name, entry['bounds'])
        manifest.append(entry)
        print(f'{name}: {count} frames, {path.stat().st_size/1024/1024:.2f} MB, polygons {entry["visible_polygons"]}', flush=True)
    write_json(dest / 'CatGray_All_Actions.json', combined)
    write_preview(dest / 'CatGray_All_Actions.html', combined, 'CatGray · 全部动作串联')
    write_json(dest / 'manifest.json', {'fps': 24, 'size': [512,512], 'source': '../../CatGray_Voxel.glb',
        'method': 'Rigid skinning and STEP morph animation sampled into orthographic vector paths',
        'combined_frames': combined['op'], 'clips': manifest})
    items = '<button onclick="openClip(\'CatGray_All_Actions\',this)">全部串联</button>'
    items += ''.join(f'<button onclick="openClip(\'{c["name"]}\',this)">{c["label"]}</button>' for c in clips)
    (OUT / 'preview.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>CatGray 全部矢量动画</title><style>body{margin:0;background:#171c22;color:#eee;font:16px system-ui;text-align:center}header{padding:20px}h1{margin:0 0 10px}p{color:#aeb8c3}nav{max-width:950px;margin:0 auto 14px}button{background:#303b47;color:white;border:1px solid #4a5d70;border-radius:8px;padding:10px 17px;margin:5px;cursor:pointer}.active{background:#895b11;border-color:#ffc451}iframe{border:0;width:100%;height:740px}a{color:#ffc451}</style><header><h1>CatGray · 全部矢量动画</h1><p>12 个独立动作 + 35.5 秒串联 · 透明背景 · 24 FPS</p><nav>'''+items+'''</nav><a id="download" href="all_actions/Walk_InPlace.json" download>下载当前 JSON</a></header><iframe id="viewer" src="all_actions/Walk_InPlace.html" title="动画预览"></iframe><script>function openClip(name,button){document.querySelectorAll('button').forEach(b=>b.classList.remove('active'));button.classList.add('active');document.getElementById('viewer').src='all_actions/'+name+'.html';document.getElementById('download').href='all_actions/'+name+'.json';}document.querySelectorAll('nav button')[1].classList.add('active');</script></html>''', encoding='utf-8')
    with zipfile.ZipFile(OUT / 'CatGray_All_Vector_Lottie.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in [OUT/'preview.html', OUT/'LOTTIE-LICENSE.md', OUT/'README.md', *dest.glob('*.json'), *dest.glob('*.html'), *dest.glob('*.svg')]:
            if path.name.startswith('qa-'):
                continue
            if path.is_file():
                archive.write(path, path.relative_to(OUT))
    print('Exported 12 clips, combined animation, offline previews and ZIP.', flush=True)


if __name__ == '__main__':
    main()
