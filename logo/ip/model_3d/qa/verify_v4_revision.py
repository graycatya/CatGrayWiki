"""Check the approved face, larger body, free arm gaps, and rounded ear shells."""
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
lift = manifest['head_revision']['translation_z']
report = {'revision': 'v4', 'checks': {}, 'failures': []}


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
with bpy.data.libraries.load(str(OUT/'revisions/v3/CatGray_IP.blend'), link=False) as (src, dst):
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
check('body_larger_than_v3', 1.14 < ratio[2] < 1.16 and 1.10 < ratio[0] < 1.30,
      {'v3_dimensions': before, 'v4_dimensions': after, 'dimension_ratios': ratio})

depsgraph = bpy.context.evaluated_depsgraph_get()
tree = BVHTree.FromObject(body, depsgraph)
gap_samples = []
for base_z in (.60, .76, .92, 1.06):
    z = base_z*1.15
    intervals = []
    start = last = None
    for i in range(961):
        x = -1.20+2.40*i/960
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
    depths = [v.co.y-(.12+.60*(abs(v.co.x)-1.4)) for v in ear.data.vertices]
    ear_details.append({'object': ear.name, 'nonmanifold_edges': nonmanifold,
                        'upper_tip_span': width, 'intrinsic_thickness': max(depths)-min(depths),
                        'materials': [mat.name for mat in ear.data.materials]})
check('ears_closed_rounded_without_outline_tubes', len(ear_objects) == len(ear_details) == 2
      and all(row['nonmanifold_edges'] == 0 and row['upper_tip_span'] > .12
              and row['intrinsic_thickness'] > .18 and len(row['materials']) == 2
              for row in ear_details),
      {'ears': ear_details, 'outline_curve_count': sum(obj.type == 'CURVE' for obj in ear_objects)})

report['passed'] = not report['failures']
(OUT/'qa/v4_revision_verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print('V4_REVISION_VERIFIED', json.dumps(report, ensure_ascii=False), flush=True)
if not report['passed']:
    raise RuntimeError('v4 verification failed: '+', '.join(report['failures']))
