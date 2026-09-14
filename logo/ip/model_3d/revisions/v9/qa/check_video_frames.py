import bpy
from pathlib import Path
out=Path(__file__).resolve().parent.parent
scene=bpy.context.scene
scene.render.resolution_x=720; scene.render.resolution_y=720
scene.render.resolution_percentage=100; scene.render.fps=24
scene.view_settings.view_transform='Standard'; scene.view_settings.look='None'
editor=scene.sequence_editor_create()
movie=editor.strips.new_movie('Reel',str(out/'animations/CatGray_Animation_Preview.mp4'),channel=1,frame_start=1)
print('MOVIE',movie.frame_start,movie.frame_final_start,movie.frame_final_end,movie.frame_duration)
scene.render.image_settings.file_format='PNG'
for frame in [1,126,190]:
 scene.frame_set(frame)
 scene.render.filepath=str(out/'qa'/f'video_check_{frame}.png')
 bpy.ops.render.render(write_still=True)
image=editor.strips.new_image('Sequence diagnostic',str(out/'preview_animation.png'),channel=2,frame_start=1)
for i in range(3): image.elements.append('preview_animation.png')
print('IMAGE_SEQUENCE',len(image.elements),image.frame_duration,image.frame_final_start,image.frame_final_end)
