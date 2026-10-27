"""Blender: export a fixed-camera, transparent PRD v1 Sprite character pack.
Run: blender -b -t 4 --python scripts/export_desktop_pet.py
The source blend is read only; four baked state Actions are saved separately.
"""
import json
import math
import shutil
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from rig_voxel import RIG, rest_pose, set_action
from facial_voxel import select_states
import desktop_pet_actions as pet_actions

OUT = ROOT / 'desktop_pet'
W, H, FPS, COLS = 192, 208, 8, 16
# duration in seconds, source action (None = authored procedural loop), loop
PLAN = [('idle',4,None,True), ('thinking',3,'Pet_Thinking',True),
        ('working',2,'Pet_Working',True), ('waiting',4,'Pet_Waiting',True),
        ('speaking',3,'Pet_Speaking',True), ('success',3,None,True),
        ('error',3,None,True), ('walk',4,'Walk_InPlace',True),
        ('run',2,'Run_InPlace',True), ('jump',2,'Jump',False)]


def rotate(rig, name, x=0, y=0, z=0):
    rig.pose.bones[name].rotation_quaternion = (
        Quaternion((0,0,1), math.radians(z)) @
        Quaternion((0,1,0), math.radians(y)) @
        Quaternion((1,0,0), math.radians(x)))


def pose(rig, name, t, duration, action):
    if action:
        pet_actions.activate(rig, action)
        # Sample original 24 FPS clips, excluding their duplicate closure frame.
        period = {'Walk_InPlace':32/24, 'Run_InPlace':16/24}.get(action,duration)
        bpy.context.scene.frame_set(1 + int(round((t % period)*24)))
        return
    for obj in bpy.data.collections[pet_actions.PROP_COLLECTION].objects:
        obj.hide_render = obj.hide_viewport = True
    rest_pose(rig)
    rig.data.pose_position = "POSE"
    phase = 2*math.pi*t/duration
    wave = math.sin(phase)
    breathe = (1-math.cos(phase))*.012
    rig.pose.bones['Body'].scale = (1, 1, 1+breathe)
    for i in range(1,4):
        rotate(rig, f'Tail.{i:02d}', y=4*math.sin(phase+i*.4))
    eyes = 'Half' if .68 < t/duration < .72 else 'Closed' if .72 <= t/duration < .76 else 'Open'
    mouth = 'Neutral'
    if name == 'success':
        eyes,mouth='Joy','Joy'
        rotate(rig,'Head',y=3*wave)
        rotate(rig,'UpperArm.L',z=-22-5*wave)
        rotate(rig,'UpperArm.R',z=22+5*wave)
    elif name == 'error':
        eyes,mouth='Sad','Sad'
        rotate(rig,'Head',x=5,z=3*wave)
        rotate(rig,'Ear.L',y=-5)
        rotate(rig,'Ear.R',y=5)
    select_states(eyes,mouth)
    bpy.context.view_layer.update()


def main():
    OUT.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'CatGray_Voxel.blend'))
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = True
    scene.render.resolution_x,scene.render.resolution_y = W,H
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.use_file_extension = True
    scene.render.use_sequencer = False
    if bpy.data.objects.get('Studio floor'):
        bpy.data.objects['Studio floor'].hide_render = True
    camera = bpy.data.objects.new('DesktopPetCamera',bpy.data.cameras.new('DesktopPetCamera'))
    scene.collection.objects.link(camera)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 6.6
    camera.location = (6,-16,7.2)
    target = Vector((0,0,2.85))
    camera.rotation_euler = (target-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera = camera
    rig = bpy.data.objects[RIG]
    pet_actions.build(rig)
    action_checks = pet_actions.verify(rig)
    (OUT/'action_verification.json').write_text(json.dumps(action_checks,indent=2)+'\n')
    pet_actions.activate(rig,'Pet_Working')
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    pet_actions.playlist(rig)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CatGray_DesktopPet.blend'))
    pet_actions.activate(rig,'Pet_Working')
    if '--review' in sys.argv:
        scene.render.resolution_x,scene.render.resolution_y=384,416
        scene.cycles.samples=16
        folder=OUT/'review'
        folder.mkdir(exist_ok=True)
        for name,duration in pet_actions.DURATIONS.items():
            for j,t in enumerate((0,.25,.5,.75)):
                pose(rig,name.lower(),t*duration,duration,'Pet_'+name)
                scene.render.filepath=str(folder/f'{name}_{j}.png')
                bpy.ops.render.render(write_still=True)
        return
    frames_dir = OUT/'frames'
    frames_dir.mkdir(exist_ok=True)
    animations,files,bounds = {},[],{}
    smoke = '--smoke' in sys.argv
    for name,duration,action,loop in PLAN:
        count = int(duration*FPS)
        animations[name] = dict(startFrame=len(files),frameCount=count,fps=FPS,loop=loop)
        for i in range(count):
            path = frames_dir/f'{name}_{i:03d}.png'
            if '--pack-only' not in sys.argv and not ('--speech-only' in sys.argv and name != 'speaking' and path.is_file()):
                pose(rig,name,i/FPS,duration,action)
                scene.render.filepath = str(path)
                bpy.ops.render.render(write_still=True)
            if not path.is_file():
                raise RuntimeError(f'Missing frame: {path}')
            files.append(path)
            print(f'DESKTOP_PET {name} {i+1}/{count}',flush=True)
            if smoke:
                return
    rows = math.ceil(len(files)/COLS)
    atlas = np.zeros((rows*H,COLS*W,4),dtype=np.float32)
    contact = np.zeros((2*H,5*W,4),dtype=np.float32)
    for index,path in enumerate(files):
        source = bpy.data.images.load(str(path),check_existing=False)
        data = np.empty(W*H*4,dtype=np.float32)
        source.pixels.foreach_get(data)
        data = data.reshape(H,W,4)
        ys,xs = np.where(data[:,:,3]>.01)
        if not len(xs) or xs.min()==0 or xs.max()==W-1 or ys.min()==0 or ys.max()==H-1:
            raise RuntimeError(f'Empty or clipped frame: {path.name}')
        bounds[path.name] = [int(xs.min()),int(H-1-ys.max()),int(xs.max()+1),int(H-ys.min())]
        row,col=divmod(index,COLS)
        atlas[(rows-1-row)*H:(rows-row)*H,col*W:(col+1)*W]=data
        for j,(name,*_) in enumerate(PLAN):
            info=animations[name]
            if index == info['startFrame']+info['frameCount']//2:
                r,c=divmod(j,5)
                contact[(1-r)*H:(2-r)*H,c*W:(c+1)*W]=data
        bpy.data.images.remove(source)
    def save(name,data):
        h,w,_=data.shape
        img=bpy.data.images.new(name,width=w,height=h,alpha=True)
        img.pixels.foreach_set(data.ravel())
        img.filepath_raw=str(OUT/name)
        img.file_format='PNG'
        img.save()
        bpy.data.images.remove(img)
    save('spritesheet.png',atlas)
    save('contact_sheet.png',contact)
    shutil.copyfile(files[0],OUT/'preview.png')
    manifest=dict(schemaVersion=1,id='catgray-voxel',name='CatGray Voxel',type='sprite',
                  asset='spritesheet.png',frameSize=[W,H],anchor=[.5,.92],animations=animations,
                  stateMap={s:s.lower() for s in ['Idle','Thinking','Working','Waiting','Speaking','Success','Error']},
                  licenseFile='LICENSE.txt')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    report=dict(passed=True,frames=len(files),atlasSize=[COLS*W,rows*H],
                decodedBytes=atlas.nbytes//4,frameBounds=bounds,
                checks=['all frames nonempty','no alpha bounds touch frame edges','uniform camera and cell size'],
                renderer=bpy.app.version_string)
    assert max(COLS*W,rows*H)<=4096 and report['decodedBytes']<=128*1024*1024
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DESKTOP_PET COMPLETE',flush=True)

if __name__=='__main__':
    main()
