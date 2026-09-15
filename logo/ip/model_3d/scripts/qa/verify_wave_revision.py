"""Check wave arm surface intersections and unobstructed native rig display."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
rig=bpy.data.objects['CATGRAY_RIG']; scene=bpy.context.scene
report={'revision':'v10','viewport':{'in_front':rig.show_in_front,
    'bone_display':rig.data.display_type,'rig_selected':rig.select_get()},'samples':[]}
assert not rig.show_in_front and rig.data.display_type=='STICK' and not rig.select_get()
rig.animation_data.use_nla=False
rig.animation_data.action=bpy.data.actions['Wave']
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
arm=next(o for o in bpy.data.objects if o.name.startswith('Arm R '))
points=[rig.matrix_world.inverted()@arm.matrix_world@v.co for v in arm.data.vertices]
levels=sorted({round(p.z,6) for p in points},reverse=True)
rings=[[i for i,p in enumerate(points) if abs(p.z-z)<1e-5] for z in levels]
def area(vertices):
    return sum((a.cross(b) for a,b in zip(vertices,vertices[1:]+vertices[:1])),Vector()).length*.5
rest_areas=[area([points[i] for i in ring]) for ring in rings]
bindings=[[(arm.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in arm.data.vertices]
inverse_bind={b.name:b.matrix_local.inverted() for b in rig.data.bones}
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
    transforms={name:rig.pose.bones[name].matrix@matrix for name,matrix in inverse_bind.items()}
    deformed=[sum((w*(transforms[name]@p) for name,w in groups),Vector()) for p,groups in zip(points,bindings)]
    ratios=[area([deformed[i] for i in ring])/base for ring,base in zip(rings,rest_areas)][2:-2]
    centres=[sum((deformed[i] for i in ring),Vector())/len(ring) for ring in rings]
    tangents=[(b-a).normalized() for a,b in zip(centres,centres[1:])]
    turns=[math.degrees(a.angle(b)) for a,b in zip(tangents,tangents[1:])]
    report['samples'].append({'frame':frame,'nonadjacent_surface_intersections':len(intersections),
        'minimum_section_area_ratio':min(ratios),'maximum_section_area_ratio':max(ratios),
        'maximum_adjacent_section_turn_degrees':max(turns)})
    assert not intersections,(frame,intersections[:5])
    assert min(ratios)>.85,(frame,'arm cross section collapsed',min(ratios))
    assert max(turns)<18,(frame,'abrupt arm centreline bend',max(turns))
report['passed']=True
(OUT/'qa/wave_revision_verification.json').write_text(json.dumps(report,indent=2))
print('WAVE_REVISION_VERIFIED',len(report['samples']),'frames',flush=True)
