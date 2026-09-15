"""Check rigid skinning, all action frames, GLB reimport and optional movies."""
from collections import Counter
import hashlib
import json
import math
import struct

import bpy
import numpy as np
from mathutils.kdtree import KDTree

from voxel_model import ROOT,NAME,generate,settings,read_vox
from rig_voxel import RIG,FPS,CLIPS,PLAYLIST,skins,set_action,rest_pose
from facial_voxel import FACE,STATES,DEFAULT,face_keys,facial_state


def positions(objects):
    graph = bpy.context.evaluated_depsgraph_get()
    return {o.name:np.array([o.matrix_world@v.co for v in o.evaluated_get(graph).data.vertices]) for o in objects}


def frame_set(scene,frame):
    integer = int(frame)
    scene.frame_set(integer,subframe=frame-integer)


def linear(value):
    return value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4


def verify(include_videos=False):
    scene = bpy.context.scene
    rig = bpy.data.objects[RIG]
    objects = skins()
    rigid_objects = [o for o in objects if not o.get("is_face")]
    keys = face_keys()
    info = json.loads((ROOT/"model_info.json").read_text())
    config = settings()
    expected = generate(config)
    size,voxels,palette = read_vox(ROOT/(NAME+".vox"))
    restored = {tuple(p[i]+info["grid_minimum"][i] for i in range(3)):c for p,c in voxels.items()}
    checks = {"vox_rest_roundtrip":restored == expected,
              "vox_dimensions":list(size) == info["grid_dimensions"],
              "vox_palette":all(tuple(bytes.fromhex(c["hex"]))+(255,) == palette[i] for i,c in enumerate(config["palette"])),
              "bone_count":len(rig.data.bones) == 18,
              "deform_bones":sum(b.use_deform for b in rig.data.bones) == 17,
              "part_count":len(rigid_objects) == 17 and len(objects) == 18,
              "face_morph_targets":tuple(k.name for k in keys.key_blocks)[1:] == STATES,
              "no_constraints":not any(p.constraints for p in rig.pose.bones),
              "fps":scene.render.fps == FPS and scene.render.fps_base == 1,
              "native_playlist":scene.frame_start == 1 and scene.frame_end == sum(c["frames"]*c["repeat"] for c in CLIPS) and
                                len(rig.animation_data.nla_tracks[PLAYLIST].strips) == len(CLIPS),
              "native_face_playlist":len(keys.animation_data.nla_tracks[PLAYLIST].strips) == sum(c["group"] != "head" for c in CLIPS),
              "no_external_textures":not any(i.source == "FILE" for i in bpy.data.images)}
    playlist_samples,start = {},1
    for clip in CLIPS:
        scene.frame_set(start+clip["poster"]-1)
        playlist_samples[clip["name"]] = positions(objects)
        start += clip["frames"]*clip["repeat"]
    rest_pose(rig)
    rest_cloud = positions(objects)
    checks["flat_voxel_faces"] = all(not p.use_smooth for o in objects for p in o.data.polygons)
    checks["grid_aligned_rest_vertices"] = all(np.max(np.abs(points/config["voxel_size"]-np.round(points/config["voxel_size"])))<1e-4
                                              for name,points in rest_cloud.items() if name != FACE)
    # Each morph owns a distinct tile set. Creating a key from an active mix
    # would accidentally copy other expressions into it and double their offsets.
    basis = np.array([v.co for v in keys.key_blocks[0].data])
    used = set()
    morphs_independent = True
    for key in list(keys.key_blocks)[1:]:
        delta = np.array([v.co for v in key.data])-basis
        indices = set(np.flatnonzero(np.linalg.norm(delta,axis=1)>.0001))
        morphs_independent &= bool(indices) and not bool(indices & used)
        used.update(indices)
    checks["face_morphs_independent"] = morphs_independent and len(used) == len(basis)
    checks["inactive_face_tiles_inside_head"] = all(
        tuple(math.floor(float(v[i])/config["voxel_size"]) for i in range(3)) in expected
        for v in basis+np.array([1e-6,0,1e-6]))
    checks["one_normalized_bone_influence"] = all(
        len(v.groups) == 1 and abs(v.groups[0].weight-1)<1e-7 and
        o.vertex_groups[v.groups[0].group].name == o["bone"] for o in objects for v in o.data.vertices)
    checks["part_voxel_counts"] = sum(o["voxels"] for o in objects) == len(expected)
    checks["closed_part_edges"] = all(all(count == 2 for count in Counter(
        tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)])))
        for p in o.data.polygons for i in range(len(p.vertices))).values()) for o in objects)
    volume = sum(p.center.dot(p.normal)*p.area/3 for o in rigid_objects for p in o.data.polygons)
    checks["rest_volume_preserved"] = math.isclose(volume,len(expected)*config["voxel_size"]**3,rel_tol=1e-5)
    checks["mesh_counts"] = sum(len(o.data.vertices) for o in objects) == info["vertices"] and sum(len(o.data.polygons)*2 for o in objects) == info["triangles"]
    native_samples,actions = {},[]
    min_floor = 1e9
    max_rigid_error = 0
    rest_bones = {b.name:b.matrix_local.copy() for b in rig.data.bones}
    for clip in CLIPS:
        name,count = clip["name"],clip["frames"]
        action = set_action(rig,name)
        checks[name+"_key_range"] = tuple(round(v) for v in action.frame_range) == (1,count+1)
        scene.frame_set(1)
        first = {p.name:p.matrix.copy() for p in rig.pose.bones}
        scene.frame_set(count+1)
        closure = max(abs(p.matrix[i][j]-first[p.name][i][j]) for p in rig.pose.bones for i in range(4) for j in range(4))
        checks[name+"_closed_end_pose"] = closure < 1e-5
        feet,roots,contact_errors,seen_states = [],[],[],set()
        max_body_error,max_head_angle = 0,0
        face_valid = True
        native_samples[name] = {}
        sample_frames = {1,1+count//4,1+count//2,1+3*count//4,count+1,clip["poster"]}
        # Quarter-frame samples also exercise interpolation between authored keys.
        for frame in np.arange(1,count+1.001,.25):
            frame_set(scene,float(frame))
            cloud = positions(rigid_objects)
            floor = min(points[:,2].min() for points in cloud.values())
            min_floor = min(min_floor,float(floor))
            foot_z = [float(cloud["Voxel_Foot."+side][:,2].min()) for side in ("L","R")]
            feet.append(foot_z)
            roots.append(rig.pose.bones["CTRL_Root"].head.z)
            for obj in rigid_objects:
                # A rigidly bound part must preserve every edge length throughout motion.
                points,rest = cloud[obj.name],rest_cloud[obj.name]
                edge_ids = [(e.vertices[0],e.vertices[1]) for e in list(obj.data.edges)[::max(1,len(obj.data.edges)//20)]]
                for a,b in edge_ids:
                    max_rigid_error = max(max_rigid_error,abs(float(np.linalg.norm(points[a]-points[b])-np.linalg.norm(rest[a]-rest[b]))))
            weights = {key.name:key.value for key in list(keys.key_blocks)[1:]}
            active = tuple(name for name,value in weights.items() if value>.5)
            seen_states.update(active)
            face_valid &= (all(min(abs(v),abs(v-1))<1e-6 for v in weights.values()) and
                           sum(n.startswith("Eyes_") for n in active) == 1 and
                           sum(n.startswith("Mouth_") for n in active) == 1)
            if clip["group"] != "body":
                allowed = ("Head","Ear.L","Ear.R") if clip["group"] != "face" else ()
                max_body_error = max(max_body_error,max(abs(p.matrix[i][j]-rest_bones[p.name][i][j])
                    for p in rig.pose.bones if p.name not in allowed for i in range(4) for j in range(4)))
                max_head_angle = max(max_head_angle,math.degrees(rig.pose.bones["Head"].rotation_quaternion.angle))
            if float(frame).is_integer():
                t = (frame-1)/count
                if name in ("Walk_InPlace","Run_InPlace"):
                    duty,stride = (.40,.55) if name == "Run_InPlace" else (.62,.36)
                    for index,side in enumerate(("L","R")):
                        q = (t+index*.5)%1
                        if q < duty:
                            target = -stride/2+stride*q/duty
                            contact_errors.append(max(abs(foot_z[index]),abs(rig.pose.bones["Foot."+side].head.y-target)))
                if int(frame) in sample_frames:
                    native_samples[name][int(frame)] = positions(objects)
                eyes,mouth = facial_state(name,t)
                face_valid &= set(active) == {"Eyes_"+eyes,"Mouth_"+mouth}
        checks[name+"_face_states"] = face_valid
        checks[name+"_native_playlist_playback"] = all(
            np.max(np.abs(points-native_samples[name][clip["poster"]][obj_name]))<1e-5
            for obj_name,points in playlist_samples[name].items())
        airborne = sum(min(z)>.01 for z in feet)
        checks[name+"_ground_clearance"] = min(min(z) for z in feet) >= -.01
        if name == "Jump":
            checks["jump_has_flight"] = max(min(z) for z in feet) > .75
            checks["jump_root_returns"] = abs(roots[0])+abs(roots[-1])<1e-6
        elif clip["group"] == "body":
            checks[name+"_planted_stance"] = max(contact_errors)<1e-4
            checks[name+"_support_pattern"] = airborne>0 if name == "Run_InPlace" else airborne == 0
        else:
            checks[name+"_independent_body"] = max_body_error < 1e-5
        if clip["group"] == "head":
            checks[name+"_visible_rotation"] = max_head_angle > (24 if name == "Head_Turn" else 8)
        if name == "Blink":
            checks["blink_open_half_closed"] = {"Eyes_Open","Eyes_Half","Eyes_Closed"} <= seen_states
        if name == "Mouth_Talk":
            checks["mouth_open_closed_a_e_o"] = {"Mouth_Closed","Mouth_A","Mouth_E","Mouth_O"} <= seen_states
        if clip["group"] == "emotion":
            emotion = name.split("_",1)[1]
            checks[name+"_distinct_eyes_and_mouth"] = {"Eyes_"+emotion,"Mouth_"+emotion} <= seen_states
        actions.append({"name":name,"closure_matrix_error":closure,"minimum_foot_z":min(min(z) for z in feet),
                        "maximum_foot_clearance":max(min(z) for z in feet),"airborne_samples":airborne,
                        "stance_target_error":max(contact_errors,default=0),"facial_states":sorted(seen_states),
                        "unrelated_bone_error":max_body_error,"maximum_head_angle_degrees":max_head_angle})
    checks["no_floor_penetration"] = min_floor >= -.01
    checks["voxel_parts_remain_rigid"] = max_rigid_error < 1e-5
    glb = (ROOT/(NAME+".glb")).read_bytes()
    magic,version,total = struct.unpack_from("<4sII",glb)
    n,kind = struct.unpack_from("<II",glb,12)
    document = json.loads(glb[20:20+n])
    checks["glb_header"] = magic == b"glTF" and version == 2 and total == len(glb) and kind == 0x4E4F534A
    checks["glb_clips"] = {a["name"] for a in document.get("animations",[])} == {c["name"] for c in CLIPS}
    checks["glb_no_studio"] = len(document.get("meshes",[])) == 18 and not document.get("cameras")
    checks["glb_skin"] = len(document.get("skins",[])) == 1 and len(document["skins"][0]["joints"]) == 18
    checks["glb_self_contained"] = not document.get("images") and not any("uri" in b for b in document.get("buffers",[]))
    triangles = sum(document["accessors"][p["indices"]]["count"]//3 for m in document["meshes"] for p in m["primitives"])
    checks["glb_triangles"] = triangles == info["triangles"]
    colors = {m["name"]:m.get("pbrMetallicRoughness",{}).get("baseColorFactor",[1,1,1,1]) for m in document["materials"]}
    checks["glb_palette"] = len(colors) == 11 and all(entry["name"] in colors and all(
        abs(colors[entry["name"]][i]-linear(int(entry["hex"][i*2:i*2+2],16)/255)) < 1e-6 for i in range(3)) for entry in config["palette"])
    face_node = next(n for n in document["nodes"] if n["name"] == FACE)
    face_mesh = document["meshes"][face_node["mesh"]]
    checks["glb_morph_names"] = face_mesh.get("extras",{}).get("targetNames") == list(STATES)
    checks["glb_default_face"] = face_mesh.get("weights") == [int(n in DEFAULT) for n in STATES]
    durations = {}
    for animation in document.get("animations",[]):
        name = animation["name"]
        durations[name] = max(document["accessors"][s["input"]]["max"][0] for s in animation["samplers"])
        clip = next(c for c in CLIPS if c["name"] == name)
        morphs = [c for c in animation["channels"] if c["target"]["path"] == "weights"]
        checks[name+"_glb_morph_channel"] = len(morphs) == int(clip["group"] != "head") and all(
            animation["samplers"][c["sampler"]]["interpolation"] == "STEP" and
            document["nodes"][c["target"]["node"]]["name"] == FACE for c in morphs)
        if clip["group"] != "body":
            allowed = {"Head","Ear.L","Ear.R"} if clip["group"] != "face" else set()
            checks[name+"_glb_independent_channels"] = all(
                document["nodes"][c["target"]["node"]]["name"] in allowed
                for c in animation["channels"] if c["target"]["path"] != "weights")
    checks["glb_clip_durations"] = all(abs(durations.get(c["name"],-1)-c["frames"]/FPS)<1e-5 for c in CLIPS)
    for obj in objects+[rig]:
        bpy.data.objects.remove(obj,do_unlink=True)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/(NAME+".glb")))
    imported = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    imported_face = next(o for o in imported if o.data.shape_keys)
    imported_rig = next(o for o in bpy.context.selected_objects if o.type == "ARMATURE")
    max_import_error = 0
    for name,samples in native_samples.items():
        set_action(imported_rig,name)
        for frame,expected_clouds in samples.items():
            scene.frame_set(frame-1)
            actual = positions(imported)
            if imported_face.name != FACE:
                actual[FACE] = actual.pop(imported_face.name)
            for object_name,reference in expected_clouds.items():
                points = actual[object_name]
                tree = KDTree(len(points))
                for i,point in enumerate(points):
                    tree.insert(point,i)
                tree.balance()
                max_import_error = max(max_import_error,max(tree.find(point)[2] for point in reference))
    checks["glb_reimport_all_clips"] = max_import_error < 1e-4
    # Reimported action screenshot checks actual animated playback, not only rest bounds.
    from animation_media import setup,verify_videos
    setup(640)
    set_action(imported_rig,"Jump")
    scene.frame_set(22)
    scene.render.filepath = str(ROOT/"qa/glb_reimport_jump.png")
    bpy.ops.render.render(write_still=True)
    setup(640,closeup=True)
    for name in ("Blink","Emotion_Joy","Emotion_Sad","Emotion_Pain","Emotion_Angry"):
        clip = next(c for c in CLIPS if c["name"] == name)
        set_action(imported_rig,name)
        scene.frame_set(clip["poster"]-1)
        scene.render.filepath = str(ROOT/"qa"/("glb_reimport_"+name+".png"))
        bpy.ops.render.render(write_still=True)
    if include_videos:
        checks["video_decode_and_source_match"] = verify_videos()["passed"]
    report = {"passed":all(checks.values()),"checks":checks,"clips":actions,"sample_step_frames":.25,
              "minimum_character_z":min_floor,"maximum_rigid_edge_error":max_rigid_error,
              "maximum_glb_reimport_vertex_error":max_import_error,"glb_durations_seconds":durations,
              "blender_version":bpy.app.version_string,"triangles":triangles,
              "files_sha256":{NAME+ext:hashlib.sha256((ROOT/(NAME+ext)).read_bytes()).hexdigest() for ext in (".blend",".glb",".vox")}}
    (ROOT/"qa/verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if not report["passed"]:
        raise RuntimeError("Animation verification failed: "+", ".join(k for k,v in checks.items() if not v))
    return report
