"""Reimport the actual delivery GLB and render it in the native studio."""
import bpy
import json
import struct
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent
qa=out/'qa'
qa.mkdir(exist_ok=True)
raw=(out/'CatGray_IP.glb').read_bytes()
magic,version,size=struct.unpack_from('<4sII',raw,0)
assert magic==b'glTF' and version==2 and size==len(raw)
json_size,chunk_type=struct.unpack_from('<II',raw,12)
assert chunk_type==0x4E4F534A
document=json.loads(raw[20:20+json_size])
if document.get('animations'):
    import runpy
    runpy.run_path(str(qa/'verify_animated_export.py'),run_name='__main__')
    raise SystemExit(0)
assert all('bufferView' in im and 'uri' not in im for im in document.get('images',[]))
assert len(document.get('images',[])) == 2
assert not document.get('animations')
assert not document.get('cameras')

bpy.ops.wm.open_mainfile(filepath=str(out/'CatGray_IP.blend'))
original=bpy.data.collections.get('CATGRAY • Character')
original.hide_render=True
original.hide_viewport=True
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(out/'CatGray_IP.glb'))
imported=set(bpy.data.objects)-before
meshes=[o for o in imported if o.type=='MESH']
expected=json.loads((out/'model_info.json').read_text(encoding='utf-8'))
assert len(meshes)==expected['objects']
arms=[o for o in meshes if o.name.startswith('Arm ')]
assert len(arms)==2 and arms[0].data!=arms[1].data
bpy.context.view_layer.update()
coords=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
minimum=[min(v[i] for v in coords) for i in range(3)]
maximum=[max(v[i] for v in coords) for i in range(3)]
assert max(abs(minimum[i]-expected['world_bounds']['min'][i]) for i in range(3))<.0001
assert max(abs(maximum[i]-expected['world_bounds']['max'][i]) for i in range(3))<.0001
scene=bpy.context.scene
scene.render.resolution_x=800
scene.render.resolution_y=800
scene.cycles.samples=48
scene.render.filepath=str(qa/'glb_reimport_hero.png')
bpy.ops.render.render(write_still=True)
result={'glb_header':'valid glTF 2.0 binary','embedded_images':len(document.get('images',[])),
        'mesh_objects_after_reimport':len(meshes),'world_bounds_match':True,
        'independent_arm_meshes':[o.name for o in arms],
        'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),
        'materials':len(document.get('materials',[])),
        'external_dependencies':False,'reimport_render':'qa/glb_reimport_hero.png'}
(qa/'export_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('EXPORT_VERIFIED',json.dumps(result),flush=True)
