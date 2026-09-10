"""Verify continuous body meshes and the preservation of the approved head."""
import bpy
import bmesh
import hashlib
import json
from array import array
from pathlib import Path

out=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(out/'CatGray_IP.blend'))
names=[o.name for o in bpy.data.collections['CATGRAY • Character'].objects
       if o.name.startswith(('Head •','Eye ','Ear ','Face •'))]

def signature(obj):
    digest=hashlib.sha256()
    if obj.type=='MESH':
        coords=array('f',[0])*(len(obj.data.vertices)*3)
        obj.data.vertices.foreach_get('co',coords)
        digest.update(coords.tobytes())
    elif obj.type=='CURVE':
        for spline in obj.data.splines:
            for p in spline.bezier_points:
                digest.update(array('f',list(p.co)+list(p.handle_left)+list(p.handle_right)).tobytes())
    digest.update(array('f',[v for row in obj.matrix_basis for v in row]).tobytes())
    return digest.hexdigest()

current={name:signature(bpy.data.objects[name]) for name in names}
with bpy.data.libraries.load(str(out/'revisions/v1/CatGray_IP.blend'),link=False) as (src,dst):
    dst.objects=list(names)
original={name:signature(obj) for name,obj in zip(names,dst.objects)}
if current!=original:
    for name,obj in zip(names,dst.objects):
        if current[name]!=original[name]:
            current_obj=bpy.data.objects[name]
            differences={'name':name,'loaded_name':obj.name,
                         'matrix_error':max(abs(current_obj.matrix_basis[r][c]-obj.matrix_basis[r][c]) for r in range(4) for c in range(4))}
            if obj.type=='MESH':
                differences['vertices']=[len(current_obj.data.vertices),len(obj.data.vertices)]
                if len(current_obj.data.vertices)==len(obj.data.vertices):
                    differences['vertex_error']=max((a.co-b.co).length for a,b in zip(current_obj.data.vertices,obj.data.vertices))
            print('HEAD_DIFFERENCE',json.dumps(differences),flush=True)
assert current==original,'Approved facial geometry changed'
checks={}
for name in ('Hoodie • continuous torso and sleeves','Body • connected pelvis legs and paws'):
    obj=bpy.data.objects[name]
    bm=bmesh.new();bm.from_mesh(obj.data)
    unseen=set(bm.verts);components=0
    while unseen:
        components+=1
        todo=[unseen.pop()]
        while todo:
            v=todo.pop()
            for e in v.link_edges:
                nxt=e.other_vert(v)
                if nxt in unseen:unseen.remove(nxt);todo.append(nxt)
    boundary=sum(e.is_boundary for e in bm.edges)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    assert components==1,(name,components)
    assert boundary==0 and nonmanifold==0,(name,boundary,nonmanifold)
    checks[name]={'connected_components':components,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold}
    bm.free()
report={'head_objects_unchanged':len(names),'body_mesh_checks':checks}
(out/'qa/body_revision_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('BODY_REVISION_VERIFIED',json.dumps(report),flush=True)
