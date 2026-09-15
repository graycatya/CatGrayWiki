"""Rigid voxel parts, FK skeleton and sampled walk/run/jump actions.

Leg poses use a two-link geometric solve while authoring; delivered actions
contain ordinary bone transforms and need no constraints, drivers or add-ons.
"""
from collections import defaultdict
import math

import bpy
from mathutils import Matrix, Quaternion, Vector

from voxel_model import HEAD, TAIL, in_loft, profile_at, segment_distance, surface_mesh
from facial_voxel import (animated_paint,build_face,face_keys,reset_face,select_states,
                          slot_for,facial_state,key_face)

RIG = "CATGRAY_VOXEL_RIG"
COLLECTION = "CATGRAY • Articulated voxel parts"
FPS = 24
CLIPS = [
    {"name":"Walk_InPlace", "frames":32, "repeat":3, "looping":True, "label":"走动", "group":"body", "poster":13},
    {"name":"Run_InPlace", "frames":16, "repeat":6, "looping":True, "label":"跑动", "group":"body", "poster":8},
    {"name":"Jump", "frames":48, "repeat":2, "looping":False, "label":"跳跃", "group":"body", "poster":23},
    {"name":"Head_Nod", "frames":48, "repeat":1, "looping":False, "label":"点头", "group":"head", "poster":15},
    {"name":"Head_Shake", "frames":48, "repeat":1, "looping":False, "label":"摇头", "group":"head", "poster":19},
    {"name":"Head_Turn", "frames":72, "repeat":1, "looping":False, "label":"转头", "group":"head", "poster":23},
    {"name":"Blink", "frames":36, "repeat":1, "looping":False, "label":"眨眼", "group":"face", "poster":12},
    {"name":"Mouth_Talk", "frames":72, "repeat":1, "looping":False, "label":"嘴型", "group":"face", "poster":19},
    {"name":"Emotion_Joy", "frames":72, "repeat":1, "looping":False, "label":"喜悦", "group":"emotion", "poster":37},
    {"name":"Emotion_Sad", "frames":72, "repeat":1, "looping":False, "label":"悲伤", "group":"emotion", "poster":37},
    {"name":"Emotion_Pain", "frames":72, "repeat":1, "looping":False, "label":"痛苦", "group":"emotion", "poster":37},
    {"name":"Emotion_Angry", "frames":72, "repeat":1, "looping":False, "label":"生气", "group":"emotion", "poster":37},
]
BODY_CLIPS = {"Walk_InPlace","Run_InPlace","Jump"}
PLAYLIST = "播放预览 • 身体 / 头部 / 表情"


def partition(voxels, step):
    parts = defaultdict(dict)
    for key,color in voxels.items():
        x,y,z = ((v+.5)*step for v in key)
        side = "L" if x < 0 else "R"
        if in_loft(x,y,profile_at(HEAD,z)) or (1.60 <= z < 1.85 and abs(x) < .60):
            bone = "Head"
        elif z > 3.65:
            bone = "Ear."+side
        elif y > .40 and x < 0 and z < 1.80:
            nearest = min(range(len(TAIL)-1),key=lambda i:segment_distance((x,y,z),TAIL[i],TAIL[i+1]))
            bone = f"Tail.{min(nearest//2+1,3):02d}"
        elif .50 < z < 1.75 and abs(y) <= .25 and abs(x) >= (.60 if z >= 1.4 else .70):
            bone = ("UpperArm." if z >= 1.1 else "Forearm.")+side
        elif z < .60:
            # The forward toe/instep belongs to the planted paw. A deep shin
            # shell would rotate its front corner through the floor in a crouch.
            bone = ("Foot." if z < .20 or (z < .40 and y < -.10) else
                    "Shin." if z < .40 else "Thigh.")+side
        else:
            bone = "Body"
        parts[bone][key] = color
    return dict(parts)


def bone_definitions():
    result = [
        ("CTRL_Root",(0,0,0),(0,0,.25),None,False),
        ("Body",(0,0,.90),(0,0,1.55),"CTRL_Root",True),
        ("Head",(0,0,1.75),(0,0,3.70),"Body",True),
    ]
    for sign,side in ((-1,"L"),(1,"R")):
        result += [
            ("Ear."+side,(sign*1.55,.10,4.0),(sign*1.60,.10,4.6),"Head",True),
            ("UpperArm."+side,(sign*.68,0,1.50),(sign*.84,0,1.10),"Body",True),
            ("Forearm."+side,(sign*.84,0,1.10),(sign*.84,0,.60),"UpperArm."+side,True),
            ("Thigh."+side,(sign*.30,0,.65),(sign*.30,0,.36),"Body",True),
            ("Shin."+side,(sign*.30,0,.36),(sign*.30,0,.15),"Thigh."+side,True),
            ("Foot."+side,(sign*.30,0,.15),(sign*.30,-.30,.15),"Shin."+side,True),
        ]
    for i,(a,b) in enumerate(((TAIL[0],TAIL[2]),(TAIL[2],TAIL[4]),(TAIL[4],TAIL[6]))):
        result.append((f"Tail.{i+1:02d}",a,b,"Body" if i == 0 else f"Tail.{i:02d}",True))
    return result


def create_rig(voxels, step, materials):
    collection = bpy.data.collections.new(COLLECTION)
    bpy.context.scene.collection.children.link(collection)
    data = bpy.data.armatures.new("CatGray voxel • 18 bones")
    rig = bpy.data.objects.new(RIG,data)
    collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name,head,tail,parent,deform in bone_definitions():
        bone = data.edit_bones.new(name)
        bone.head, bone.tail, bone.use_deform = head,tail,deform
        bone.align_roll(Vector((0,-1,0)))
        if parent:
            bone.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    data.display_type = "STICK"
    rig.show_in_front = False
    controls = data.collections.new("Root / Body / Head")
    limbs = data.collections.new("Arms / Legs / Ears / Tail")
    for bone in data.bones:
        (controls if bone.name in ("CTRL_Root","Body","Head") else limbs).assign(bone)
        bone.color.palette = "THEME04" if bone.name == "CTRL_Root" else "THEME02"
    parts = partition(voxels,step)
    stats = []
    for bone,cells in sorted(parts.items()):
        visible_cells = cells
        if bone == "Head":
            visible_cells = {p:1 if c>=5 and animated_paint((p[0]+.5)*step,(p[2]+.5)*step) else c for p,c in cells.items()}
        verts,faces,colors = surface_mesh(visible_cells,step)
        mesh = bpy.data.meshes.new("Voxels • "+bone)
        mesh.from_pydata(verts,[],faces)
        mesh.update()
        obj = bpy.data.objects.new("Voxel_"+bone,mesh)
        collection.objects.link(obj)
        obj.parent = rig
        for mat in materials:
            mesh.materials.append(mat)
        for polygon,color in zip(mesh.polygons,colors):
            polygon.material_index = color
            polygon.use_smooth = False
        obj.vertex_groups.new(name=bone).add(list(range(len(verts))),1.0,"REPLACE")
        modifier = obj.modifiers.new("Rigid voxel bone","ARMATURE")
        modifier.object = rig
        obj["bone"] = bone
        obj["voxels"] = len(cells)
        obj["binding"] = "One bone per rigid part; closed caps at joint boundaries"
        stats.append({"bone":bone,"voxels":len(cells),"vertices":len(verts),"quads":len(faces)})
    face,face_info = build_face(parts["Head"],step,materials,rig,collection)
    stats.append({"bone":"Head","object":face.name,"voxels":0,"vertices":face_info["vertices"],"quads":face_info["quads"],"is_face":True})
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rig["controls"] = "CTRL_Root; Body; Head; Ear.L/R; UpperArm/Forearm.L/R; Thigh/Shin/Foot.L/R; Tail.01–03"
    rig["style"] = "Rigid segmented voxel animation; one normalized bone influence per vertex"
    rig["forward_axis"] = "-Y, Z up"
    return rig,stats,face_info


def skins():
    return [o for o in bpy.data.collections[COLLECTION].objects if o.type == "MESH"]


def neutral(rig):
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)


def set_action(rig, name):
    rig.data.pose_position = "POSE"
    rig.animation_data_create()
    rig.animation_data.use_nla = False
    action = bpy.data.actions[name]
    neutral(rig)
    object_slot = slot_for(action,"OBJECT")
    rig.animation_data.action = action if object_slot else None
    if object_slot:
        rig.animation_data.action_slot = object_slot
    reset_face()
    keys = face_keys()
    key_slot = slot_for(action,"KEY")
    if key_slot:
        keys.animation_data_create()
        keys.animation_data.action = action
        keys.animation_data.action_slot = key_slot
    return action


def smooth(t):
    t = max(0,min(1,t))
    return t*t*(3-2*t)


def envelope(t, points):
    for (a,x),(b,y) in zip(points,points[1:]):
        if a <= t <= b:
            return x+(y-x)*smooth((t-a)/(b-a))
    return points[-1][1]


def rotation(x=0,y=0,z=0):
    return (Quaternion((0,0,1),math.radians(z)) @ Quaternion((0,1,0),math.radians(y))
            @ Quaternion((1,0,0),math.radians(x))).to_matrix().to_4x4()


def pivot(point, rotate):
    p = Vector(point)
    return Matrix.Translation(p) @ rotate @ Matrix.Translation(-p)


class Motion:
    def __init__(self,rig):
        self.rig = rig
        self.rest = {b.name:b.matrix_local.copy() for b in rig.data.bones}
        self.heads = {b.name:b.head_local.copy() for b in rig.data.bones}
        self.foot_points = {o["bone"]:[v.co-self.heads[o["bone"]] for v in o.data.vertices]
                            for o in skins() if o["bone"].startswith("Foot.")}
        self.reach_errors = []

    def leg(self, deforms, side, y, ground, pitch):
        thigh,shin,foot = (name+"."+side for name in ("Thigh","Shin","Foot"))
        hip = deforms["Body"] @ self.heads[thigh]
        foot_rotation = rotation(x=pitch)
        lowest = min((foot_rotation.to_3x3()@v).z for v in self.foot_points[foot])
        ankle = Vector((self.heads[foot].x,y,ground-lowest))
        a = (self.heads[shin]-self.heads[thigh]).length
        b = (self.heads[foot]-self.heads[shin]).length
        delta = ankle-hip
        distance = delta.length
        self.reach_errors.append(max(0,distance-a-b))
        d = max(abs(a-b)+1e-6,min(a+b-1e-6,distance))
        along = delta.normalized()
        front = along.cross(Vector((1,0,0))).normalized()
        projection = (a*a-b*b+d*d)/(2*d)
        knee = hip+along*projection+front*math.sqrt(max(0,a*a-projection*projection))
        for bone,old_end,new_start,new_end in (
            (thigh,self.heads[shin],hip,knee),(shin,self.heads[foot],knee,ankle)):
            old_start = self.heads[bone]
            q = (old_end-old_start).normalized().rotation_difference((new_end-new_start).normalized())
            deforms[bone] = Matrix.Translation(new_start) @ q.to_matrix().to_4x4() @ Matrix.Translation(-old_start)
        deforms[foot] = Matrix.Translation(ankle) @ foot_rotation @ Matrix.Translation(-self.heads[foot])

    def pose(self,name,t):
        if name not in BODY_CLIPS:
            self.gesture(name,t)
            return
        phase = math.tau*t
        jump = name == "Jump"
        running = name == "Run_InPlace"
        root_z,body_z,body_pitch = 0,0,0
        flight = 0
        if jump:
            if .26 < t < .66:
                flight = (t-.26)/.40
                root_z = .85*4*flight*(1-flight)
            body_z = envelope(t,[(0,0),(.16,-.18),(.26,0),(.46,-.07),(.66,0),(.73,-.16),(.90,0),(1,0)])
            body_pitch = envelope(t,[(0,0),(.16,7),(.26,0),(.46,2),(.66,0),(.73,6),(.90,0),(1,0)])
            body_x = 0
        else:
            body_z = (-.165+.06*(1+math.cos(2*phase-math.tau*.9))/2 if running
                      else -.065+.012*math.cos(2*phase))
            body_pitch = 6 if running else 2
            body_x = (.012 if running else .015)*math.sin(phase)
        deforms = {"CTRL_Root":Matrix.Translation((0,0,root_z))}
        deforms["Body"] = (deforms["CTRL_Root"] @ Matrix.Translation((body_x,0,body_z))
                           @ pivot(self.heads["Body"],rotation(x=body_pitch)))
        deforms["Head"] = deforms["Body"] @ pivot(self.heads["Head"],rotation(x=-body_pitch*.8))
        for side,offset,sign in (("L",0,-1),("R",.5,1)):
            q = (t+offset)%1
            if jump:
                foot_y = .08*math.sin(math.pi*flight) if flight else 0
                lift = root_z+(.10*math.sin(math.pi*flight) if flight else 0)
                foot_pitch = -10*math.sin(math.pi*flight) if flight else 0
                arm = envelope(t,[(0,0),(.16,22),(.29,-32),(.50,-25),(.66,0),(.74,12),(.92,0),(1,0)])
                elbow = envelope(t,[(0,0),(.16,-18),(.32,-35),(.55,-25),(.72,-15),(.92,0),(1,0)])
                outward = 18*math.sin(math.pi*max(0,min(1,(t-.12)/.7))) if .12<t<.82 else 0
            else:
                duty,stride,height = (.40,.55,.17) if running else (.62,.36,.085)
                if q < duty:
                    foot_y = -stride/2+stride*q/duty
                    lift,foot_pitch = 0,0
                else:
                    s = (q-duty)/(1-duty)
                    foot_y = stride/2-stride*smooth(s)
                    lift = height*math.sin(math.pi*s)**1.4
                    foot_pitch = -18*math.sin(math.pi*s) if running else -9*math.sin(math.pi*s)
                arm = (32 if running else 17)*math.cos(math.tau*q)
                elbow = (-45+8*math.sin(math.tau*q)) if running else -8
                outward = 4 if running else 2
            self.leg(deforms,side,foot_y,lift,foot_pitch)
            upper,lower = "UpperArm."+side,"Forearm."+side
            deforms[upper] = deforms["Body"] @ pivot(self.heads[upper],rotation(x=arm,y=-sign*outward))
            deforms[lower] = deforms[upper] @ pivot(self.heads[lower],rotation(x=elbow))
            ear = "Ear."+side
            ear_angle = (2*math.sin(2*phase) if not jump else -body_pitch*.3)
            deforms[ear] = deforms["Head"] @ pivot(self.heads[ear],rotation(y=sign*ear_angle))
        for i in range(3):
            bone = f"Tail.{i+1:02d}"
            parent = "Body" if i == 0 else f"Tail.{i:02d}"
            angle = (3 if running else 1.5)*math.sin(phase-i*.4) if not jump else body_pitch*.25
            deforms[bone] = deforms[parent] @ pivot(self.heads[bone],rotation(z=angle))
        self.apply(deforms)

    def apply(self,deforms):
        desired = {bone:deform@self.rest[bone] for bone,deform in deforms.items()}
        for pb in self.rig.pose.bones:
            basis = self.rest[pb.name].inverted() @ desired[pb.name]
            if pb.parent:
                parent = pb.parent.name
                basis = self.rest[pb.name].inverted() @ self.rest[parent] @ desired[parent].inverted() @ desired[pb.name]
            pb.location,pb.rotation_quaternion,pb.scale = basis.decompose()

    def gesture(self,name,t):
        hold = smooth(t/.20)*(1-smooth((t-.80)/.20))
        pitch,roll,yaw,ears = 0,0,0,0
        if name == "Head_Nod":
            pitch = envelope(t,[(0,0),(.17,-4),(.30,10),(.43,-3),(.59,9),(.76,0),(1,0)])
        elif name == "Head_Shake":
            yaw = 15*math.sin(math.tau*2*t)*math.sin(math.pi*t)**2
        elif name == "Head_Turn":
            yaw = envelope(t,[(0,0),(.25,26),(.38,26),(.54,0),(.72,-26),(.84,-26),(1,0)])
        elif name == "Emotion_Joy":
            pitch,roll,ears = -3*hold,2*hold*math.sin(math.tau*2*t),-5*hold
        elif name == "Emotion_Sad":
            pitch,roll,ears = 7*hold,-3*hold,11*hold
        elif name == "Emotion_Pain":
            pitch,roll,ears = 4*hold,5*hold*math.sin(math.tau*3*t),9*hold
        elif name == "Emotion_Angry":
            pitch,yaw,ears = 5*hold,2*hold*math.sin(math.tau*2*t),6*hold
        deforms = {name:Matrix.Identity(4) for name in self.rest}
        deforms["Head"] = pivot(self.heads["Head"],rotation(x=pitch,y=roll,z=yaw))
        for sign,side in ((-1,"L"),(1,"R")):
            bone = "Ear."+side
            deforms[bone] = deforms["Head"] @ pivot(self.heads[bone],rotation(y=sign*ears))
        self.apply(deforms)


def build_actions(rig):
    rig.animation_data_create()
    rig.animation_data.use_nla = False
    motion = Motion(rig)
    for clip in CLIPS:
        name,count = clip["name"],clip["frames"]
        action = bpy.data.actions.new(name)
        action.use_fake_user = True
        slot = action.slots.new("OBJECT",rig.name)
        rig.animation_data.action = action
        rig.animation_data.action_slot = slot
        morph_slot = None if clip["group"] == "head" else action.slots.new("KEY",face_keys().name)
        previous = {}
        for half_frame in range(count*2+1):
            frame = 1+half_frame/2
            neutral(rig)
            motion.pose(name,(frame-1)/count)
            for pb in rig.pose.bones:
                if clip["group"] == "face":
                    continue
                if clip["group"] != "body" and pb.name not in ("Head","Ear.L","Ear.R"):
                    continue
                if pb.name in previous and pb.rotation_quaternion.dot(previous[pb.name]) < 0:
                    pb.rotation_quaternion.negate()
                previous[pb.name] = pb.rotation_quaternion.copy()
                for path in ("location","rotation_quaternion","scale"):
                    pb.keyframe_insert(path,frame=frame,group=pb.name)
            if morph_slot:
                key_face(action,morph_slot,frame,*facial_state(name,(frame-1)/count))
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for key in fc.keyframe_points:
                            key.interpolation = "CONSTANT" if fc.data_path.startswith('key_blocks[') else "LINEAR"
        action["duration_seconds"] = count/FPS
        action["looping"] = clip["looping"]
        track = rig.animation_data.nla_tracks.new()
        track.name,track.mute = name,True
        strip = track.strips.new(name,1,action)
        strip.action_slot = slot
        if morph_slot:
            track = face_keys().animation_data.nla_tracks.new()
            track.name,track.mute = name,True
            strip = track.strips.new(name,1,action)
            strip.action_slot = morph_slot
    if max(motion.reach_errors) > .002:
        raise RuntimeError(f"Foot trajectory exceeds leg reach: {max(motion.reach_errors):.6f}")
    rig.animation_data.action = None
    rig.animation_data.use_nla = True
    track = rig.animation_data.nla_tracks.new()
    track.name = PLAYLIST
    keys = face_keys()
    keys.animation_data.action = None
    keys.animation_data.use_nla = True
    face_track = keys.animation_data.nla_tracks.new()
    face_track.name = PLAYLIST
    select_states()
    scene = bpy.context.scene
    for marker in list(scene.timeline_markers):
        scene.timeline_markers.remove(marker)
    start = 1
    for clip in CLIPS:
        action = bpy.data.actions[clip["name"]]
        strip = track.strips.new(clip["name"],start,action)
        strip.action_slot = slot_for(action,"OBJECT")
        strip.repeat = clip["repeat"]
        strip.extrapolation = "NOTHING"
        morph_slot = slot_for(action,"KEY")
        if morph_slot:
            strip = face_track.strips.new(clip["name"],start,action)
            strip.action_slot = morph_slot
            # Head-only clips leave gaps on this track. Hold the preceding
            # neutral end state: NLA otherwise resets keyed weights to zero.
            strip.repeat,strip.extrapolation = clip["repeat"],"HOLD_FORWARD"
        scene.timeline_markers.new(clip["label"]+" / "+clip["name"],frame=start)
        start += clip["frames"]*clip["repeat"]
    scene.render.fps,scene.render.fps_base = FPS,1
    scene.frame_start,scene.frame_end = 1,start-1
    scene.frame_set(1)
    return {"armature":rig.name,"bones":len(rig.data.bones),"deform_bones":sum(b.use_deform for b in rig.data.bones),
            "maximum_vertex_influences":1,"constraints":0,"fps":FPS,"preview_frames":[1,start-1],
            "maximum_ik_reach_error":max(motion.reach_errors),
            "clips":[dict(c,duration_seconds=c["frames"]/FPS,keyframes=[1,c["frames"]+1]) for c in CLIPS]}


def rest_pose(rig):
    rig.animation_data.action = None
    rig.animation_data.use_nla = False
    neutral(rig)
    reset_face()
    rig.data.pose_position = "REST"
    bpy.context.view_layer.update()
