"""Check wave arm surface intersections and unobstructed native rig display."""
import bpy
import json
from pathlib import Path
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
rig=bpy.data.objects['CATGRAY_RIG']; scene=bpy.context.scene
report={'revision':'v9','viewport':{'in_front':rig.show_in_front,
    'bone_display':rig.data.display_type,'rig_selected':rig.select_get()},'samples':[]}
assert not rig.show_in_front and rig.data.display_type=='STICK' and not rig.select_get()
rig.animation_data.use_nla=False
rig.animation_data.action=bpy.data.actions['Wave']
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
arm=next(o for o in bpy.data.objects if o.name.startswith('Arm R '))
# Check the final subdivided, skinned surface across the entire action.
for frame in range(1,98):
    scene.frame_set(frame)
    ev=arm.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
    vertices=[v.co.copy() for v in mesh.vertices]
    polygons=[tuple(p.vertices) for p in mesh.polygons]
    tree=BVHTree.FromPolygons(vertices,polygons)
    intersections=[(a,b) for a,b in tree.overlap(tree)
        if a<b and not set(polygons[a]).intersection(polygons[b])]
    ev.to_mesh_clear()
    hand_angle=rig.pose.bones['Hand.R'].rotation_quaternion.angle
    report['samples'].append({'frame':frame,'nonadjacent_surface_intersections':len(intersections),
        'local_hand_rotation_radians':hand_angle})
    assert not intersections,(frame,intersections[:5])
    assert abs(hand_angle)<1e-6,(frame,hand_angle)
report['passed']=True
(OUT/'qa/wave_revision_verification.json').write_text(json.dumps(report,indent=2))
print('WAVE_REVISION_VERIFIED',len(report['samples']),'frames',flush=True)
