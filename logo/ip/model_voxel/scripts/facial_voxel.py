"""Pixel face states carried by glTF morph targets, with STEP animation.

Unused colored tiles are stored inside the opaque head. Each morph translates
one state to the front surface; there are no zero-area faces, textures,
visibility drivers, or animated materials. Eyes and mouths switch independently.
"""
import math

import bpy

from voxel_model import DIRECTIONS, HEAD, face_color, in_loft, profile_at

FACE = "Voxel_Face"
EYES = ("Open","Half","Closed","Joy","Sad","Pain","Angry")
MOUTHS = ("Neutral","Closed","A","E","O","Joy","Sad","Pain","Angry")
STATES = tuple("Eyes_"+s for s in EYES)+tuple("Mouth_"+s for s in MOUTHS)
DEFAULT = ("Eyes_Open","Mouth_Neutral")
DEPTH = 1.3


def animated_paint(x,z):
    return (any(math.hypot(x-cx,z-3.0)<=.455 for cx in (-.8,.8))
            or (abs(x)<=.27 and 2.15<=z<2.65))


def eye_pixel(state,x,z):
    for cx in (-.8,.8):
        sign = -1 if cx < 0 else 1
        dx,dz = x-cx,z-3.0
        inner = -sign*dx
        radius = math.hypot(dx,dz)
        if abs(dx)>.55:
            continue
        if state in ("Sad","Angry"):
            brow = .52+(.40 if state == "Sad" else -.50)*inner
            if abs(dx)<.38 and abs(dz-brow)<.058:
                return 5
        if state == "Pain" and abs(dx)<.35 and abs(dz-(.50+.06*math.cos(dx*9)))<.055:
            return 5
        if state == "Joy":
            if abs(dx)<.42 and abs(dz-(.13-.28*(dx/.42)**2))<.065:
                return 5
            if .23<sign*dx<.48 and -.54<dz<-.40:
                return 3
        elif state == "Closed":
            if abs(dx)<.42 and abs(dz-(-.04-.055*(1-(dx/.42)**2)))<.055:
                return 5
        elif state == "Pain":
            if -.31<inner<.31 and abs(abs(dz)-(.30-inner)*.48)<.065:
                return 5
        elif radius <= .455:
            if state == "Open":
                return face_color(x,z)
            lid = .02 if state == "Half" else .03+(.35 if state == "Sad" else -.45)*inner
            if abs(dz-lid)<.062:
                return 5
            if dz < lid:
                return face_color(x,z)
    return None


def mouth_pixel(state,x,z):
    ax = abs(x)
    if ax>.49 or not 2.04<z<2.65:
        return None
    if state == "Neutral":
        return face_color(x,z)
    if ax<.055 and z>2.54:
        return 5
    if state == "Closed":
        return 5 if ax<.29 and abs(z-(2.39-.08*(1-(x/.29)**2)))<.056 else None
    if state in ("Sad","Angry"):
        width = .34 if state == "Sad" else .38
        line = 2.22+.18*(1-(x/width)**2)
        return 5 if ax<width and abs(z-line)<(.06 if state == "Sad" else .075) else None
    if state == "Joy":
        if 2.08<z<2.53 and ax<.42*math.sqrt(max(0,(z-2.08)/.45)):
            if z>2.40 and ax<.32:
                return 10
            if z<2.27 and ax<.20:
                return 11
            return 5
    if state == "A":
        if (x/.24)**2+((z-2.29)/.25)**2<1:
            return 11 if z<2.18 else 5
    if state == "E":
        if ax<.35 and 2.18<z<2.45:
            return 10 if 2.31<z<2.40 and ax<.26 else 5
    if state == "O":
        if (x/.21)**2+((z-2.31)/.22)**2<1:
            return 9 if ax<.11 and abs(z-2.31)<.12 else 5
    if state == "Pain":
        if ax<.36 and 2.16<z<2.43:
            return 10 if 2.22<z<2.37 and ax<.27 else 5
    return None


def build_face(head_cells,step,materials,rig,collection):
    front = {}
    for (i,j,k),color in head_cells.items():
        x,y,z = ((v+.5)*step for v in (i,j,k))
        if in_loft(x,y,profile_at(HEAD,z)):
            front[i,k] = min(j,front.get((i,k),j))
    vertices,faces,colors,ranges = [],[],[],{}
    for state in STATES:
        start = len(vertices)
        region,expression = state.split("_",1)
        for (i,k),j in sorted(front.items()):
            x,z = (i+.5)*step,(k+.5)*step
            color = eye_pixel(expression,x,z) if region == "Eyes" else mouth_pixel(expression,x,z)
            if color is None:
                continue
            base = len(vertices)
            # Full colored voxel tiles seated just in front of the head surface.
            for a,b,c in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1)):
                vertices.append(((i+a)*step,j*step-.006+b*.045+DEPTH,(k+c)*step))
            for _,corners in DIRECTIONS:
                faces.append(tuple(base+a+2*b+4*c for a,b,c in corners))
                colors.append(color-1)
        ranges[state] = (start,len(vertices))
    mesh = bpy.data.meshes.new("Pixel face • eye and mouth states")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj = bpy.data.objects.new(FACE,mesh)
    collection.objects.link(obj)
    obj.parent = rig
    for mat in materials:
        mesh.materials.append(mat)
    for polygon,color in zip(mesh.polygons,colors):
        polygon.material_index = color
        polygon.use_smooth = False
    obj.vertex_groups.new(name="Head").add(list(range(len(vertices))),1,"REPLACE")
    obj.modifiers.new("Follow Head","ARMATURE").object = rig
    obj["bone"],obj["voxels"],obj["is_face"] = "Head",0,True
    obj["hiding_strategy"] = "Unused pixel states embedded inside opaque head; STEP morph weights"
    obj.shape_key_add(name="Basis")
    for state,(a,b) in ranges.items():
        key = obj.shape_key_add(name=state,from_mix=False)
        for index in range(a,b):
            key.data[index].co.y -= DEPTH
        key.value = float(state in DEFAULT)
    obj.data.shape_keys.name = "CatGray • Facial states"
    return obj,{"object":FACE,"morph_targets":list(STATES),"vertices":len(vertices),"quads":len(faces),
                "tiles_per_state":{n:(b-a)//8 for n,(a,b) in ranges.items()},"interpolation":"STEP",
                "default_states":list(DEFAULT),"external_textures":False}


def face_keys():
    obj = bpy.data.objects.get(FACE)
    if obj is None or obj.type != "MESH":
        # Blender's glTF importer may retain the original morph node as an
        # Empty and create its skinned mesh as a sibling with the mesh name.
        obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.data.shape_keys
                    and "Eyes_Open" in o.data.shape_keys.key_blocks),None)
    return obj.data.shape_keys if obj and obj.data.shape_keys else None


def select_states(eyes="Open",mouth="Neutral"):
    keys = face_keys()
    if keys:
        active = ("Eyes_"+eyes,"Mouth_"+mouth)
        for key in keys.key_blocks:
            if key.name != "Basis":
                key.value = float(key.name in active)


def slot_for(action,target_type):
    return next((s for s in action.slots if s.target_id_type == target_type),None)


def reset_face():
    keys = face_keys()
    if keys:
        if keys.animation_data:
            keys.animation_data.action = None
            keys.animation_data.use_nla = False
        select_states()


def facial_state(name,t):
    if t<.001 or t>.999:
        return "Open","Neutral"
    if name == "Blink":
        # Two clear blink closures, with half-lid in/out frames.
        for center in (.30,.70):
            distance = abs(t-center)
            if distance<.038:
                return "Closed","Neutral"
            if distance<.080:
                return "Half","Neutral"
    if name == "Mouth_Talk" and .10<t<.90:
        sequence = ("Closed","A","E","O","Closed","E","A","O","Closed","A","E","Closed")
        state = sequence[min(len(sequence)-1,int((t-.10)/.80*len(sequence)))]
        return ("Closed" if .47<t<.51 else "Open"),state
    if name.startswith("Emotion_"):
        state = name.split("_",1)[1]
        if .12<=t<.22 or .82<t<=.91:
            return "Half","Closed"
        if .22<=t<=.82:
            return state,state
    return "Open","Neutral"


def key_face(action,slot,frame,eyes,mouth):
    keys = face_keys()
    keys.animation_data_create()
    keys.animation_data.action = action
    keys.animation_data.action_slot = slot
    keys.animation_data.use_nla = False
    select_states(eyes,mouth)
    for key in keys.key_blocks:
        if key.name != "Basis":
            key.keyframe_insert("value",frame=frame,group=key.name.split("_")[0])
