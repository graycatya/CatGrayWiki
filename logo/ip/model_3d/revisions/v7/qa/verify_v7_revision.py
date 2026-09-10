"""Verify thicker ear volumes while preserving the approved v6 character."""
import bpy
import bmesh
import hashlib
import json
import math
from array import array
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
objects=[o for o in bpy.data.collections['CATGRAY • Character'].objects if o.type in {'MESH','CURVE'}]
ears=[o for o in objects if o.name.startswith('Ear ')]
names=[o.name for o in objects]
with bpy.data.libraries.load(str(OUT/'revisions/v6/CatGray_IP.blend'),link=False) as (src,dst):
    dst.objects=list(names)
old=dict(zip(names,dst.objects))
collection=bpy.data.collections.new('QA archived v6')
bpy.context.scene.collection.children.link(collection)
for obj in old.values():
    collection.objects.link(obj)
    obj.hide_render=True
bpy.context.view_layer.update()
report={'revision':'v7','checks':{},'failures':[]}

def check(name,passed,details):
    report['checks'][name]={'passed':bool(passed),**details}
    if not passed: report['failures'].append(name)

def fingerprint(obj):
    digest=hashlib.sha256()
    if obj.type=='MESH':
        coordinates=array('f',[0])*(3*len(obj.data.vertices))
        obj.data.vertices.foreach_get('co',coordinates)
        digest.update(coordinates.tobytes())
        for face in sorted(tuple(sorted(p.vertices)) for p in obj.data.polygons):
            digest.update(array('I',face).tobytes())
    else:
        digest.update(array('f',[obj.data.bevel_depth]).tobytes())
        for spline in obj.data.splines:
            if spline.type=='BEZIER':
                for p in spline.bezier_points:
                    digest.update(array('f',[*p.co,*p.handle_left,*p.handle_right]).tobytes())
            else:
                for p in spline.points: digest.update(array('f',p.co).tobytes())
    return digest.hexdigest()

preserved=[o for o in objects if o not in ears]
changed=[o.name for o in preserved if fingerprint(o)!=fingerprint(old[o.name])]
transform_error=max(abs(o.matrix_basis[i][j]-old[o.name].matrix_basis[i][j])
                    for o in objects for i in range(4) for j in range(4))
check('v6_head_face_body_arms_and_tail_unchanged',not changed and transform_error<1e-6,
      {'objects_compared':len(preserved),'changed_geometry':changed,'transform_error':transform_error})

details=[]
for ear in ears:
    prior=old[ear.name]
    xz_error=max(abs(a.co[i]-b.co[i]) for a,b in zip(ear.data.vertices,prior.data.vertices) for i in (0,2))
    material_faces_unchanged=all(a.material_index==b.material_index
                               for a,b in zip(ear.data.polygons,prior.data.polygons))
    measurements=[]
    for obj in [prior,ear]:
        bm=bmesh.new(); bm.from_mesh(obj.data)
        depths=[v.co.y-(.16+.72*(abs(v.co.x)-1.4)) for v in bm.verts]
        measurements.append({'axial_depth':max(depths)-min(depths),
            'normal_depth':(max(depths)-min(depths))/math.sqrt(1+.72**2),
            'volume':bm.calc_volume(signed=True),
            'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
            'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)})
        bm.free()
    colors=[]
    for mat in ear.data.materials:
        linear=mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value
        colors.append([round(255*(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055)) for v in linear[:3]])
    details.append({'object':ear.name,'front_outline_xz_error':xz_error,
        'pink_face_assignment_unchanged':material_faces_unchanged,'material_srgb':colors,
        'v6':measurements[0],'v7':measurements[1],
        'depth_ratio':measurements[1]['axial_depth']/measurements[0]['axial_depth'],
        'volume_ratio':measurements[1]['volume']/measurements[0]['volume']})
check('ears_thicker_closed_and_reference_shape_preserved',len(details)==2 and all(
    r['front_outline_xz_error']<1e-6 and r['pink_face_assignment_unchanged']
    and r['material_srgb']==[[116,116,116],[255,163,163]]
    and 2.0<r['depth_ratio']<2.4 and 2.0<r['volume_ratio']<2.4
    and r['v7']['nonmanifold_edges']==0 and r['v7']['zero_area_faces']==0
    and r['v7']['volume']>0 for r in details),{'ears':details})

def visible_pink_area(group):
    verts,faces,labels=[],[],[]
    for obj in group:
        if not obj.name.startswith(('Head ','Ear ')): continue
        ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); data=ev.to_mesh()
        offset=len(verts)
        verts.extend(obj.matrix_world@v.co for v in data.vertices)
        for p in data.polygons:
            faces.append(tuple(offset+i for i in p.vertices))
            labels.append(obj.name.startswith('Ear ') and p.material_index==1)
        ev.to_mesh_clear()
    tree=BVHTree.FromPolygons(verts,faces)
    count=0
    for i in range(181):
        for j in range(181):
            hit,normal,index,distance=tree.ray_cast(Vector((.65+1.3*i/180,-5,3.20+1.22*j/180+.21075)),Vector((0,1,0)),10)
            count+=hit is not None and labels[index]
    return count*(1.3/180)*(1.22/180)
before,after=visible_pink_area(list(old.values())),visible_pink_area(objects)
check('visible_pink_region_keeps_approved_size',.95<after/before<1.05,
      {'v6_projected_area':before,'v7_projected_area':after,'ratio':after/before})
report['passed']=not report['failures']
(OUT/'qa/v7_revision_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('V7_REVISION_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
if not report['passed']: raise RuntimeError('v7 verification failed: '+', '.join(report['failures']))
