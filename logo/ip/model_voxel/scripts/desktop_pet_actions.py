"""Author editable 24 FPS desktop pet actions in a separate Blender project.

All poses are baked into real bone/object and discrete facial Action slots.
The original CatGray_Voxel.blend and its 12 source actions remain untouched.
"""
import math
import bpy
from mathutils import Matrix, Vector
from rig_voxel import Motion, RIG, rotation, pivot, neutral, set_action
from facial_voxel import face_keys, key_face, slot_for
import desktop_pet_speech as speech

DURATIONS = {'Thinking':3, 'Working':2, 'Waiting':4, 'Speaking':3}
PROP_COLLECTION = 'DesktopPet • Keyboard'


def keyboard():
    collection = bpy.data.collections.get(PROP_COLLECTION)
    if collection:
        return collection
    collection = bpy.data.collections.new(PROP_COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    def material(name, color):
        m=bpy.data.materials.new(name)
        m.diffuse_color=(*color,1)
        m.use_nodes=True
        m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1)
        m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8
        return m
    dark=material('Pet keyboard • charcoal',(.045,.06,.085))
    light=material('Pet keyboard • keys',(.48,.58,.68))
    amber=material('Pet keyboard • amber key',(.95,.45,.045))
    def block(name,location,size,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=location)
        obj=bpy.context.object
        obj.name=name
        obj.dimensions=size
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for c in list(obj.users_collection):
            c.objects.unlink(obj)
        collection.objects.link(obj)
        obj.data.materials.append(mat)
        return obj
    block('Keyboard base',(0,-.90,.98),(1.70,.58,.10),dark)
    for row in range(3):
        for col in range(10):
            block(f'Key {row}.{col}',(-.72+col*.16,-1.11+row*.17,1.055),(.13,.13,.05),amber if (row,col)==(0,9) else light)
    for x in (-.74,.74):
        block('Keyboard stand',(x,-.85,.47),(.09,.09,.94),dark)
    return collection


def arm(motion, d, side, target):
    """Geometrically solve shoulder/elbow/paw; bake ordinary FK transforms."""
    upper,lower='UpperArm.'+side,'Forearm.'+side
    # Shoulder caps have volume above their bone origin: move them outward
    # and down before solving so raised arms stay below the oversized head.
    sign=-1 if side=='L' else 1
    shoulder=d['Body']@motion.heads[upper]+Vector((sign*.10,-.06,-.20))
    original_elbow=motion.heads[lower]
    original_tip=motion.rig.data.bones[lower].tail_local
    a=(original_elbow-motion.heads[upper]).length
    b=(original_tip-original_elbow).length
    target=Vector(target)
    delta=target-shoulder
    length=delta.length
    if length>=a+b:
        raise RuntimeError(f'Unreachable {side} paw: {length:.3f} > {a+b:.3f}')
    along=delta.normalized()
    sign=-1 if side=='L' else 1
    pole=Vector((sign, -.10, -.15))
    outward=(pole-along*pole.dot(along)).normalized()
    distance=max(abs(a-b)+1e-5,length)
    projection=(a*a-b*b+distance*distance)/(2*distance)
    elbow=shoulder+along*projection+outward*math.sqrt(max(0,a*a-projection*projection))
    for bone,old_start,old_end,start,end in (
        (upper,motion.heads[upper],original_elbow,shoulder,elbow),
        (lower,original_elbow,original_tip,elbow,target)):
        q=(old_end-old_start).normalized().rotation_difference((end-start).normalized())
        d[bone]=Matrix.Translation(start)@q.to_matrix().to_4x4()@Matrix.Translation(-old_start)


def authored_pose(motion,name,t):
    p=math.tau*t
    d={n:Matrix.Identity(4) for n in motion.rest}
    eyes='Closed' if .80<=t<.84 else 'Half' if .78<=t<.80 or .84<=t<.86 else 'Open'
    mouth='Neutral'
    d['Body']=Matrix.Translation((0,0,.012*(1-math.cos(p))))
    d['Head']=d['Body'].copy()
    if name=='Working':
        # IK targets are bone endpoints, not paw undersides. The raised path
        # leaves clearance for the rigid forearm shell above physical keycaps.
        d['Head']=d['Body']@pivot(motion.heads['Head'],rotation(x=5,y=1.5*math.sin(p)))
        for side,sign in [('L',-1),('R',1)]:
            tapping=math.sin(2*p+(0 if side=='L' else math.pi))
            arm(motion,d,side,(sign*.55,-.85+.02*math.cos(p),1.35+.07*(1+tapping)/2))
    elif name=='Thinking':
        d['Head']=d['Body']@pivot(motion.heads['Head'],rotation(x=-4,y=-5+1.5*math.sin(p),z=-4))
        arm(motion,d,'L',(-.66,-.78,1.46+.02*math.sin(p)))
        arm(motion,d,'R',(.70,-.59,1.00))
        eyes='Half' if .3<t<.6 else eyes
    elif name=='Waiting':
        # Planted feet, relaxed arms; deliberate scan rather than a thinking pose.
        d['Body']=Matrix.Translation((.035*math.sin(p),0,0))@pivot(motion.heads['Body'],rotation(y=2*math.sin(p)))
        d['Head']=d['Body']@pivot(motion.heads['Head'],rotation(z=18*math.sin(p),x=1*math.sin(2*p)))
        for side in ['L','R']:
            for part in ['UpperArm.','Forearm.']:
                d[part+side]=d['Body']@Matrix.Translation(((-.04 if side=='L' else .04),0,-.09))
    elif name=='Speaking':
        d['Body']=Matrix.Translation((0,0,.02*(1-math.cos(2*p))))
        d['Head']=d['Body']@pivot(motion.heads['Head'],rotation(x=4*math.sin(2*p),y=3*math.sin(p)))
        arm(motion,d,'L',(-.75,-.48-.12*(1+math.sin(p))/2,1.16+.10*(1+math.sin(p))/2))
        arm(motion,d,'R',(.75,-.48-.12*(1-math.sin(p))/2,1.10+.10*(1-math.sin(p))/2))
        mouth=speech.aperture(t)
    for side,sign in [('L',-1),('R',1)]:
        ear='Ear.'+side
        d[ear]=d['Head']@pivot(motion.heads[ear],rotation(y=sign*(3*math.sin(p)+(5 if name=='Thinking' else 0))))
    for i in range(1,4):
        bone=f'Tail.{i:02d}'
        parent='Body' if i==1 else f'Tail.{i-1:02d}'
        d[bone]=d[parent]@pivot(motion.heads[bone],rotation(z=(5 if name=='Waiting' else 2)*math.sin(p-i*.45)))
    motion.apply(d)
    return eyes,mouth


def build(rig):
    speech.install(rig)
    keyboard()
    motion=Motion(rig)
    rig.animation_data_create()
    rig.animation_data.use_nla=False
    rig.data.pose_position='POSE'
    for name,duration in DURATIONS.items():
        action_name='Pet_'+name
        old=bpy.data.actions.get(action_name)
        if old:
            bpy.data.actions.remove(old)
        action=bpy.data.actions.new(action_name)
        action.use_fake_user=True
        obj_slot=action.slots.new('OBJECT',rig.name)
        morph_slot=action.slots.new('KEY',face_keys().name)
        rig.animation_data.action=action
        rig.animation_data.action_slot=obj_slot
        previous={}
        for i in range(duration*24+1):
            # The end is an exact closed duplicate of frame 1, including blinks.
            t=(i/(duration*24))%1
            neutral(rig)
            eyes,mouth=authored_pose(motion,name,t)
            for pb in rig.pose.bones:
                if pb.name in previous and pb.rotation_quaternion.dot(previous[pb.name])<0:
                    pb.rotation_quaternion.negate()
                previous[pb.name]=pb.rotation_quaternion.copy()
                for path in ('location','rotation_quaternion','scale'):
                    pb.keyframe_insert(path,frame=i+1,group=pb.name)
            key_face(action,morph_slot,i+1,eyes,mouth)
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:
                            k.interpolation='CONSTANT' if fc.data_path.startswith('key_blocks[') else 'LINEAR'
        action['duration_seconds']=duration
        action['looping']=True
        action['prop_collection']=PROP_COLLECTION if name=='Working' else ''
    activate(rig,'Pet_Working')
    bpy.context.scene.frame_start=1
    bpy.context.scene.frame_end=DURATIONS['Working']*24
    bpy.context.scene.frame_set(1)


def activate(rig,name):
    set_action(rig,name)
    collection=bpy.data.collections.get(PROP_COLLECTION)
    if collection:
        for obj in collection.objects:
            if obj.animation_data:
                obj.animation_data.action=None
                obj.animation_data.use_nla=False
            obj.hide_render=name!='Pet_Working'
            obj.hide_viewport=name!='Pet_Working'


def verify(rig):
    """Check baked transforms, endpoint closure, feet and distinct whole-body poses."""
    import numpy as np
    report={}
    for name,duration in DURATIONS.items():
        activate(rig,'Pet_'+name)
        samples=[]
        feet=[]
        for frame in range(1,duration*24+2):
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            samples.append(np.array([list(pb.matrix.flatten()) if hasattr(pb.matrix,'flatten') else [v for row in pb.matrix for v in row] for pb in rig.pose.bones]))
            feet.append([list(rig.pose.bones['Foot.'+s].matrix.translation) for s in ['L','R']])
        samples=np.array(samples)
        assert np.max(np.abs(samples[0]-samples[-1]))<1e-4, name+' loop closure'
        amplitude=float(np.max(np.abs(samples[:-1]-samples[0])))
        assert amplitude>.02,name+' lacks body movement'
        assert np.max(np.abs(np.array(feet)-feet[0]))<1e-4,name+' foot drift'
        report[name]={'loopClosed':True,'feetPlanted':True,'maximumBoneMatrixChange':amplitude,'frames':duration*24}
    return report


def playlist(rig):
    """Save a native four-action NLA reel, playable on opening the blend."""
    keys=face_keys()
    for data in (rig,keys):
        data.animation_data_create()
        data.animation_data.action=None
        data.animation_data.use_nla=True
        for track in data.animation_data.nla_tracks:
            track.mute=True
    body_track=rig.animation_data.nla_tracks.new()
    body_track.name='DesktopPet • Four state review'
    face_track=keys.animation_data.nla_tracks.new()
    face_track.name=body_track.name
    collection=bpy.data.collections[PROP_COLLECTION]
    start=1
    for name,duration in DURATIONS.items():
        action=bpy.data.actions['Pet_'+name]
        count=duration*24
        for track,target in ((body_track,'OBJECT'),(face_track,'KEY')):
            strip=track.strips.new('Pet_'+name,start,action)
            strip.action_slot=slot_for(action,target)
            strip.frame_start=start
            strip.frame_end=start+count
            strip.extrapolation='NOTHING'
        for obj in collection.objects:
            for frame in (start,start+count-1):
                obj.hide_render=obj.hide_viewport=name!='Working'
                obj.keyframe_insert('hide_render',frame=frame)
                obj.keyframe_insert('hide_viewport',frame=frame)
        bpy.context.scene.timeline_markers.new('Pet_'+name,frame=start)
        start+=count
    for obj in collection.objects:
        a=obj.animation_data.action
        a.use_fake_user=True
        for layer in a.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for key in fc.keyframe_points:
                            key.interpolation='CONSTANT'
    scene=bpy.context.scene
    # Only the desktop reel markers are relevant in this review project.
    for marker in list(scene.timeline_markers):
        if not marker.name.startswith('Pet_'):
            scene.timeline_markers.remove(marker)
    scene.frame_start,scene.frame_end=1,start-1
    scene.render.fps=24
    scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.overlay.show_overlays=False
