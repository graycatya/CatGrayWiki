"""Render diagnostic poses before producing all animation frames."""
import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
assert bpy.data.objects.get('CATGRAY_RIG'), 'Rig build must finish before pose previews'
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.render.resolution_x=800; scene.render.resolution_y=800
scene.render.image_settings.file_format='PNG'
for filename,frame,camera in [('rig_idle',1,'Three quarter'),('rig_wave',126,'Three quarter'),
                              ('rig_wave_front',126,'Front'),('rig_walk_side',178,'Side'),
                              ('rig_walk_front',178,'Front')]:
    scene.frame_set(frame)
    scene.camera=bpy.data.objects['Camera • '+camera]
    scene.render.filepath=str(OUT/'qa'/f'{filename}.png')
    print('RIG_POSE_RENDER',filename,frame,flush=True)
    bpy.ops.render.render(write_still=True)
scene.render.engine='BLENDER_EEVEE'
if hasattr(scene.eevee,'taa_render_samples'): scene.eevee.taa_render_samples=32
scene.frame_set(126); scene.camera=bpy.data.objects['Camera • Three quarter']
scene.render.filepath=str(OUT/'qa/rig_wave_eevee.png')
bpy.ops.render.render(write_still=True)
editor=scene.sequence_editor_create()
print('SEQUENCE_API',[a for a in dir(editor) if a in ('strips','sequences','sequences_all')],flush=True)
print('RIG_POSE_PREVIEWS_COMPLETE',flush=True)
