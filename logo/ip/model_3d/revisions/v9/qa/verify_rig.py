"""Native rig checks: rest shape, weights, looping, foot contact and collisions."""
import bpy
import json
import math
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
scene=bpy.context.scene; rig=bpy.data.objects['CATGRAY_RIG']
skins=[o for o in bpy.data.collections['CATGRAY • Character'].objects if o.type=='MESH']
body=next(o for o in skins if o.name.startswith('Body '))
head=next(o for o in skins if o.name.startswith('Head '))
arms=[o for o in skins if o.name.startswith('Arm ')]
report={'revision':'v9','checks':{},'failures':[]}
def check(name,passed,details):
    report['checks'][name]={'passed':bool(passed),**details}
    if not passed: report['failures'].append(name)

def surface(obj,tree=False):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); data=ev.to_mesh()
    coords=np.empty(len(data.vertices)*3,dtype=np.float32)
    data.vertices.foreach_get('co',coords); coords=coords.reshape(-1,3)
    matrix=np.array(obj.matrix_world)
    coords=coords@matrix[:3,:3].T+matrix[:3,3]
    bvh=BVHTree.FromPolygons(coords,[list(p.vertices) for p in data.polygons]) if tree else None
    ev.to_mesh_clear()
    return coords,bvh

rig.animation_data.use_nla=False; rig.animation_data.action=None
rig.data.pose_position='REST'; bpy.context.view_layer.update()
rest={o.name:surface(o)[0] for o in skins}
original_names=[o.name for o in skins]
with bpy.data.libraries.load(str(OUT/'revisions/v7/CatGray_IP.blend'),link=False) as (src,dst):
    dst.objects=list(original_names)
previous=dict(zip(original_names,dst.objects))
archive=bpy.data.collections.new('QA v7 reference')
scene.collection.children.link(archive)
for obj in previous.values(): archive.objects.link(obj); obj.hide_render=True
bpy.context.view_layer.update()
rest_errors=[]
for obj in skins:
    points=surface(previous[obj.name])[0]
    error=float(np.max(np.linalg.norm(points-rest[obj.name],axis=1))) if points.shape==rest[obj.name].shape else 999.
    rest_errors.append({'object':obj.name,'max_vertex_error':error})
check('approved_v7_rest_shape_preserved',max(r['max_vertex_error'] for r in rest_errors)<.00002,
      {'objects':rest_errors})

invalid=0; max_error=0.; max_influences=0
for obj in skins:
    for vertex in obj.data.vertices:
        weights=[g.weight for g in vertex.groups]
        error=abs(sum(weights)-1)
        invalid+=error>.0001 or not weights or len(weights)>4
        max_error=max(max_error,error); max_influences=max(max_influences,len(weights))
check('all_meshes_normalized_and_parented_to_rig',invalid==0
      and all(o.parent==rig and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers) for o in skins),
      {'skinned_objects':len(skins),'invalid_vertices':invalid,
       'maximum_weight_error':max_error,'maximum_influences':max_influences})

rig.data.pose_position='POSE'
def activate(name,frame):
    action=bpy.data.actions[name]
    rig.animation_data.action=action; rig.animation_data.action_slot=action.slots[0]
    scene.frame_set(frame); bpy.context.view_layer.update()

loops=[]
for name,end in [('Idle_Breathe',73),('Walk_InPlace',37),('Wave',97)]:
    activate(name,1); first={p.name:p.matrix.copy() for p in rig.pose.bones}
    activate(name,end)
    error=max(abs(p.matrix[i][j]-first[p.name][i][j]) for p in rig.pose.bones for i in range(4) for j in range(4))
    loops.append({'clip':name,'endpoint_pose_error':error})
check('loop_endpoints_and_wave_return_match',all(r['endpoint_pose_error']<.0001 for r in loops),{'clips':loops})

face_meshes=[o for o in skins if o.name.startswith(('Head ','Eye ','Face '))]
face_ok=all(all(len(v.groups)==1 and o.vertex_groups[v.groups[0].group].name=='Head' and abs(v.groups[0].weight-1)<1e-6
                   for v in o.data.vertices) for o in face_meshes)
check('face_keeps_contact_with_head',face_ok,{'rigid_head_bound_objects':len(face_meshes)})

soles={side:np.where((rest[body.name][:,2]<.008)&(rest[body.name][:,0]*sign>.13))[0]
       for side,sign in [('L',-1),('R',1)]}
ground=[]
for f in range(1,38):
    activate('Walk_InPlace',f)
    p,_=surface(body)
    for side,offset in [('R',0),('L',.5)]:
        q=((f-1)/36+offset)%1
        values=p[soles[side],2]
        ground.append({'frame':f,'side':side,'stance':q<=.5,'lowest_z':float(values.min()),
                       'highest_sole_z':float(values.max())})
stance=[r for r in ground if r['stance']]
check('walking_feet_contact_ground',min(r['lowest_z'] for r in ground)>-.006
      and max(abs(r['lowest_z']) for r in stance)<.006
      and max(r['lowest_z'] for r in ground)>.025,
      {'minimum_z':min(r['lowest_z'] for r in ground),'maximum_stance_ground_error':max(abs(r['lowest_z']) for r in stance),
       'maximum_swing_clearance':max(r['lowest_z'] for r in ground),'samples':ground})

collision_samples=[]
for name,end in [('Idle_Breathe',73),('Wave',97),('Walk_InPlace',37)]:
    for frame in list(range(1,end+1,6))+[end]:
        activate(name,frame)
        _,head_tree=surface(head,True); _,body_tree=surface(body,True)
        worst_head=1e9; worst_body=1e9
        for arm in arms:
            points,_=surface(arm)
            indices=np.where(rest[arm.name][:,2]<1.30)[0][::32]
            for p in points[indices]:
                vector=Vector(p)
                for tree,which in [(head_tree,'head'),(body_tree,'body')]:
                    hit,normal,index,distance=tree.find_nearest(vector)
                    signed=(vector-hit).dot(normal)
                    if which=='head': worst_head=min(worst_head,signed)
                    else: worst_body=min(worst_body,signed)
        collision_samples.append({'clip':name,'frame':frame,'hand_head_signed_clearance':worst_head,
                                  'distal_arm_body_signed_clearance':worst_body})
check('hands_and_forearms_clear_head_and_body',all(r['hand_head_signed_clearance']>-.003
      and r['distal_arm_body_signed_clearance']>-.006 for r in collision_samples),{'samples':collision_samples})

activate('Wave',1); hand_start=rig.pose.bones['Hand.R'].tail.copy()
activate('Wave',54); hand_end=rig.pose.bones['Hand.R'].tail.copy()
check('wave_has_clear_gesture', (hand_end-hand_start).length>.75,
      {'hand_displacement':(hand_end-hand_start).length,'raised_hand_position':list(hand_end)})

report['passed']=not report['failures']
(OUT/'qa/rig_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('RIG_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
if not report['passed']: raise RuntimeError('Rig checks failed: '+', '.join(report['failures']))
