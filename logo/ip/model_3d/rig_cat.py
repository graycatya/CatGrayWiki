"""Build an editable rig and three reusable animation clips from approved v7."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion

OUT=Path(__file__).resolve().parent
FPS=24
bpy.ops.wm.open_mainfile(filepath=str(OUT/'revisions/v7/CatGray_IP.blend'))
scene=bpy.context.scene
scene.render.fps=FPS
scene.render.fps_base=1
bpy.context.preferences.filepaths.save_version=0
character=bpy.data.collections['CATGRAY • Character']
root=next(o for o in character.objects if o.type=='EMPTY')

# Convert the already evaluated curve surfaces without changing their shape.
for obj in list(character.objects):
    if obj.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True); bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target='MESH')
skins=[o for o in character.objects if o.type=='MESH']
rest_vertices={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in skins}

data=bpy.data.armatures.new('CatGray • Skeleton')
rig=bpy.data.objects.new('CATGRAY_RIG',data)
character.objects.link(rig)
rig.parent=root
rig.show_in_front=False
data.display_type='STICK'
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None,deform=True,connect=False):
    b=data.edit_bones.new(name); b.head=head; b.tail=tail
    b.use_deform=deform
    b.align_roll(Vector((0,-1,0)))
    if parent: b.parent=data.edit_bones[parent]
    b.use_connect=connect
    return b

bone('CTRL_Root',(0,0,0),(0,0,.28),deform=False)
bone('Pelvis',(0,0,.64),(0,0,.96),'CTRL_Root')
bone('Spine',(0,0,.96),(0,0,1.30),'Pelvis',connect=True)
bone('Chest',(0,0,1.30),(0,0,1.59),'Spine',connect=True)
bone('Neck',(0,0,1.59),(0,0,1.90),'Chest',connect=True)
bone('Head',(0,0,1.90),(0,0,3.75),'Neck',connect=True)
for sign,side in [(-1,'L'),(1,'R')]:
    shoulder=(sign*.535,.029,1.58125)
    elbow=(sign*.838,0,1.081)
    wrist=(sign*.756,-.064,.7015)
    bone('Clavicle.'+side,(sign*.16,0,1.54),shoulder,'Chest')
    bone('UpperArm.'+side,shoulder,elbow,'Clavicle.'+side,connect=True)
    bone('Forearm.'+side,elbow,wrist,'UpperArm.'+side,connect=True)
    bone('Hand.'+side,wrist,(sign*.718,-.090,.558),'Forearm.'+side,connect=True)
    bone('ElbowSoft.'+side,elbow,wrist,'UpperArm.'+side,connect=True)
    bone('WristSoft.'+side,wrist,(sign*.718,-.090,.558),'Forearm.'+side,connect=True)
    hip=(sign*.278,.015,.65)
    knee=(sign*.278,-.110,.34)
    ankle=(sign*.278,-.100,.12)
    toe=(sign*.278,-.295,.10)
    bone('Thigh.'+side,hip,knee,'Pelvis')
    bone('Shin.'+side,knee,ankle,'Thigh.'+side,connect=True)
    bone('Foot.'+side,ankle,toe,'Shin.'+side,connect=True)
    bone('Toe.'+side,toe,(sign*.278,-.37,.095),'Foot.'+side,connect=True)
    bone('KneeSoft.'+side,knee,ankle,'Thigh.'+side,connect=True)
    bone('AnkleSoft.'+side,ankle,toe,'Shin.'+side,connect=True)
    bone('CTRL_Foot_IK.'+side,ankle,toe,'CTRL_Root',deform=False)
    bone('CTRL_Knee_Pole.'+side,(sign*.278,-.95,.34),(sign*.278,-.95,.48),'CTRL_Root',deform=False)
    bone('Ear.'+side,(sign*1.47,.25,3.69),(sign*1.55,.34,4.51),'Head')

tail_points=[(-.10,.28,.555),(-.36,.65,.575),(-.79,1.03,.661),
             (-1.18,1.27,.862),(-1.36,1.45,1.17),(-1.30,1.53,1.34),
             (-1.12,1.60,1.355),(-1.02,1.63,1.20)]
tail_points=[Vector((x*1.08,y*1.06,z*1.15)) for x,y,z in tail_points]
for i,(a,b) in enumerate(zip(tail_points,tail_points[1:])):
    bone(f'Tail.{i+1:02d}',a,b,'Pelvis' if i==0 else f'Tail.{i:02d}',connect=i>0)
bpy.ops.object.mode_set(mode='OBJECT')

control_collection=data.collections.new('控制 • Root / Feet / Knees')
fk_collection=data.collections.new('姿态 • Head / Body / Arms / Tail')
leg_collection=data.collections.new('腿部变形 • IK driven')
for b in data.bones:
    if b.name.startswith('CTRL_'):
        control_collection.assign(b); b.color.palette='THEME04'
    elif b.name.startswith(('Thigh.','Shin.','Foot.','Toe.','ElbowSoft.','WristSoft.','KneeSoft.','AnkleSoft.')):
        leg_collection.assign(b); b.color.palette='THEME03'
    else:
        fk_collection.assign(b); b.color.palette='THEME02'
leg_collection.is_visible=False
for pb in rig.pose.bones:
    pb.rotation_mode='QUATERNION'
    pb.ik_stretch=0

ik_calibration=[]
for side in ('L','R'):
    ik=rig.pose.bones['Shin.'+side].constraints.new('IK')
    ik.name='Foot planting • two-bone IK'
    ik.target=rig; ik.subtarget='CTRL_Foot_IK.'+side
    ik.pole_target=rig; ik.pole_subtarget='CTRL_Knee_Pole.'+side
    ik.chain_count=2; ik.use_stretch=False; ik.iterations=128
    best=None
    for angle in [0,math.pi/2,-math.pi/2,math.pi]:
        ik.pole_angle=angle; bpy.context.view_layer.update()
        err=(rig.pose.bones['Shin.'+side].head-data.bones['Shin.'+side].head_local).length
        if best is None or err<best[0]: best=(err,angle)
    ik.pole_angle=best[1]
    copy=rig.pose.bones['Foot.'+side].constraints.new('COPY_ROTATION')
    copy.name='Keep foot orientation from IK control'
    copy.target=rig; copy.subtarget='CTRL_Foot_IK.'+side
    copy.owner_space='WORLD'; copy.target_space='WORLD'
    ik_calibration.append({'side':side,'pole_angle':best[1],'rest_knee_error':best[0]})
    # Half-angle support joints distribute each bend over two transitions.
    # Their rotations are ordinary bones in GLB, preserving the round skin.
    for support,target in [('ElbowSoft','Forearm'),('WristSoft','Hand'),
                           ('KneeSoft','Shin'),('AnkleSoft','Foot')]:
        soften=rig.pose.bones[support+'.'+side].constraints.new('COPY_ROTATION')
        soften.name='Soft joint • half-angle bend'
        soften.target=rig; soften.subtarget=target+'.'+side
        soften.owner_space='LOCAL'; soften.target_space='LOCAL'; soften.influence=.5
bpy.context.view_layer.update()

def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a))); return t*t*(3-2*t)

def blend_centres(value,centres):
    if value<=centres[0][1]: return {centres[0][0]:1.}
    for (a,x),(b,y) in zip(centres,centres[1:]):
        if value<y:
            t=smooth(x,y,value); return {a:1-t,b:t}
    return {centres[-1][0]:1.}

tail_lengths=[0.]
for a,b in zip(tail_points,tail_points[1:]): tail_lengths.append(tail_lengths[-1]+(b-a).length)
tail_centres=[(f'Tail.{i+1:02d}',(a+b)/2) for i,(a,b) in enumerate(zip(tail_lengths,tail_lengths[1:]))]
def tail_station(p):
    nearest=(1e9,0.)
    for i,(a,b) in enumerate(zip(tail_points,tail_points[1:])):
        t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared))
        dist=(p-(a+(b-a)*t)).length_squared
        if dist<nearest[0]: nearest=(dist,tail_lengths[i]+t*(b-a).length)
    return nearest[1]

def weights(obj,p):
    x,y,z=p; name=obj.name
    if name.startswith(('Head ','Eye ','Face ')): return {'Head':1.}
    if name.startswith('Ear '):
        side='L' if x<0 else 'R'; f=smooth(3.67,4.10,z)
        return {'Head':1-f,'Ear.'+side:f}
    if name.startswith('Tail '):
        if 'rounded tip' in name: return {'Tail.07':1.}
        return blend_centres(tail_station(p),tail_centres)
    if name.startswith('Arm '):
        side='L' if x<0 else 'R'
        # Overlapping quadratic weights distribute elbow rotation over the
        # whole rounded joint, instead of short isolated support-bone bands.
        u=smooth(.78,1.43,z)
        palm=1-smooth(.59,.81,z)
        limb={'UpperArm.'+side:u*u,
              'ElbowSoft.'+side:2*u*(1-u),
              'Forearm.'+side:(1-u)**2*(1-palm),
              'Hand.'+side:(1-u)**2*palm}
        anchored=smooth(1.57,1.73,z)
        return {**{n:w*(1-anchored) for n,w in limb.items()},'Chest':anchored}
    if name.startswith('Body '):
        trunk=blend_centres(z,[('Pelvis',.75),('Spine',1.07),('Chest',1.43),('Neck',1.78)])
        legs=1-smooth(.38,.70,z)
        lateral=.30+.70*smooth(.10,.34,abs(x))
        legs*=1-(1-lateral)*smooth(.36,.56,z)
        result={n:w*(1-legs) for n,w in trunk.items()}
        halfwidth=.006+.11*smooth(.36,.76,z)
        right=smooth(-halfwidth,halfwidth,x)
        leg=blend_centres(z,[('Foot',.105),('AnkleSoft',.17),('Shin',.26),('KneeSoft',.36),('Thigh',.55)])
        for side,mix in [('L',1-right),('R',right)]:
            for part,w in leg.items():
                result[part+'.'+side]=w*mix*legs
        return result
    raise RuntimeError('No weight rule for '+name)

weight_report=[]
for obj in skins:
    world=obj.matrix_world.copy()
    obj.parent=rig
    obj.matrix_world=world
    obj.vertex_groups.clear()
    groups={b.name:obj.vertex_groups.new(name=b.name) for b in data.bones if b.use_deform}
    maximum=0; error=0
    for vertex,p in zip(obj.data.vertices,rest_vertices[obj.name]):
        values=sorted(((n,w) for n,w in weights(obj,p).items() if w>1e-7),key=lambda a:-a[1])[:4]
        total=sum(w for n,w in values)
        if total<1e-8: raise RuntimeError('Unweighted vertex '+obj.name)
        for name,w in values: groups[name].add([vertex.index],w/total,'REPLACE')
        maximum=max(maximum,len(values)); error=max(error,abs(sum(w/total for n,w in values)-1))
    # Subdivision before armature matches the geometry/weights sampled by glTF.
    modifier=obj.modifiers.new('CatGray • skeletal deformation','ARMATURE')
    modifier.object=rig
    modifier.use_deform_preserve_volume=False
    obj['rig_binding']='Normalized manual weights; maximum four influences; v7 rest silhouette'
    weight_report.append({'object':obj.name,'vertices':len(obj.data.vertices),
                          'maximum_influences':maximum,'normalization_error':error})

rig['version']='v9 • smooth arm weights, stable paw wave, unobstructed viewport'
rig['controls']='CTRL_Root; Pelvis/Spine/Chest/Head; arm FK; foot IK; knee poles; Ear.L/R; Tail.01-07'
rig['forward_axis']='-Y; Z up; 24 FPS'
root['revision']='v9: smooth wave and unobstructed viewport; approved v7 geometry'
root['production_note']='Editable skeletal rig and three actions. Foot IK, arm FK, segmented tail. No facial expression rig.'

def rotate(name,axis,degrees):
    rest=data.bones[name].matrix_local.to_quaternion()
    rig.pose.bones[name].rotation_quaternion=rest.inverted()@Quaternion(Vector(axis),math.radians(degrees))@rest

def locate(name,offset):
    rig.pose.bones[name].location=data.bones[name].matrix_local.to_3x3().inverted()@Vector(offset)

def neutral():
    for pb in rig.pose.bones: pb.matrix_basis=Matrix.Identity(4)

def idle_pose(t):
    phase=math.tau*t
    breath=(1-math.cos(phase))*.5
    locate('Pelvis',(0,0,.006*breath))
    rig.pose.bones['Chest'].scale=(1+.010*breath,1,1+.014*breath)
    rig.pose.bones['Head'].scale=(1/(1+.010*breath),1,1/(1+.014*breath))
    rotate('Head',(0,1,0),.7*math.sin(phase))
    for i in range(7):
        shift=i*.30
        rotate(f'Tail.{i+1:02d}',(0,0,1),.60*(math.sin(phase-shift)+math.sin(shift)))
    rotate('Ear.L',(0,1,0),.65*math.sin(phase)**3)
    rotate('Ear.R',(0,1,0),-.50*math.sin(phase)**3)

def wave_pose(t):
    idle_pose(t)
    envelope=smooth(0,.25,t)*(1-smooth(.78,1,t))
    wave_time=max(0,min(1,(t-.25)/.53))
    wiggle=math.sin(math.tau*2*wave_time)*math.sin(math.pi*wave_time)**2
    locate('Clavicle.R',(.09*envelope,-.05*envelope,0))
    rotate('UpperArm.R',(0,1,0),(-60+3*wiggle)*envelope)
    rotate('Forearm.R',(0,1,0),(-48+10*wiggle)*envelope)
    # Keep the mitten-shaped paw aligned with the forearm throughout the wave.
    rotate('Hand.R',(0,1,0),0)
    rest=data.bones['Head'].matrix_local.to_quaternion()
    q=Quaternion(Vector((0,0,1)),math.radians(3*envelope))@Quaternion(Vector((0,1,0)),math.radians(-2*envelope))
    rig.pose.bones['Head'].rotation_quaternion=rest.inverted()@q@rest

def walk_pose(t):
    phase=math.tau*t
    locate('Pelvis',(.010*math.sin(phase),0,-.015+.0075*(1-math.cos(2*phase))))
    rotate('Pelvis',(0,1,0),.7*math.sin(phase))
    rotate('Chest',(0,0,1),.9*math.sin(phase))
    rotate('Head',(0,0,1),-.45*math.sin(phase))
    for side,offset,sign in [('R',0,1),('L',.5,-1)]:
        q=(t+offset)%1
        y=.04-.095*math.cos(math.tau*q)
        lift=0 if q<.5 else math.sin(math.pi*(2*q-1))**2
        locate('CTRL_Foot_IK.'+side,(0,y,.045*lift))
        rotate('CTRL_Foot_IK.'+side,(1,0,0),-5*lift)
        rest=data.bones['UpperArm.'+side].matrix_local.to_quaternion()
        rotation=Quaternion(Vector((1,0,0)),math.radians(7*math.cos(math.tau*q)))@Quaternion(Vector((0,1,0)),math.radians(-3*sign))
        rig.pose.bones['UpperArm.'+side].rotation_quaternion=rest.inverted()@rotation@rest
        rotate('Forearm.'+side,(1,0,0),-1.5*math.cos(math.tau*q))
    for i in range(7):
        rotate(f'Tail.{i+1:02d}',(0,0,1),.65*math.sin(phase-i*.3))

clips=[]
rig.animation_data_create()
for name,duration,pose in [('Idle_Breathe',72,idle_pose),('Wave',96,wave_pose),('Walk_InPlace',36,walk_pose)]:
    action=bpy.data.actions.new(name)
    action.use_fake_user=True
    slot=action.slots.new('OBJECT',rig.name)
    rig.animation_data.action=action; rig.animation_data.action_slot=slot
    for frame in range(1,duration+2):
        neutral(); pose((frame-1)/duration)
        for pb in rig.pose.bones:
            for path in ('location','rotation_quaternion','scale'):
                pb.keyframe_insert(data_path=path,frame=frame,group=pb.name)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points: key.interpolation='LINEAR'
    track=rig.animation_data.nla_tracks.new(); track.name=name
    strip=track.strips.new(name,1,action); strip.action_slot=slot
    track.mute=True
    action['clip_duration_seconds']=duration/FPS
    action['looping']=name!='Wave'
    clips.append({'name':name,'frames':[1,duration+1],'duration_seconds':duration/FPS,'looping':name!='Wave'})

rig.animation_data.action=None
neutral()
data.pose_position='REST'
bpy.context.view_layer.update()
bind_errors=[]
for obj in skins:
    if obj.name.startswith('Arm '): obj['rigging_role']='Bound to UpperArm / Forearm / Hand; shoulder cap blends into Chest'
    # Every vertex must have a normalized nonzero weight and no more than four bones.
    for vertex in obj.data.vertices:
        total=sum(g.weight for g in vertex.groups)
        if abs(total-1)>.0001 or len(vertex.groups)>4: bind_errors.append((obj.name,vertex.index,total))
if bind_errors: raise RuntimeError('Invalid weights '+str(bind_errors[:3]))

report={'revision':'v9','source':'revisions/v7/CatGray_IP.blend',
        'armature':rig.name,'bones':len(data.bones),'deform_bones':sum(b.use_deform for b in data.bones),
        'skinned_objects':len(skins),'weights':weight_report,'ik_calibration':ik_calibration,
        'fps':FPS,'clips':clips,'skin_algorithm':'linear blend; max four influences; subdivision before skinning'}
(OUT/'qa/rig_build.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('RIG_BUILT',json.dumps(report,ensure_ascii=False),flush=True)
if any(item['rest_knee_error']>.003 for item in ik_calibration): raise RuntimeError('IK changes neutral knee position')

# Export actions while only the three reusable clips are present.
data.pose_position='POSE'
rig.animation_data.use_nla=False
rig.animation_data.action=bpy.data.actions['Idle_Breathe']
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT')
for obj in skins+[rig]: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
# Native playback timeline: idle, wave, and two walking cycles. The muted
# single-clip tracks above remain available for selecting/editing each action.
rig.animation_data.action=None
rig.animation_data.use_nla=True
playlist=rig.animation_data.nla_tracks.new()
playlist.name='播放预览 • 待机 / 挥手 / 走路'
for name,start,repeat in [('Idle_Breathe',1,1),('Wave',73,1),('Walk_InPlace',169,2)]:
    action=bpy.data.actions[name]
    strip=playlist.strips.new(name,start,action); strip.action_slot=action.slots[0]
    strip.repeat=repeat; strip.extrapolation='NOTHING'; strip.blend_type='REPLACE'
scene.frame_start=1; scene.frame_end=240
for marker in list(scene.timeline_markers): scene.timeline_markers.remove(marker)
for label,frame in [('待机呼吸 / Idle',1),('挥手 / Wave',73),('原地走路 / Walk',169)]:
    scene.timeline_markers.new(label,frame=frame)
scene.frame_set(1)
notes=bpy.data.texts.new('使用说明 • 骨骼与动画')
notes.write('''CatGray v9 骨骼动画\n\n时间轴 1–240 帧：待机呼吸、挥手、两轮原地走路。空格播放。\n独立动作：Idle_Breathe / Wave / Walk_InPlace，24 FPS。\n编辑单个动作：禁用“播放预览”NLA 轨道，在动作编辑器选择对应动作。\nCTRL_Root：整体移动。CTRL_Foot_IK.L/R：脚底位置和朝向。\nCTRL_Knee_Pole.L/R：膝盖弯曲方向。\nHead / Chest / Pelvis：头身姿态。UpperArm / Forearm / Hand：手臂 FK。\nTail.01–07：尾巴；Ear.L/R：耳朵。左右手臂仍为独立网格。\n骨骼默认不置顶，使用细线显示；物体模式打开即可查看表面。需要透视编辑时，在骨架对象的数据/视图显示设置中开启 In Front（在前面）。\n招手使用连续肘部权重，手掌随前臂摆动。没有眨眼、口型或手指表情绑定。\n''')
root['animation_preview']='Timeline 1–240 at 24 fps: Idle, Wave, Walk twice'
bpy.ops.object.select_all(action='DESELECT')
body_view=next(o for o in skins if o.name.startswith('Body '))
bpy.context.view_layer.objects.active=body_view
scene.camera=bpy.data.objects['Camera • Three quarter']
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
manifest=json.loads((OUT/'revisions/v7/model_info.json').read_text())
manifest['rig_revision']=report
manifest['body_revision']['rigging_status']='Weighted to CATGRAY_RIG; arm FK, leg IK, three animation clips'
(OUT/'model_info.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('CATGRAY_RIG_COMPLETE',flush=True)

if '--no-export' not in sys.argv:
    import runpy
    runpy.run_path(str(OUT/'export_rig.py'),run_name='__main__')
