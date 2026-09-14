"""Render the native NLA preview once, then encode three clips and a reel."""
import bpy
import json
import shutil
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
FRAMES=OUT/'qa/animation_frames'
FRAMES.mkdir(exist_ok=True)
ANIM=OUT/'animations'
ANIM.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
assert bpy.data.objects.get('CATGRAY_RIG')
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.eevee.taa_render_samples=64
scene.render.resolution_x=720; scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.fps=24
scene.camera=bpy.data.objects['Camera • Three quarter']
scene.frame_start=1; scene.frame_end=240
scene.render.filepath=str(FRAMES/'frame_')
if '--encode-only' not in sys.argv:
    print('RENDER_ANIMATION_FRAMES',240,flush=True)
    bpy.ops.render.render(animation=True)
shutil.copy2(FRAMES/'frame_0126.png',OUT/'preview_animation.png')

encoding=bpy.data.scenes.new('Video encoding • rendered animation')
encoding.render.resolution_x=720; encoding.render.resolution_y=720
encoding.render.resolution_percentage=100; encoding.render.fps=24
encoding.view_settings.view_transform='Standard'
encoding.view_settings.look='None'
encoding.render.use_sequencer=True
editor=encoding.sequence_editor_create()
strip=editor.strips.new_image('CatGray animation',str(FRAMES/'frame_0001.png'),channel=1,frame_start=1)
for frame in range(2,241): strip.elements.append(f'frame_{frame:04d}.png')
encoding.render.image_settings.media_type='VIDEO'
encoding.render.image_settings.file_format='FFMPEG'
encoding.render.ffmpeg.format='MPEG4'; encoding.render.ffmpeg.codec='H264'
encoding.render.ffmpeg.constant_rate_factor='HIGH'
encoding.render.ffmpeg.ffmpeg_preset='GOOD'
encoding.render.ffmpeg.audio_codec='NONE'
videos=[]
for name,start,end in [('Idle_Breathe',1,72),('Wave',73,168),('Walk_InPlace',169,240),('CatGray_Animation_Preview',1,240)]:
    encoding.frame_start=start; encoding.frame_end=end
    destination=ANIM/(name+'.mp4')
    encoding.render.filepath=str(destination)
    print('ENCODE_VIDEO',name,flush=True)
    bpy.ops.render.render(animation=True,scene=encoding.name)
    if not destination.exists():
        candidates=list(ANIM.glob(name+'*.mp4'))
        if len(candidates)==1: candidates[0].rename(destination)
    assert destination.exists() and destination.stat().st_size>10000
    videos.append({'file':str(destination.relative_to(OUT)),'frames':end-start+1,
                   'duration_seconds':(end-start+1)/24,'resolution':[720,720],
                   'bytes':destination.stat().st_size})

# Decode each delivered movie through Blender's video reader, then decode
# a mid-wave frame to an image for final visual verification.
decode=bpy.data.scenes.new('Video playback verification')
decode.render.resolution_x=720; decode.render.resolution_y=720
decode.render.resolution_percentage=100; decode.render.fps=24
decode.view_settings.view_transform='Standard'; decode.view_settings.look='None'
decode.render.use_sequencer=True
movies=decode.sequence_editor_create()
for item in videos:
    movie=movies.strips.new_movie('Verify '+item['file'],str(OUT/item['file']),channel=1,frame_start=1)
    item['decoded_frames']=int(movie.frame_duration)
    assert item['decoded_frames']==item['frames'],item
    movies.strips.remove(movie)
movie=movies.strips.new_movie('Verify reel',str(ANIM/'CatGray_Animation_Preview.mp4'),channel=1,frame_start=1)
# Still renders use the window's current frame; select the decoding scene
# explicitly rather than inheriting the completed reel's final frame.
bpy.context.window.scene=decode
decode.frame_set(126)
decode.render.image_settings.file_format='PNG'
decode.render.filepath=str(OUT/'qa/video_decoded_wave.png')
bpy.ops.render.render(write_still=True,scene=decode.name)
import numpy as np
def image_pixels(path):
    image=bpy.data.images.load(str(path),check_existing=False)
    values=np.empty(len(image.pixels),dtype=np.float32)
    image.pixels.foreach_get(values)
    bpy.data.images.remove(image)
    return values.reshape(-1,4)[:,:3]
pixel_error=float(np.mean(np.abs(image_pixels(OUT/'preview_animation.png')-
    image_pixels(OUT/'qa/video_decoded_wave.png'))))
assert pixel_error<.015, ('Encoded wave differs from source frame',pixel_error)
(OUT/'qa/animation_video_verification.json').write_text(json.dumps({'passed':True,'videos':videos,
    'reel_frame_126_mean_rgb_error':pixel_error},indent=2))
shutil.copy2(ANIM/'Wave.mp4',ANIM/'Wave_v10.mp4')
# The delivered videos and decoded/poster frames are retained. Temporary
# image sequences are generated solely for encoding, so remove them now.
for path in FRAMES.glob('frame_*.png'): path.unlink()
FRAMES.rmdir()
print('ANIMATION_VIDEOS_COMPLETE',json.dumps(videos),flush=True)
