"""Render unique action frames, encode loops/reel, and check decoded movies."""
import hashlib
import json
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

from voxel_model import ROOT,NAME
from rig_voxel import RIG,FPS,CLIPS,set_action
from rig_voxel import rest_pose
from facial_voxel import select_states

FRAMES = ROOT/"qa/animation_frames"
ANIMATIONS = ROOT/"animations"


def setup(resolution=720,closeup=False):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 32
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.fps,scene.render.fps_base = FPS,1
    bpy.data.objects["Studio floor"].hide_render = False
    camera = bpy.data.objects.get("Camera_animation")
    if camera is None:
        camera = bpy.data.objects.new("Camera_animation",bpy.data.cameras.new("Animation camera"))
        bpy.context.scene.collection.objects.link(camera)
    camera.data.type,camera.data.ortho_scale = "ORTHO",4.6 if closeup else 6.7
    camera.location = (2.8,-14,4.4) if closeup else (7,-12,7.0)
    target = (0,-.1,3.12) if closeup else (0,0,2.7)
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera = camera
    return scene


def preview_poses():
    scene = setup(640)
    rig = bpy.data.objects[RIG]
    destination = ROOT/"previews"
    for action,frame,label in (
        ("Walk_InPlace",1,"walk_contact"),("Walk_InPlace",13,"walk_passing"),
        ("Run_InPlace",1,"run_contact"),("Run_InPlace",8,"run_flight"),
        ("Jump",9,"jump_crouch"),("Jump",23,"jump_apex"),("Jump",36,"jump_landing")):
        set_action(rig,action)
        scene.frame_set(frame)
        scene.render.filepath = str(destination/(label+".png"))
        bpy.ops.render.render(write_still=True)
    camera = scene.camera
    camera.location = (12,-3,4.5)
    camera.rotation_euler = (Vector((0,0,2.6))-camera.location).to_track_quat("-Z","Y").to_euler()
    for action,frame,label in (("Walk_InPlace",25,"walk_side"),("Run_InPlace",13,"run_side"),("Jump",23,"jump_side")):
        set_action(rig,action)
        scene.frame_set(frame)
        scene.render.filepath = str(destination/(label+".png"))
        bpy.ops.render.render(write_still=True)
    setup(640,closeup=True)
    for clip in CLIPS:
        if clip["group"] == "body":
            continue
        set_action(rig,clip["name"])
        scene.frame_set(clip["poster"])
        scene.render.filepath = str(destination/(clip["name"]+"_pose.png"))
        bpy.ops.render.render(write_still=True)
    rest_pose(rig)
    for label,eyes,mouth in (("neutral","Open","Neutral"),("half","Half","Neutral"),
                             ("closed","Closed","Closed"),("mouth_a","Open","A"),
                             ("mouth_e","Open","E"),("mouth_o","Open","O")):
        select_states(eyes,mouth)
        bpy.context.view_layer.update()
        scene.render.filepath = str(destination/("face_"+label+".png"))
        bpy.ops.render.render(write_still=True)
    expression_gallery()
    sidewall_gallery()


def sidewall_gallery():
    """Keep an oblique closeup of open/cleared eyes and changing mouth shapes."""
    scene = setup(640,closeup=True)
    rest_pose(bpy.data.objects[RIG])
    scene.camera.location = (10,-12,4.4)
    scene.camera.rotation_euler = (Vector((0,-.3,3.0))-scene.camera.location).to_track_quat("-Z","Y").to_euler()
    scene.camera.data.ortho_scale = 3.65
    states = (("neutral","Open","Neutral"),("half","Half","E"),("closed","Closed","Closed"),
              ("mouth_o","Open","O"),("joy","Joy","Joy"),("angry","Angry","Angry"))
    size,gap = 640,12
    width,height = 3*size+2*gap,2*size+gap
    pixels = np.ones((height,width,4),dtype=np.float32)
    for index,(label,eyes,mouth) in enumerate(states):
        select_states(eyes,mouth)
        bpy.context.view_layer.update()
        path = ROOT/"previews"/("face_side_"+label+".png")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        source = bpy.data.images.load(str(path),check_existing=False)
        data = np.empty(size*size*4,dtype=np.float32)
        source.pixels.foreach_get(data)
        row,column = divmod(index,3)
        y,x = (1-row)*(size+gap),column*(size+gap)
        pixels[y:y+size,x:x+size] = data.reshape(size,size,4)
        bpy.data.images.remove(source)
    output = bpy.data.images.new("Oblique facial states",width=width,height=height)
    output.pixels.foreach_set(pixels.ravel())
    output.filepath_raw = str(ROOT/"previews/face_sidewalls.png")
    output.file_format = "PNG"
    output.save()
    bpy.data.images.remove(output)
    select_states()


def expression_gallery():
    size,gap = 640,12
    width = 2*size+gap
    pixels = np.ones((width,width,4),dtype=np.float32)
    for expression,row,column in (("Joy",1,0),("Sad",1,1),("Pain",0,0),("Angry",0,1)):
        source = bpy.data.images.load(str(ROOT/"previews"/("Emotion_"+expression+"_pose.png")),check_existing=False)
        data = np.empty(size*size*4,dtype=np.float32)
        source.pixels.foreach_get(data)
        y,x = row*(size+gap),column*(size+gap)
        pixels[y:y+size,x:x+size] = data.reshape(size,size,4)
        bpy.data.images.remove(source)
    output = bpy.data.images.new("Four emotions",width=width,height=width)
    output.pixels.foreach_set(pixels.ravel())
    output.filepath_raw = str(ROOT/"previews/expressions.png")
    output.file_format = "PNG"
    output.save()
    bpy.data.images.remove(output)


def pixel_array(path):
    image = bpy.data.images.load(str(path),check_existing=False)
    pixels = np.empty(len(image.pixels),dtype=np.float32)
    image.pixels.foreach_get(pixels)
    result = pixels.reshape(-1,4)[:,:3].copy()
    bpy.data.images.remove(image)
    return result


def encoding_scene(name):
    scene = bpy.data.scenes.new(name)
    scene.render.resolution_x = scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.fps,scene.render.fps_base = FPS,1
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.use_sequencer = True
    scene.sequence_editor_create()
    return scene


def videos_plan():
    plan,reel = [],[]
    for clip in CLIPS:
        sequence = [f"{clip['name']}_{f:04d}.png" for f in range(1,clip["frames"]+1)]*clip["repeat"]
        plan.append((clip["name"],sequence))
        reel.extend(sequence)
    plan.append((NAME+"_Animation_Preview",reel))
    return plan


def encode():
    ANIMATIONS.mkdir(exist_ok=True)
    scene = encoding_scene("Encode voxel animation")
    editor = scene.sequence_editor
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.audio_codec = "NONE"
    results = []
    for name,sequence in videos_plan():
        if not all((FRAMES/file).is_file() for file in sequence):
            raise RuntimeError("Missing source frames for "+name)
        strip = editor.strips.new_image(name,str(FRAMES/sequence[0]),channel=1,frame_start=1)
        for filename in sequence[1:]:
            strip.elements.append(filename)
        scene.frame_start,scene.frame_end = 1,len(sequence)
        scene.render.filepath = str(ANIMATIONS/(name+".mp4"))
        bpy.ops.render.render(animation=True,scene=scene.name)
        editor.strips.remove(strip)
        results.append({"file":name+".mp4","frames":len(sequence),"duration_seconds":len(sequence)/FPS,
                        "fps":FPS,"resolution":[720,720],"codec":"H.264"})
    (ROOT/"qa/video_manifest.json").write_text(json.dumps({"videos":results},indent=2)+"\n")
    bpy.data.scenes.remove(scene)


def verify_videos():
    manifest = json.loads((ROOT/"qa/video_manifest.json").read_text())
    scene = encoding_scene("Decode voxel animation")
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    original_scene = bpy.context.window.scene
    bpy.context.window.scene = scene
    checks = []
    try:
        for item in manifest["videos"]:
            path = ANIMATIONS/item["file"]
            movie = scene.sequence_editor.strips.new_movie(item["file"],str(path),channel=1,frame_start=1)
            decoded = int(movie.frame_duration)
            # Every delivered clip has a retained uncompressed representative frame.
            if path.stem == NAME+"_Animation_Preview":
                samples,start = [],0
                for clip in CLIPS:
                    samples.append((start+clip["poster"],clip["name"]))
                    start += clip["frames"]*clip["repeat"]
            else:
                clip = next(c for c in CLIPS if c["name"] == path.stem)
                samples = [(clip["poster"],path.stem)]
            comparisons = []
            for index,(sample,source) in enumerate(samples):
                scene.frame_set(sample)
                suffix = "" if index == 0 else "_"+source
                decoded_path = ROOT/"qa"/(path.stem+suffix+"_decoded.png")
                scene.render.filepath = str(decoded_path)
                bpy.ops.render.render(write_still=True,scene=scene.name)
                reference = ROOT/"previews"/(source+"_poster.png")
                error = float(np.mean(np.abs(pixel_array(reference)-pixel_array(decoded_path))))
                comparisons.append({"frame":sample,"source_action":source,"mean_rgb_error":error})
            error = max(c["mean_rgb_error"] for c in comparisons)
            checks.append({"file":item["file"],"expected_frames":item["frames"],"decoded_frames":decoded,
                           "mean_rgb_error":error,"comparisons":comparisons,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                           "passed":decoded == item["frames"] and error < .02 and path.stat().st_size>10000})
            scene.sequence_editor.strips.remove(movie)
    finally:
        bpy.context.window.scene = original_scene
        bpy.data.scenes.remove(scene)
    report = {"passed":all(c["passed"] for c in checks),"videos":checks}
    (ROOT/"qa/video_verification.json").write_text(json.dumps(report,indent=2)+"\n")
    if not report["passed"]:
        raise RuntimeError("Video verification failed: "+json.dumps(report))
    return report


def render(encode_only=False):
    FRAMES.mkdir(parents=True,exist_ok=True)
    scene = setup()
    rig = bpy.data.objects[RIG]
    if not encode_only:
        for clip in CLIPS:
            setup(closeup=clip["group"] != "body")
            set_action(rig,clip["name"])
            for frame in range(1,clip["frames"]+1):
                scene.frame_set(frame)
                scene.render.filepath = str(FRAMES/f"{clip['name']}_{frame:04d}.png")
                bpy.ops.render.render(write_still=True)
    # Retained samples allow verifying delivered videos after frame cleanup.
    for clip in CLIPS:
        name,sample = clip["name"],clip["poster"]
        (ROOT/"previews"/(name+"_poster.png")).write_bytes((FRAMES/f"{name}_{sample:04d}.png").read_bytes())
    (ROOT/"previews"/(NAME+"_Animation_Preview_poster.png")).write_bytes((FRAMES/"Walk_InPlace_0013.png").read_bytes())
    encode()
    verify_videos()
    for path in FRAMES.glob("*.png"):
        path.unlink()
    FRAMES.rmdir()
    print("ANIMATION_MEDIA_COMPLETE",flush=True)
