"""Reimport delivered GLB and compare its animated poses with the native rig."""
import bpy
import json
import struct
import numpy as np
from pathlib import Path

OUT=Path(__file__).resolve().parent.parent
raw=(OUT/'CatGray_IP.glb').read_bytes()
magic,version,total=struct.unpack_from('<4sII',raw,0)
assert magic==b'glTF' and version==2 and total==len(raw)
size,kind=struct.unpack_from('<II',raw,12)
assert kind==0x4E4F534A
doc=json.loads(raw[20:20+size])
names={a['name'] for a in doc.get('animations',[])}
assert names=={'Idle_Breathe','Wave','Walk_InPlace'},names
assert len(doc.get('skins',[]))==1
assert 38<=len(doc['skins'][0]['joints'])<=43
assert len(doc.get('images',[]))==2
assert all('bufferView' in i and 'uri' not in i for i in doc['images'])
assert all('uri' not in b for b in doc['buffers'])
assert all('skin' in n for n in doc['nodes'] if 'mesh' in n)
durations={}
for action in doc['animations']:
    accesses=[doc['accessors'][s['input']] for s in action['samplers']]
    duration=max(a['max'][0] for a in accesses)-min(a['min'][0] for a in accesses)
    durations[action['name']]=duration
    assert abs(duration-{'Idle_Breathe':3,'Wave':4,'Walk_InPlace':1.5}[action['name']])<.0001

bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
scene=bpy.context.scene
original=bpy.data.collections['CATGRAY • Character']
rig=bpy.data.objects['CATGRAY_RIG']
meshes=[o for o in original.objects if o.type=='MESH']
rig.animation_data.use_nla=False
def activate(target,action,frame):
    target.animation_data.use_nla=False
    target.animation_data.action=action
    target.animation_data.action_slot=action.slots[0]
    scene.frame_set(int(frame),subframe=frame-int(frame))

def bounds(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); data=ev.to_mesh()
    p=np.empty(len(data.vertices)*3,dtype=np.float32)
    data.vertices.foreach_get('co',p); p=p.reshape(-1,3)
    matrix=np.array(obj.matrix_world)
    p=p@matrix[:3,:3].T+matrix[:3,3]
    result=np.r_[p.min(axis=0),p.max(axis=0)]
    ev.to_mesh_clear()
    return result

reference={}
for clip,frame in [('Idle_Breathe',37),('Wave',54),('Walk_InPlace',10)]:
    activate(rig,bpy.data.actions[clip],frame)
    reference[(clip,frame)]={o.name:bounds(o) for o in meshes}
original.hide_render=True
before_objects=set(bpy.data.objects); before_actions=set(bpy.data.actions)
bpy.ops.import_scene.gltf(filepath=str(OUT/'CatGray_IP.glb'))
imported=set(bpy.data.objects)-before_objects
actions=set(bpy.data.actions)-before_actions
armatures=[o for o in imported if o.type=='ARMATURE']
assert len(armatures)==1
target=armatures[0]
# Blender's importer also creates an Icosphere as a bone display helper.
# Count the actual skinned character objects, independently of that UI mesh.
imported_meshes=[o for o in imported if o.type=='MESH' and any(
    m.type=='ARMATURE' and m.object==target for m in o.modifiers)]
display_helpers=[o for o in imported if o.type=='MESH' and o not in imported_meshes]
for helper in display_helpers: helper.hide_render=True
assert len(armatures)==1 and len(imported_meshes)==len(meshes)==28, {
    'armatures':[o.name for o in armatures], 'imported_meshes':[o.name for o in imported_meshes],
    'native_meshes':[o.name for o in meshes]}
mapping={o.name:next(m for m in imported_meshes if m.name==o.name or m.name.startswith(o.name+'.')) for o in meshes}
pose_reports=[]
for (clip,frame),expected in reference.items():
    action=next(a for a in actions if a.name.startswith(clip))
    imported_frame=frame-1+float(action.frame_range[0])
    activate(target,action,imported_frame)
    errors={name:float(np.max(np.abs(bounds(mapping[name])-box))) for name,box in expected.items()}
    pose_reports.append({'clip':clip,'native_frame':frame,'imported_frame':imported_frame,
                         'maximum_bounds_error':max(errors.values()),'objects':errors})
    assert max(errors.values())<.008,pose_reports[-1]
wave=next(a for a in actions if a.name.startswith('Wave'))
activate(target,wave,53+float(wave.frame_range[0]))
scene.camera=bpy.data.objects['Camera • Three quarter']
scene.render.engine='BLENDER_EEVEE'; scene.eevee.taa_render_samples=64
scene.render.resolution_x=720; scene.render.resolution_y=720
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(OUT/'qa/rig_glb_reimport_wave.png')
bpy.ops.render.render(write_still=True)
report={'passed':True,'format':'glTF 2.0 binary','clip_durations_seconds':durations,
    'skin_count':len(doc['skins']),'joints':len(doc['skins'][0]['joints']),
    'skinned_meshes':len(imported_meshes),'embedded_images':2,'external_dependencies':False,
    'importer_display_helpers':[o.name for o in display_helpers],
    'native_export_pose_comparisons':pose_reports,'bytes':len(raw)}
(OUT/'qa/animated_export_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('ANIMATED_EXPORT_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
