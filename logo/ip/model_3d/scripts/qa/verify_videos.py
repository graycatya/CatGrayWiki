"""Decode delivered videos without rerendering the 3D animation."""
import bpy,json
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
scene.render.resolution_x=scene.render.resolution_y=720
scene.render.resolution_percentage=100;scene.render.fps=24
scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
scene.render.use_sequencer=True;scene.render.image_settings.file_format='PNG'
editor=scene.sequence_editor_create();report=[]
for name,frames in [('Idle_Breathe',72),('Wave',96),('Walk_InPlace',72),('CatGray_Animation_Preview',240),('Wave_Side',96)]:
    movie=editor.strips.new_movie(name,str(ROOT/'animations'/f'{name}.mp4'),channel=1,frame_start=1)
    assert int(movie.frame_duration)==frames,(name,movie.frame_duration)
    report.append({'file':name+'.mp4','frames':frames,'seconds':frames/24})
    editor.strips.remove(movie)
def pixels(path):
    image=bpy.data.images.load(str(path),check_existing=False)
    values=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(values)
    bpy.data.images.remove(image);return values.reshape(-1,4)[:,:3]
comparisons=[]
for name,frame,source,output in [('CatGray_Animation_Preview',126,'previews/preview_animation.png','qa/video_decoded_wave.png'),('Wave_Side',54,'qa/wave_arc_side.png','qa/wave_side_decoded.png')]:
    movie=editor.strips.new_movie(name,str(ROOT/'animations'/f'{name}.mp4'),channel=1,frame_start=1)
    scene.frame_set(frame);scene.render.filepath=str(ROOT/output);bpy.ops.render.render(write_still=True)
    error=float(np.mean(np.abs(pixels(ROOT/source)-pixels(ROOT/output))))
    assert error<.015,(name,error)
    comparisons.append({'video':name,'frame':frame,'mean_rgb_error':error});editor.strips.remove(movie)
(ROOT/'qa/video_verification.json').write_text(json.dumps({'passed':True,'videos':report,'comparisons':comparisons},indent=2))
print('VIDEOS_VERIFIED',report)
