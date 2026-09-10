"""Verify v4 proportions, v3-like relaxed arms, and reference-correct v5 ears."""
import bpy
import bmesh
import hashlib
import json
from array import array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
character = bpy.data.collections['CATGRAY • Character']
objects = list(character.objects)
body = next(obj for obj in objects if obj.name.startswith('Body •'))
head = next(obj for obj in objects if obj.name.startswith('Head •'))
manifest = json.loads((OUT/'model_info.json').read_text())
lift = 0.0
report = {'revision': 'v5', 'checks': {}, 'failures': []}


def check(name, passed, details):
    report['checks'][name] = {'passed': bool(passed), **details}
    if not passed:
        report['failures'].append(name)


def fingerprint(obj):
    digest = hashlib.sha256()
    if obj.type == 'MESH':
        coordinates = array('f', [0]) * (3*len(obj.data.vertices))
        obj.data.vertices.foreach_get('co', coordinates)
        digest.update(coordinates.tobytes())
        # Primitive builders may reorder polygons or rotate their loop start.
        # Compare the same face connectivity independently of storage order.
        faces = sorted(tuple(sorted(polygon.vertices)) for polygon in obj.data.polygons)
        for face in faces:
            digest.update(array('I', face).tobytes())
    elif obj.type == 'CURVE':
        digest.update(array('f', [obj.data.bevel_depth]).tobytes())
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for p in spline.bezier_points:
                    digest.update(array('f', [*p.co, *p.handle_left, *p.handle_right]).tobytes())
            else:
                for p in spline.points:
                    digest.update(array('f', p.co).tobytes())
    return digest.hexdigest()


preserved = [obj for obj in objects if obj.name.startswith(('Head ', 'Eye ', 'Face '))]
names = [obj.name for obj in preserved] + [body.name]
with bpy.data.libraries.load(str(OUT/'revisions/v4/CatGray_IP.blend'), link=False) as (src, dst):
    dst.objects = list(names)
old = dict(zip(names, dst.objects))
changed = [obj.name for obj in preserved if fingerprint(obj) != fingerprint(old[obj.name])]
transform_errors = []
for obj in preserved:
    prior = old[obj.name]
    expected = prior.matrix_basis.copy()
    expected.translation.z += lift
    transform_errors.append(max(abs(obj.matrix_basis[i][j]-expected[i][j])
                                for i in range(4) for j in range(4)))
check('approved_head_and_face_preserved', not changed and max(transform_errors) < 1e-6,
      {'objects_compared': len(preserved), 'geometry_changed': changed,
       'max_transform_error': max(transform_errors), 'uniform_lift_z': lift})

old_body = old[body.name]
def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
before, after = bounds(old_body), bounds(body)
ratio = [after[i]/before[i] for i in range(3)]
check('approved_v4_proportions_preserved', .999 < ratio[2] < 1.001
      and .999 < ratio[1] < 1.001 and .97 < ratio[0] < 1.03,
      {'v4_dimensions': before, 'v5_dimensions': after, 'dimension_ratios': ratio})

depsgraph = bpy.context.evaluated_depsgraph_get()
tree = BVHTree.FromObject(body, depsgraph)
gap_samples = []
for base_z in [.56+.01*i for i in range(53)]:
    z = base_z*1.15
    intervals = []
    start = last = None
    for i in range(601):
        x = -1.20+2.40*i/600
        hit, normal, index, distance = tree.ray_cast(Vector((x, -2, z)), Vector((0, 1, 0)), 4)
        if hit is not None:
            if start is None:
                start = x
            last = x
        elif start is not None:
            intervals.append((start, last)); start = last = None
    if start is not None:
        intervals.append((start, last))
    gaps = [intervals[i+1][0]-intervals[i][1] for i in range(len(intervals)-1)]
    gap_samples.append({'height': z, 'occupied_intervals': intervals, 'arm_gaps': gaps})
check('arms_separated_below_shoulders', all(len(row['occupied_intervals']) == 3
                                          and min(row['arm_gaps']) > .020 for row in gap_samples),
      {'samples': gap_samples, 'minimum_gap': min((g for row in gap_samples for g in row['arm_gaps']), default=0)})

ear_objects = [obj for obj in objects if obj.name.startswith('Ear ')]
ear_details = []
for ear in ear_objects:
    if ear.type != 'MESH':
        continue
    bm = bmesh.new(); bm.from_mesh(ear.data)
    nonmanifold = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    max_z = max(v.co.z for v in ear.data.vertices)
    tip = [v.co for v in ear.data.vertices if v.co.z > max_z-.03]
    width = max(v.x for v in tip)-min(v.x for v in tip)
    depths = [v.co.y-(.16+.72*(abs(v.co.x)-1.4)) for v in ear.data.vertices]
    equator = [v.co for v in ear.data.vertices
               if abs(v.co.y-(.16+.72*(abs(v.co.x)-1.4))) < 1e-6]
    turns = []
    for i in range(len(equator)):
        a,b,c = equator[i-1],equator[i],equator[(i+1)%len(equator)]
        turns.append((b.x-a.x)*(c.z-b.z)-(b.z-a.z)*(c.x-b.x))
    orientation = 1 if sum(turns) >= 0 else -1
    wrong_turns = sum(v*orientation < -1e-6 for v in turns)
    def lin(v):
        return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4
    color_errors = []
    for mat, expected in zip(ear.data.materials,[(116,116,116),(255,163,163)]):
        actual = mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value
        color_errors.append(max(abs(actual[i]-lin(expected[i]/255)) for i in range(3)))
    ear_details.append({'object': ear.name, 'nonmanifold_edges': nonmanifold,
                        'upper_tip_span': width, 'intrinsic_thickness': max(depths)-min(depths),
                        'materials': [mat.name for mat in ear.data.materials],
                        'equator_vertices': len(equator), 'concave_turns': wrong_turns,
                        'reference_color_error': max(color_errors)})
check('ears_convex_with_reference_colors_and_no_outline_tubes', len(ear_objects) == len(ear_details) == 2
      and all(row['nonmanifold_edges'] == 0 and row['upper_tip_span'] > .12
              and row['intrinsic_thickness'] > .12 and len(row['materials']) == 2
              and row['concave_turns'] == 0 and row['reference_color_error'] < 1e-6
              for row in ear_details),
      {'ears': ear_details, 'outline_curve_count': sum(obj.type == 'CURVE' for obj in ear_objects)})

projection = json.loads((OUT/'qa/ear_projection_measurements.json').read_text())
pink_area = projection['v5']['projected_pink_area']
reference_area = projection['front_reference']['pink_area_at_100_pixels_per_unit']
check('pink_inset_smaller_and_near_reference',
      pink_area < projection['v4']['projected_pink_area']*.85
      and pink_area < projection['v3']['projected_pink_area']*.95
      and .80 < pink_area/reference_area < 1.10,
      {'projected_pink_area': pink_area, 'v4_pink_area': projection['v4']['projected_pink_area'],
       'v3_pink_area': projection['v3']['projected_pink_area'], 'reference_pink_area': reference_area,
       'ratio_to_reference': pink_area/reference_area})

report['passed'] = not report['failures']
(OUT/'qa/v5_revision_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print('V5_REVISION_VERIFIED', json.dumps(report, ensure_ascii=False), flush=True)
if not report['passed']:
    raise RuntimeError('v5 verification failed: '+', '.join(report['failures']))
