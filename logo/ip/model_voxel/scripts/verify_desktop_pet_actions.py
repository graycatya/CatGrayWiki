"""Validate the delivered Blender file's actions and playable native NLA reel."""
import json
from pathlib import Path
import sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desktop_pet_actions as pet
from rig_voxel import RIG
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'desktop_pet/CatGray_DesktopPet.blend'))
rig=bpy.data.objects[RIG]
scene=bpy.context.scene
collection=bpy.data.collections[pet.PROP_COLLECTION]
start=1
reel={}
for name,duration in pet.DURATIONS.items():
    scene.frame_set(start+duration*6)
    bpy.context.view_layer.update()
    expected=name=='Working'
    assert all(obj.hide_render != expected for obj in collection.objects),name+' prop visibility'
    matrices=np.array([[v for row in b.matrix for v in row] for b in rig.pose.bones])
    scene.frame_set(start+duration*15)
    bpy.context.view_layer.update()
    later=np.array([[v for row in b.matrix for v in row] for b in rig.pose.bones])
    assert np.max(np.abs(matrices-later))>.01,name+' native timeline static'
    reel[name]={'start':start,'end':start+duration*24-1,'keyboardVisible':expected,'nativeNlaMotion':True}
    start+=duration*24
pet.activate(rig,'Pet_Speaking')
speech_shapes=set()
for frame in range(1,74):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    blocks=pet.face_keys().key_blocks
    active=[k.name for k in blocks if k.name.startswith('Mouth_') and k.value>.001]
    assert len(active)==1 and active[0].startswith('Mouth_Talk'), ('mixed/legacy speech mouth',frame,active)
    assert abs(blocks[active[0]].value-1)<1e-6
    speech_shapes.add(active[0])
assert speech_shapes=={'Mouth_'+n for n in pet.speech.STATES}, speech_shapes
report={'passed':True,'speechMouth':{'dedicatedShapes':sorted(speech_shapes),'oneActiveShapePerFrame':True,'legacyMouthShapesUsed':False},'sourceActionsPreserved':all(bpy.data.actions.get(n) for n in ['Walk_InPlace','Mouth_Talk','Emotion_Joy']),
        'nativeTimeline':reel,'bakedActions':pet.verify(rig)}
assert report['sourceActionsPreserved']
(ROOT/'desktop_pet/action_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE ACTIONS AND NLA VERIFIED')
