import bpy,json
from pathlib import Path
out=Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(out/'revisions/v7/CatGray_IP.blend'))
for obj in bpy.data.collections['CATGRAY • Character'].objects:
 print('OBJECT',obj.name,obj.type,len(obj.data.vertices) if obj.type=='MESH' else '',list(obj.location),[m.type for m in obj.modifiers])
for p in bpy.ops.export_scene.gltf.get_rna_type().properties:
 if any(t in p.identifier for t in ('anim','bone','apply','influence')):
  print('EXPORT_API',p.identifier,p.default if hasattr(p,'default') else '',[i.identifier for i in p.enum_items] if p.type=='ENUM' else '')
print('RENDER_FORMATS',[i.identifier for i in bpy.context.scene.render.image_settings.bl_rna.properties['file_format'].enum_items])
print('FFMPEG',hasattr(bpy.context.scene.render,'ffmpeg'),bpy.app.build_options.codec_ffmpeg)

editor=bpy.context.scene.sequence_editor_create()
print('SEQUENCE_API', [a for a in dir(editor) if a in ('strips','sequences','sequences_all')])
print('EEVEE_OPTIONS', [p.identifier for p in bpy.context.scene.eevee.bl_rna.properties] if hasattr(bpy.context.scene,'eevee') else 'none')
