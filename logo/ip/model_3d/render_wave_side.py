"""Render the side-view wave and compare its decoded frame to the source."""
import bpy,json,shutil
import numpy as np
from pathlib import Path
OUT=Path(__file__).resolve().parent
FRAMES=OUT/'qa/wave_side_frames';FRAMES.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
s=bpy.context.scene
s.camera=bpy.data.objects['Camera • Side']
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=64
s.render.resolution_x=s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.frame_start=73;s.frame_end=168;s.render.filepath=str(FRAMES/'frame_')
bpy.ops.render.render(animation=True)
shutil.copy2(FRAMES/'frame_0126.png',OUT/'qa/wave_arc_side.png')
encoding=bpy.data.scenes.new('Side wave encoding');bpy.context.window.scene=encoding
encoding.render.resolution_x=encoding.render.resolution_y=720
encoding.render.resolution_percentage=100;encoding.render.fps=24
encoding.view_settings.view_transform='Standard';encoding.view_settings.look='None'
encoding.render.use_sequencer=True
strip=encoding.sequence_editor_create().strips.new_image('Side wave',str(FRAMES/'frame_0073.png'),channel=1,frame_start=1)
for f in range(74,169):strip.elements.append(f'frame_{f:04d}.png')
encoding.frame_start=1;encoding.frame_end=96
encoding.render.image_settings.media_type='VIDEO';encoding.render.image_settings.file_format='FFMPEG'
encoding.render.ffmpeg.format='MPEG4';encoding.render.ffmpeg.codec='H264'
encoding.render.ffmpeg.constant_rate_factor='HIGH';encoding.render.ffmpeg.ffmpeg_preset='GOOD';encoding.render.ffmpeg.audio_codec='NONE'
video=OUT/'animations/Wave_Side.mp4';encoding.render.filepath=str(video)
bpy.ops.render.render(animation=True)
assert video.exists()
decode=bpy.data.scenes.new('Side wave decode');bpy.context.window.scene=decode
decode.render.resolution_x=decode.render.resolution_y=720;decode.render.resolution_percentage=100;decode.render.fps=24
decode.view_settings.view_transform='Standard';decode.view_settings.look='None';decode.render.use_sequencer=True
movie=decode.sequence_editor_create().strips.new_movie('Verify side',str(video),channel=1,frame_start=1)
assert int(movie.frame_duration)==96
decode.frame_set(54);decode.render.image_settings.file_format='PNG';decode.render.filepath=str(OUT/'qa/wave_side_decoded.png')
bpy.ops.render.render(write_still=True)
def pixels(path):
    im=bpy.data.images.load(str(path),check_existing=False);p=np.empty(len(im.pixels),dtype=np.float32)
    im.pixels.foreach_get(p);bpy.data.images.remove(im);return p.reshape(-1,4)[:,:3]
error=float(np.mean(np.abs(pixels(OUT/'qa/wave_arc_side.png')-pixels(OUT/'qa/wave_side_decoded.png'))))
assert error<.015,error
shutil.copy2(video,OUT/'animations/Wave_Side_v10.mp4')
(OUT/'qa/side_wave_video_verification.json').write_text(json.dumps({'passed':True,'frames':96,'seconds':4,'source_frame':126,'video_frame':54,'mean_rgb_error':error},indent=2))
for f in FRAMES.glob('frame_*.png'):f.unlink()
FRAMES.rmdir()
print('SIDE_WAVE_VIDEO_COMPLETE',error,flush=True)
