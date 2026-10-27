"""Render isolated dedicated speaking shapes for visual review (Blender)."""
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from rig_voxel import RIG,rest_pose
from facial_voxel import select_states
from desktop_pet_speech import STATES
OUT=ROOT/'desktop_pet/review'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'desktop_pet/CatGray_DesktopPet.blend'))
scene=bpy.context.scene
rest_pose(bpy.data.objects[RIG])
scene.render.engine='CYCLES'
scene.cycles.samples=16
scene.cycles.device='CPU'
scene.render.resolution_x=scene.render.resolution_y=384
scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
for obj in bpy.data.collections['DesktopPet • Keyboard'].objects:
    obj.hide_render=True
camera=scene.camera
camera.data.ortho_scale=3.5
camera.location=(1.8,-14,3.6)
camera.rotation_euler=(Vector((0,-.1,3.10))-camera.location).to_track_quat('-Z','Y').to_euler()
gallery=np.zeros((384,1536,4),dtype=np.float32)
samples=[]
for index,name in enumerate(STATES):
    select_states('Open',name)
    bpy.context.view_layer.update()
    path=OUT/f'{name}.png'
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(str(path),check_existing=False)
    data=np.empty(384*384*4,dtype=np.float32)
    image.pixels.foreach_get(data)
    samples.append(data.reshape(384,384,4).copy())
    gallery[:,index*384:(index+1)*384]=samples[-1]
    bpy.data.images.remove(image)
for i in range(len(samples)):
    for j in range(i):
        assert np.count_nonzero(np.max(np.abs(samples[i]-samples[j]),axis=2)>.02)>10, 'Speech shapes visually indistinguishable'
image=bpy.data.images.new('Dedicated speech apertures',width=1536,height=384,alpha=True)
image.pixels.foreach_set(gallery.ravel())
image.filepath_raw=str(OUT/'speech_mouth_shapes.png')
image.file_format='PNG'
image.save()
print('DEDICATED SPEECH SHAPES RENDERED')
