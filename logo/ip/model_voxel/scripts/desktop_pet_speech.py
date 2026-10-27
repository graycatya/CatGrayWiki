"""Dedicated speech aperture shapes; never sequence emotion/viseme demo states.

A consistent rounded mouth opens downward through three pixel-sized apertures.
New geometry is confined to the separate desktop-pet project.
"""
import json
import math
import bpy
from voxel_model import ROOT, read_vox
from rig_voxel import partition
import facial_voxel as face

STATES=('TalkRest','TalkSmall','TalkMedium','TalkOpen')


def speech_pixel(state,x,z):
    if abs(x)>.49 or not 2.04<z<2.65:
        return None
    if abs(x)<.055 and z>2.54:
        return 5
    if state=='TalkRest':
        return 5 if abs(x)<.24 and abs(z-(2.39-.045*(1-(x/.24)**2)))<.05 else None
    depth={'TalkSmall':.21,'TalkMedium':.31,'TalkOpen':.40}[state]
    # Same mouth corners and upper lip throughout; the lower edge opens down.
    top=2.44
    bottom=top-depth
    if abs(x)<.255 and bottom<z<top:
        if abs(x)>.18 and (z<bottom+.045 or z>top-.045):
            return None
        return 11 if depth>.25 and z<bottom+.09 and abs(x)<.13 else 5
    return None


def install(rig):
    old=bpy.data.objects[face.FACE]
    materials=list(old.data.materials)
    collection=old.users_collection[0]
    bpy.data.objects.remove(old,do_unlink=True)
    info=json.loads((ROOT/'model_info.json').read_text())
    _,grid,_=read_vox(ROOT/'CatGray_Voxel.vox')
    minimum=info['grid_minimum']
    voxels={tuple(p[i]+minimum[i] for i in range(3)):color for p,color in grid.items()}
    head=partition(voxels,info['voxel_size'])['Head']
    original=face.mouth_pixel
    original_states=face.STATES
    def mouth(state,x,z):
        return speech_pixel(state,x,z) if state in STATES else original(state,x,z)
    face.mouth_pixel=mouth
    face.STATES=original_states+tuple('Mouth_'+s for s in STATES)
    try:
        face.build_face(head,info['voxel_size'],materials,rig,collection)
    finally:
        face.mouth_pixel=original
        face.STATES=original_states


def aperture(t):
    # Speech-like bursts with unequal emphasis and rests; not A/E/O rotation.
    seconds=(t%1)*3
    bursts=((.08,.62,.94),(.72,1.11,.62),(1.28,1.80,1.0),(1.92,2.28,.55),(2.38,2.78,.82))
    opening=0
    for start,end,strength in bursts:
        if start<seconds<end:
            opening=strength*math.sin(math.pi*(seconds-start)/(end-start))**1.1
            break
    return 'TalkRest' if opening<.14 else 'TalkSmall' if opening<.42 else 'TalkMedium' if opening<.76 else 'TalkOpen'
