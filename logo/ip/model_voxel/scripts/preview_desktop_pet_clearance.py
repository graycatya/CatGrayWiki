"""Front and side visual review of the corrected thinking/typing hand poses."""
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desktop_pet_actions as pet
from rig_voxel import RIG
OUT=ROOT/'desktop_pet/review'
OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'desktop_pet/CatGray_DesktopPet.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.device='CPU'
scene.cycles.samples=16
scene.render.resolution_x,scene.render.resolution_y=384,416
scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
rig=bpy.data.objects[RIG]
camera=scene.camera
camera.data.ortho_scale=6.6
gallery=np.zeros((832,1152,4),dtype=np.float32)
for row,(name,frame) in enumerate([('Thinking',19),('Working',8)]):
    pet.activate(rig,'Pet_'+name)
    scene.frame_set(frame)
    for col,location in enumerate([(6,-16,7.2),(-12,-7,5.8),(12,-7,5.8)]):
        camera.location=location
        camera.rotation_euler=(Vector((0,-.1,2.65))-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(OUT/f'clearance_{name}_{col}.png')
        bpy.ops.render.render(write_still=True)
        image=bpy.data.images.load(scene.render.filepath,check_existing=False)
        data=np.empty(384*416*4,dtype=np.float32)
        image.pixels.foreach_get(data)
        gallery[(1-row)*416:(2-row)*416,col*384:(col+1)*384]=data.reshape(416,384,4)
        bpy.data.images.remove(image)
image=bpy.data.images.new('Hand clearance front and sides',width=1152,height=832,alpha=True)
image.pixels.foreach_set(gallery.ravel())
image.file_format='PNG'
image.filepath_raw=str(OUT/'clearance_views.png')
image.save()
print('FRONT AND SIDE CLEARANCE VIEWS RENDERED')
