"""Check preserved approved geometry, separate arm skins and smooth hips."""
import bpy
import bmesh
import hashlib
import json
import math
from array import array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
character = bpy.data.collections['CATGRAY • Character']
objects = list(character.objects)
body = next(o for o in objects if o.name.startswith('Body •'))
arms = sorted([o for o in objects if o.name.startswith('Arm ')], key=lambda o:o.name)
preserved = [o for o in objects if o.type in {'MESH','CURVE'} and o != body and o not in arms]
report = {'revision':'v6', 'checks':{}, 'failures':[]}

def check(name, passed, details):
    report['checks'][name] = {'passed':bool(passed), **details}
    if not passed:
        report['failures'].append(name)

def fingerprint(obj):
    digest = hashlib.sha256()
    if obj.type == 'MESH':
        coordinates = array('f',[0])*(3*len(obj.data.vertices))
        obj.data.vertices.foreach_get('co',coordinates)
        digest.update(coordinates.tobytes())
        for face in sorted(tuple(sorted(p.vertices)) for p in obj.data.polygons):
            digest.update(array('I',face).tobytes())
    else:
        digest.update(array('f',[obj.data.bevel_depth]).tobytes())
        for spline in obj.data.splines:
            if spline.type == 'BEZIER':
                for p in spline.bezier_points:
                    digest.update(array('f',[*p.co,*p.handle_left,*p.handle_right]).tobytes())
            else:
                for p in spline.points:
                    digest.update(array('f',p.co).tobytes())
    return digest.hexdigest()

names = [o.name for o in preserved]+[body.name]
with bpy.data.libraries.load(str(OUT/'revisions/v5/CatGray_IP.blend'),link=False) as (src,dst):
    dst.objects = list(names)
old = dict(zip(names,dst.objects))
comparison = bpy.data.collections.new('QA previous geometry')
bpy.context.scene.collection.children.link(comparison)
for obj in old.values():
    comparison.objects.link(obj)
    obj.hide_render = True
bpy.context.view_layer.update()
changed = [o.name for o in preserved if fingerprint(o)!=fingerprint(old[o.name])]
transform_error = max(abs(o.matrix_basis[i][j]-old[o.name].matrix_basis[i][j])
                      for o in preserved for i in range(4) for j in range(4))
check('approved_head_face_ears_tail_preserved', not changed and transform_error<1e-6,
      {'objects_compared':len(preserved),'changed_geometry':changed,
       'maximum_transform_error':transform_error})

def surface(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data = evaluated.to_mesh()
    points = [obj.matrix_world@v.co for v in data.vertices]
    tree = BVHTree.FromPolygons(points,[list(p.vertices) for p in data.polygons])
    evaluated.to_mesh_clear()
    return tree, points

body_tree, body_points = surface(body)
old_tree, old_points = surface(old[body.name])
arm_surfaces = [surface(arm) for arm in arms]
torso_errors = []
for z in [1.0,1.05,1.10,1.15]:
    for direction in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
        a = old_tree.ray_cast(Vector((0,0,z)),Vector(direction),2)[0]
        b = body_tree.ray_cast(Vector((0,0,z)),Vector(direction),2)[0]
        torso_errors.append((a-b).length)
height_old = max(p.z for p in old_points)-min(p.z for p in old_points)
height_new = max(p.z for p in body_points)-min(p.z for p in body_points)
check('approved_torso_proportions_preserved',max(torso_errors)<.015
      and abs(height_new-height_old)<.003,
      {'height_v5':height_old,'height_v6':height_new,
       'maximum_upper_torso_surface_change':max(torso_errors)})

topologies=[]
for obj in [body]+arms:
    bm=bmesh.new(); bm.from_mesh(obj.data)
    remaining=set(bm.verts); components=0
    while remaining:
        components+=1; todo=[remaining.pop()]
        while todo:
            v=todo.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in remaining:
                    remaining.remove(other); todo.append(other)
    topologies.append({'object':obj.name,'vertices':len(bm.verts),
        'components':components,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
        'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces),
        'quad_ratio':sum(len(f.verts)==4 for f in bm.faces)/len(bm.faces),
        'signed_volume':bm.calc_volume(signed=True)})
    bm.free()
check('separate_closed_arm_skins_and_connected_trunk_legs',len(arms)==2
      and len({o.data.as_pointer() for o in [body]+arms})==3
      and all(t['components']==1 and t['nonmanifold_edges']==0
              and t['zero_area_faces']==0 and t['signed_volume']>0 for t in topologies)
      and all(t['quad_ratio']>.99 for t in topologies[1:]),{'meshes':topologies})

gaps=[]
for base_z in [.56+.01*i for i in range(57)]:
    z=base_z*1.15
    torso_edge=body_tree.ray_cast(Vector((0,0,z)),Vector((1,0,0)),2)[0].x
    row=[]
    for arm,(tree,points) in zip(arms,arm_surfaces):
        sign=1 if arm.location.x>0 else -1
        # Horizontal rays through the arm centre depth resolve the inner edge.
        inner=tree.ray_cast(Vector((0,0,z)),Vector((sign,0,0)),2)[0]
        row.append(abs(inner.x)-torso_edge if inner else 0)
    gaps.append({'height':z,'left':row[0],'right':row[1]})
distances=[]; penetration=[]
for arm,(tree,points) in zip(arms,arm_surfaces):
    for p in points:
        if p.z<1.12*1.15:
            nearest,normal,index,distance=body_tree.find_nearest(p)
            signed=(p-nearest).dot(normal)
            distances.append(distance)
            if signed<-.0001: penetration.append((arm.name,list(p)))
gap_values=[r[k] for r in gaps for k in ('left','right')]
check('arms_follow_body_with_exposed_clearance',not penetration and min(gap_values)>.012
      and sum(gap_values)/len(gap_values)<.07 and min(distances)>.01,
      {'minimum_horizontal_gap':min(gap_values),'mean_horizontal_gap':sum(gap_values)/len(gap_values),
       'minimum_surface_distance_below_shoulders':min(distances),
       'penetrating_vertices_below_shoulders':len(penetration),'height_samples':gaps})

pivots=[]
for arm in arms:
    pivot=arm.matrix_world.translation
    pivots.append({'object':arm.name,'shoulder_origin':list(pivot),
                   'elbow_landmark':list(arm.get('elbow_landmark',[])),
                   'wrist_landmark':list(arm.get('wrist_landmark',[]))})
check('independent_shoulder_origins_for_later_binding',all(1.50<p['shoulder_origin'][2]<1.70
      and .45<abs(p['shoulder_origin'][0])<.62 for p in pivots),
      {'arms':pivots,'armature_created':False,'weights_created':False})

def hip_curvature(tree):
    turns=[]
    for x in [0,.18,.28,.38,-.18,-.28,-.38]:
        curve=[]
        for j in range(64):
            z=(.30+.007*j)*1.15
            hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
            if hit is not None: curve.append(hit)
        for a,b,c in zip(curve,curve[1:],curve[2:]):
            u=(b-a).normalized(); v=(c-b).normalized()
            turns.append(math.degrees(math.acos(max(-1,min(1,u.dot(v))))))
    turns.sort()
    return {'maximum_turn_degrees':max(turns),'p95_turn_degrees':turns[int(len(turns)*.95)],
            'mean_turn_degrees':sum(turns)/len(turns),'samples':len(turns)}
curvature_old,curvature_new=hip_curvature(old_tree),hip_curvature(body_tree)
check('lower_abdomen_leg_transition_smoother',
      curvature_new['maximum_turn_degrees']<curvature_old['maximum_turn_degrees']*.85,
      {'v5':curvature_old,'v6':curvature_new,'sample_height_step':.007*1.15})

report['passed']=not report['failures']
(OUT/'qa/v6_revision_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V6_REVISION_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
if not report['passed']:
    raise RuntimeError('v6 verification failed: '+', '.join(report['failures']))
