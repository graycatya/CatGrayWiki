"""Render front, side and three-quarter checkpoints for the forward wave."""
import bpy
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32
s.render.resolution_x=720;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
for f,view in [(126,'Front'),(126,'Three quarter'),(126,'Side'),(92,'Three quarter'),(110,'Three quarter'),(140,'Three quarter')]:
 s.frame_set(f);s.camera=bpy.data.objects['Camera • '+view];s.render.filepath=str(OUT/'qa'/('wave_arc_'+str(f)+'_'+view.replace(' ','_')+'.png'));bpy.ops.render.render(write_still=True)
