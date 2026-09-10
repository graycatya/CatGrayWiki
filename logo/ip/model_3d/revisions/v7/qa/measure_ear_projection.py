"""Measure visible ear area at the same front projection used by the references."""
import bpy
import json
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent.parent
results = {}
for label, path in [('v3', OUT/'revisions/v3/CatGray_IP.blend'),
                    ('v4', OUT/'revisions/v4/CatGray_IP.blend'),
                    ('v5', OUT/'CatGray_IP.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    collection = bpy.data.collections['CATGRAY • Character']
    objects = [o for o in collection.objects if o.name.startswith(('Head ', 'Ear '))]
    head = next(o for o in objects if o.name.startswith('Head '))
    dz = head.location.z
    depsgraph = bpy.context.evaluated_depsgraph_get()
    vertices, triangles, labels = [], [], []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in mesh.vertices)
        for tri in mesh.loop_triangles:
            triangles.append(tuple(offset+i for i in tri.vertices))
            mat = mesh.materials[tri.material_index]
            labels.append('pink' if 'Inner ears' in mat.name else
                          'ear' if obj.name.startswith('Ear ') else 'head')
        evaluated.to_mesh_clear()
    tree = BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
    counts = {'pink': 0, 'ear': 0, 'head': 0}
    xs, zs = np.linspace(.65, 1.95, 221), np.linspace(3.20, 4.42, 221)
    pink_xz = []
    for x in xs:
        for z in zs:
            hit, normal, index, distance = tree.ray_cast(Vector((x, -5, z+dz)), Vector((0, 1, 0)), 10)
            if hit is not None:
                tag = labels[index]; counts[tag] += 1
                if tag == 'pink': pink_xz.append((float(x), float(z)))
    pixel_area = float((xs[1]-xs[0])*(zs[1]-zs[0]))
    results[label] = {'projected_pink_area': counts['pink']*pixel_area,
                      'projected_visible_ear_area': (counts['pink']+counts['ear'])*pixel_area,
                      'visible_pink_fraction': counts['pink']/max(1, counts['pink']+counts['ear']),
                      'pink_bounds_xz': [min(v[0] for v in pink_xz), min(v[1] for v in pink_xz),
                                         max(v[0] for v in pink_xz), max(v[1] for v in pink_xz)]}

image = bpy.data.images.load(str(OUT.parent/'正视.png'), check_existing=False)
width, height = image.size
pixels = np.empty(width*height*4, dtype=np.float32)
image.pixels.foreach_get(pixels)
pixels = pixels.reshape(height, width, 4)[::-1]
crop = pixels[:180, width//2:]
mask = np.max(np.abs(crop[:,:,:3]-np.array([1,163/255,163/255])), axis=2) < .015
results['front_reference'] = {'pink_pixels_right_ear': int(mask.sum()),
                              'pink_area_at_100_pixels_per_unit': float(mask.sum()/10000)}
(OUT/'qa/ear_projection_measurements.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2), flush=True)
