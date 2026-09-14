"""Independent geometry and painted-surface checks for the unclothed revision.

Run with Blender in background after build_cat.py finishes. Reads the saved
native asset and v2 archive; writes only the JSON report beside this script.
"""
import json
from array import array
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


OUT = Path(__file__).resolve().parent.parent
REPORT = OUT / 'qa/unclothed_revision_verification.json'
bpy.ops.wm.open_mainfile(filepath=str(OUT / 'CatGray_IP.blend'))
character = bpy.data.collections['CATGRAY • Character']
objects = list(character.all_objects)
geometry = [obj for obj in objects if obj.type in {'MESH', 'CURVE'}]
head = next(obj for obj in geometry if obj.name.startswith('Head •'))
body = next(obj for obj in geometry if obj.name.startswith('Body • continuous bare skin'))
report = {'asset': str(OUT / 'CatGray_IP.blend'), 'checks': {}, 'failures': []}


def check(name, passed, details):
    report['checks'][name] = {'passed': bool(passed), **details}
    if not passed:
        report['failures'].append(name)


def mesh_topology(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    remaining = set(bm.verts)
    components = []
    while remaining:
        todo = [remaining.pop()]
        count = 0
        while todo:
            vert = todo.pop()
            count += 1
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                if other in remaining:
                    remaining.remove(other)
                    todo.append(other)
        components.append(count)
    result = {
        'object': obj.name,
        'vertices': len(bm.verts),
        'connected_components': len(components),
        'component_sizes': sorted(components, reverse=True),
        'boundary_edges': sum(edge.is_boundary for edge in bm.edges),
        'nonmanifold_edges': sum(not edge.is_manifold for edge in bm.edges),
        'zero_area_faces': sum(face.calc_area() < 1e-14 for face in bm.faces),
    }
    bm.free()
    return result


class EvaluatedSurface:
    """World-space triangle BVH retaining UV and material indices."""
    def __init__(self, obj):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        self.evaluated = obj.evaluated_get(depsgraph)
        self.mesh = self.evaluated.to_mesh(preserve_all_data_layers=True,
                                           depsgraph=depsgraph)
        self.mesh.calc_loop_triangles()
        self.vertices = [obj.matrix_world @ vert.co for vert in self.mesh.vertices]
        self.triangles = list(self.mesh.loop_triangles)
        self.tree = BVHTree.FromPolygons(
            self.vertices, [tuple(tri.vertices) for tri in self.triangles],
            all_triangles=True)

    def nearest(self, point):
        hit, normal, index, distance = self.tree.find_nearest(point)
        return {'distance': float(distance),
                'signed_distance': float((point-hit).dot(normal))}

    def ray(self, x, z, back=False):
        return self.tree.ray_cast(Vector((x, 5 if back else -5, z)),
                                  Vector((0, -1 if back else 1, 0)), 10)

    def uv(self, point, index, layer_name=None):
        tri = self.triangles[index]
        a, b, c = [self.vertices[i] for i in tri.vertices]
        ab, ac, ap = b-a, c-a, point-a
        d00, d01, d11 = ab.dot(ab), ab.dot(ac), ac.dot(ac)
        d20, d21 = ap.dot(ab), ap.dot(ac)
        denominator = d00*d11-d01*d01
        if abs(denominator) < 1e-20:
            return None
        v = (d11*d20-d01*d21)/denominator
        w = (d00*d21-d01*d20)/denominator
        layer = (self.mesh.uv_layers.get(layer_name) if layer_name
                 else self.mesh.uv_layers.active)
        if layer is None:
            return None
        uvs = [layer.data[i].uv for i in tri.loops]
        return uvs[0]*(1-v-w)+uvs[1]*v+uvs[2]*w

    def close(self):
        self.evaluated.to_mesh_clear()


garment_tokens = ('hood', 'cloth', 'sleeve', 'cuff', 'pocket', 'neckline',
                  'zipper', 'drawstring', 'waistband', 'undershirt')
bad_objects = [obj.name for obj in geometry
               if any(token in obj.name.lower() for token in garment_tokens)]
used_materials = {mat.name for obj in geometry for mat in obj.data.materials if mat}
bad_materials = sorted(name for name in used_materials
                       if any(token in name.lower() for token in garment_tokens))
check('clothing_removed', not bad_objects and not bad_materials,
      {'character_geometry_objects': len(geometry), 'clothing_objects': bad_objects,
       'clothing_materials_used_by_character': bad_materials})

for label, obj in [('head', head), ('body', body)]:
    topology = mesh_topology(obj)
    check(label+'_closed_connected_surface',
          topology['connected_components'] == 1
          and topology['boundary_edges'] == 0
          and topology['nonmanifold_edges'] == 0,
          topology)

head_surface = EvaluatedSurface(head)
nose = next(obj for obj in geometry if obj.name == 'Face • little charcoal nose')
bm = bmesh.new()
bm.from_mesh(nose.data)
edge_indices = {vert.index for edge in bm.edges if edge.is_boundary for vert in edge.verts}
bm.free()
edge_points = [nose.matrix_world @ nose.data.vertices[i].co for i in edge_indices]
edge_distances = [head_surface.nearest(point) for point in edge_points]
all_nose_distances = [head_surface.nearest(nose.matrix_world @ vert.co)
                      for vert in nose.data.vertices]
max_edge_distance = max((item['distance'] for item in edge_distances), default=999)
max_relief = max(item['signed_distance'] for item in all_nose_distances)
check('nose_attached_shallow_relief', bool(edge_points) and max_edge_distance < .006
      and .008 < max_relief < .045,
      {'boundary_vertices': len(edge_points),
       'max_edge_distance': max_edge_distance,
       'mean_edge_distance': sum(item['distance'] for item in edge_distances)/max(1, len(edge_distances)),
       'max_outward_relief': max_relief,
       'edge_distance_tolerance': .006,
       'note': 'The edge may intersect the skin slightly; the centre must remain a shallow raised nose.'})

mouth_details = []
mouth_names = ('Face • philtrum', 'Face • smile L', 'Face • smile R',
               'Face • pink tongue • perimeter')
for name in mouth_names:
    obj = next(obj for obj in geometry if obj.name == name)
    points = []
    for spline in obj.data.splines:
        if spline.type == 'POLY':
            points.extend(obj.matrix_world @ Vector(point.co[:3]) for point in spline.points)
        else:
            points.extend(obj.matrix_world @ point.co for point in spline.bezier_points)
    distances = [head_surface.nearest(point)['distance'] for point in points]
    radius = obj.data.bevel_depth * min(obj.matrix_world.to_scale())
    mouth_details.append({'object': name, 'centre_samples': len(points),
                          'max_centre_to_head_distance': max(distances, default=999),
                          'tube_radius': radius,
                          'all_centres_within_tube_radius': bool(points) and max(distances) < radius})
check('mouth_lines_intersect_skin', all(item['all_centres_within_tube_radius']
                                      for item in mouth_details),
      {'curves': mouth_details})

body_images = []
texture_uv_maps = {}
for material in body.data.materials:
    if material and material.use_nodes:
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                body_images.append(node.image)
                links = node.inputs['Vector'].links
                if links and links[0].from_node.type == 'UVMAP':
                    texture_uv_maps[node.image.name] = links[0].from_node.uv_map
body_images = list(dict.fromkeys(body_images))
belly_geometry = [obj.name for obj in geometry if obj != body
                  and any(token in obj.name.lower() for token in ('belly', 'abdomen', 'tummy'))]
check('belly_is_packed_image_texture', bool(body_images)
      and all(image.packed_file is not None for image in body_images)
      and body.data.uv_layers.active is not None and not belly_geometry,
      {'body_images': [{'name': image.name, 'dimensions': list(image.size),
                        'packed': image.packed_file is not None} for image in body_images],
       'texture_uv_maps': texture_uv_maps,
       'separate_belly_geometry': belly_geometry})

body_surface = EvaluatedSurface(body)
texture = next((image for image in body_images if 'BareBody' in image.name),
               body_images[0] if body_images else None)
if texture is not None:
    pixels = array('f', [0]) * len(texture.pixels)
    texture.pixels.foreach_get(pixels)
    width, height = texture.size

    def sample_surface(x, z, back=False):
        hit, normal, index, distance = body_surface.ray(x, z, back)
        if hit is None:
            return None
        uv = body_surface.uv(hit, index, texture_uv_maps.get(texture.name))
        if uv is None:
            return None
        ix = min(width-1, max(0, int(uv.x*width)))
        iy = min(height-1, max(0, int(uv.y*height)))
        start = 4*(iy*width+ix)
        rgb = tuple(float(pixels[start+i]) for i in range(3))
        return {'rgb': rgb, 'white': min(rgb) > .82 and max(rgb)-min(rgb) < .10}

    samples = {'front': [], 'back': []}
    for iz in range(69):
        z = .15+(float(body.get('belly_center_z', .91))+float(body.get('belly_height', .92))*.5+.06-.15)*iz/68
        for ix in range(71):
            x = -.72+1.44*ix/70
            for label, back in [('front', False), ('back', True)]:
                result = sample_surface(x, z, back)
                if result is not None:
                    samples[label].append({'x': x, 'z': z, **result})
    whites = [item for item in samples['front'] if item['white']]
    back_white = sum(item['white'] for item in samples['back'])
    oval = {}
    oval_ok = False
    if whites:
        xmin, xmax = min(item['x'] for item in whites), max(item['x'] for item in whites)
        zmin, zmax = min(item['z'] for item in whites), max(item['z'] for item in whites)
        cx, cz = (xmin+xmax)/2, (zmin+zmax)/2
        rx, rz = (xmax-xmin)/2+.0103, (zmax-zmin)/2+.0103
        intersection = union = 0
        for item in samples['front']:
            predicted = ((item['x']-cx)/rx)**2+((item['z']-cz)/rz)**2 <= 1
            intersection += predicted and item['white']
            union += predicted or item['white']
        fit_iou = intersection/max(1, union)
        oval = {'projected_bounds_xz': [xmin, zmin, xmax, zmax],
                'centre_xz': [cx, cz], 'height_to_width': rz/rx,
                'ellipse_mask_intersection_over_union': fit_iou}
        oval_ok = abs(cx) < .05 and 1.03 < rz/rx < 2.3 and fit_iou > .82
    check('front_white_oval_back_gray', len(whites) > 100 and back_white == 0 and oval_ok,
          {'front_surface_samples': len(samples['front']),
           'back_surface_samples': len(samples['back']),
           'white_front_samples': len(whites), 'white_back_samples': back_white,
           'front_centre_rgb': sample_surface(0, float(body.get('belly_center_z', .91))),
           'back_centre_rgb': sample_surface(0, float(body.get('belly_center_z', .91)), True), **oval})
else:
    check('front_white_oval_back_gray', False, {'reason': 'Body has no image texture.'})

archive = OUT / 'revisions/v2/CatGray_IP.blend'
if archive.exists():
    with bpy.data.libraries.load(str(archive), link=False) as (source, destination):
        destination.objects = [next(name for name in source.objects if name.startswith('Head •'))]
    old_head = destination.objects[0]
    old_points = [old_head.matrix_world @ vert.co for vert in old_head.data.vertices]
    new_points = [head.matrix_world @ vert.co - Vector((0, 0, head.location.z))
                  for vert in head.data.vertices]

    def silhouette(points):
        bins = {}
        for point in points:
            zkey = round(point.z, 5)
            bounds = bins.setdefault(zkey, [point.x, point.x, point.y, point.y])
            bounds[0] = min(bounds[0], point.x)
            bounds[1] = max(bounds[1], point.x)
            bounds[2] = min(bounds[2], point.y)
            bounds[3] = max(bounds[3], point.y)
        return bins

    old_rows, new_rows = silhouette(old_points), silhouette(new_points)

    def resample_rows(rows, heights):
        keys = sorted(rows)
        result = {}
        for height in heights:
            for lower, upper in zip(keys, keys[1:]):
                if lower <= height <= upper:
                    weight = (height-lower)/(upper-lower)
                    result[height] = [a+(b-a)*weight
                                      for a, b in zip(rows[lower], rows[upper])]
                    break
        return result

    # Compare the silhouette itself, independent of changed mesh resolution.
    shared = [1.50+2.75*i/100 for i in range(101)]
    old_rows, new_rows = [resample_rows(rows, shared) for rows in (old_rows, new_rows)]
    width_errors = [abs((new_rows[z][1]-new_rows[z][0])
                        -(old_rows[z][1]-old_rows[z][0])) for z in shared]
    upper_samples = [{'height': z, 'old_rear_y': old_rows[z][3],
                      'new_rear_y': new_rows[z][3],
                      'rear_increase': new_rows[z][3]-old_rows[z][3]}
                     for z in shared if 3.45 <= z <= 4.15]
    width_old = max(point.x for point in old_points)-min(point.x for point in old_points)
    width_new = max(point.x for point in new_points)-min(point.x for point in new_points)
    mean_rear_gain = sum(item['rear_increase'] for item in upper_samples)/max(1, len(upper_samples))
    max_width_error = max(width_errors, default=999)
    check('frontal_width_preserved_upper_rear_fuller', len(shared) > 80
          and max_width_error < .01 and mean_rear_gain > .10
          and all(item['rear_increase'] > .08 for item in upper_samples),
          {'compared_height_rings': len(shared), 'old_width': width_old,
           'new_width': width_new, 'max_width_difference_at_equal_height': max_width_error,
           'upper_rear_mean_increase': mean_rear_gain,
           'upper_rear_samples': upper_samples[::4]})
else:
    check('frontal_width_preserved_upper_rear_fuller', False,
          {'reason': 'Expected revisions/v2 native asset is missing.'})

head_min_z = min((head.matrix_world @ vert.co).z for vert in head.data.vertices)
body_max_z = max((body.matrix_world @ vert.co).z for vert in body.data.vertices)
report['neck_overlap_height'] = body_max_z-head_min_z
report['passed'] = not report['failures']
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('UNCLOTHED_REVISION_VERIFICATION', json.dumps(report, ensure_ascii=False), flush=True)
head_surface.close()
body_surface.close()
if report['failures']:
    raise RuntimeError('Unclothed revision checks failed: '+', '.join(report['failures']))
