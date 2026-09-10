import bpy
for kind,scene in [('context',bpy.context.scene),('new',bpy.data.scenes.new('Encoding'))]:
 print('SCENE',kind)
 for obj in [scene.render,scene.render.image_settings,scene.render.ffmpeg]:
  print('PROPERTIES',[(p.identifier,p.type) for p in obj.bl_rna.properties if any(x in p.identifier for x in ['format','type','media','ffmpeg'])])
 try:
  scene.render.image_settings.file_format='FFMPEG'
  print('FFMPEG_SUCCESS')
 except Exception as e: print('FFMPEG_ERROR',str(e))
 bpy.context.window.scene=scene
 try:
  scene.render.image_settings.file_format='FFMPEG'
  print('ACTIVE_FFMPEG_SUCCESS')
 except Exception as e: print('ACTIVE_FFMPEG_ERROR',str(e))
