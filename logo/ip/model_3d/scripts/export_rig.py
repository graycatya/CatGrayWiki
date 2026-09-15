"""Bake an export-only copy to ordinary bone keys; keep native IK editable."""
import bpy
import json
from pathlib import Path
from mathutils import Matrix

OUT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
scene=bpy.context.scene; rig=bpy.data.objects['CATGRAY_RIG']
manifest=json.loads((OUT/'model_info.json').read_text())
clips=manifest['rig_revision']['clips']
rig.animation_data.use_nla=False
skins=[o for o in bpy.data.collections['CATGRAY • Character'].objects if o.type=='MESH']
visibility={o.name:o.hide_viewport for o in skins}
# Bone evaluation has no dependency on the dense display meshes. Excluding
# their viewport evaluation avoids re-skinning 700k triangles per sample.
for obj in skins: obj.hide_viewport=True
poses={}
for clip in clips:
    action=bpy.data.actions[clip['name']]
    rig.animation_data.action=action; rig.animation_data.action_slot=action.slots[0]
    frames={}
    for frame in range(clip['frames'][0],clip['frames'][1]+1):
        scene.frame_set(frame)
        frames[frame]={p.name:p.matrix.copy() for p in rig.pose.bones}
    poses[clip['name']]=frames
    print('SAMPLED_CLIP',clip['name'],len(frames),flush=True)

rig.animation_data_clear()
for pb in rig.pose.bones:
    for constraint in list(pb.constraints): pb.constraints.remove(constraint)
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for bone in list(rig.data.edit_bones):
    if bone.name.startswith(('CTRL_Foot_IK.','CTRL_Knee_Pole.')): rig.data.edit_bones.remove(bone)
bpy.ops.object.mode_set(mode='OBJECT')
for action in list(bpy.data.actions): bpy.data.actions.remove(action)
rig.animation_data_create()
rig.animation_data.use_nla=False
rest={b.name:b.matrix_local.copy() for b in rig.data.bones}
parents={b.name:b.parent.name if b.parent else None for b in rig.data.bones}
errors=[]
for clip in clips:
    name=clip['name']; action=bpy.data.actions.new(name); action.use_fake_user=True
    slot=action.slots.new('OBJECT',rig.name)
    rig.animation_data.action=action; rig.animation_data.action_slot=slot
    previous_rotations={}
    for frame,state in poses[name].items():
        for pb in rig.pose.bones:
            parent=parents[pb.name]
            basis=rest[pb.name].inverted()@state[pb.name]
            if parent:
                basis=rest[pb.name].inverted()@rest[parent]@state[parent].inverted()@state[pb.name]
            location,rotation,scale=basis.decompose()
            if pb.name in previous_rotations and rotation.dot(previous_rotations[pb.name])<0: rotation.negate()
            previous_rotations[pb.name]=rotation.copy()
            pb.location=location; pb.rotation_quaternion=rotation; pb.scale=scale
            for path in ('location','rotation_quaternion','scale'):
                pb.keyframe_insert(data_path=path,frame=frame,group=pb.name)
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points: key.interpolation='LINEAR'
    track=rig.animation_data.nla_tracks.new(); track.name=name; track.mute=True
    strip=track.strips.new(name,1,action); strip.action_slot=slot
    maximum=0.
    for frame in list(range(1,clip['frames'][1]+1,6))+[clip['frames'][1]]:
        scene.frame_set(frame)
        maximum=max(maximum,max(abs(pb.matrix[i][j]-poses[name][frame][pb.name][i][j])
                    for pb in rig.pose.bones for i in range(4) for j in range(4)))
    errors.append({'clip':name,'maximum_baked_pose_matrix_error':maximum})
    # TRS-only formats approximate the tiny shear from breathing scale and
    # half-angle constraints. Deformed mesh bounds are checked after import.
    if maximum>.002: raise RuntimeError('Export baking changes pose: '+str(errors[-1]))

rig.animation_data.action=bpy.data.actions['Idle_Breathe']
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
scene.frame_set(1)
for obj in skins: obj.hide_viewport=visibility[obj.name]
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for obj in skins+[rig]: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(OUT/'CatGray_IP.glb'),export_format='GLB',use_selection=True,
    export_yup=True,export_apply=True,export_animations=True,export_animation_mode='ACTIONS',
    export_force_sampling=False,export_bake_animation=False,export_anim_single_armature=True,
    export_def_bones=False,export_frame_range=False,export_frame_step=1,
    export_rest_position_armature=True,export_anim_slide_to_zero=True,
    export_reset_pose_bones=True,export_influence_nb=4,export_all_influences=False,
    export_cameras=False,export_lights=False,export_leaf_bone=False)
(OUT/'qa/export_bake_verification.json').write_text(json.dumps({'passed':True,'clips':errors,
    'export_bones':len(rig.data.bones),'native_constraints_preserved':True},indent=2))
print('ANIMATED_GLB_EXPORTED',json.dumps(errors),flush=True)
