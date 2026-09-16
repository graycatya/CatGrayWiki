"""Check rigid skinning, all action frames, GLB reimport and optional movies."""
from collections import Counter
import hashlib
import json
import math
import struct

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

from voxel_model import ROOT,NAME,generate,settings,read_vox
from rig_voxel import RIG,FPS,CLIPS,PLAYLIST,skins,set_action,rest_pose,partition
from facial_voxel import (FACE,STATES,DEFAULT,EYES,MOUTHS,face_keys,facial_state,
                          front_cells,eye_pixel,mouth_pixel,select_states)
from voxel_model import DIRECTIONS


def positions(objects):
    graph = bpy.context.evaluated_depsgraph_get()
    return {o.name:np.array([o.matrix_world@v.co for v in o.evaluated_get(graph).data.vertices]) for o in objects}


def frame_set(scene,frame):
    integer = int(frame)
    scene.frame_set(integer,subframe=frame-integer)


def linear(value):
    return value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4


def verify_face_surface(rig,objects,config):
    """Probe visible fronts AND stair risers, including cleared expression pixels.

    Rays begin close to the original head, avoiding occlusion by other stairs.
    Several points across each face detect partial-depth coverage. Expected
    colors come from the expression drawings, not the generated tile geometry.
    """
    rest_pose(rig)
    step = config["voxel_size"]
    head_cells = partition(generate(config),step)["Head"]
    front = front_cells(head_cells,step)
    pixels = {(i,k):j for (i,k),j in front.items() if
              any(eye_pixel(s,(i+.5)*step,(k+.5)*step) is not None for s in EYES) or
              any(mouth_pixel(s,(i+.5)*step,(k+.5)*step) is not None for s in MOUTHS)}
    head = next(o for o in objects if o.name == "Voxel_Head")
    face = next(o for o in objects if o.type == "MESH" and o.data.shape_keys)
    palette = [(entry["name"],tuple(linear(int(entry["hex"][i:i+2],16)/255) for i in (0,2,4)))
               for entry in config["palette"]]

    def material_color_name(material):
        # Reimport adds .001 to existing names; compare the rendered color.
        shader = next((n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),None) if material.use_nodes else None
        rgb = shader.inputs["Base Color"].default_value if shader else material.diffuse_color
        return next((name for name,color in palette if all(abs(rgb[i]-color[i])<1e-5 for i in range(3))),material.name)

    def tree_for(mesh_objects):
        graph = bpy.context.evaluated_depsgraph_get()
        points,polygons,materials = [],[],[]
        for obj in mesh_objects:
            evaluated = obj.evaluated_get(graph)
            mesh = evaluated.to_mesh()
            base = len(points)
            color_names = [material_color_name(m) for m in mesh.materials]
            points.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
            polygons.extend(tuple(base+i for i in p.vertices) for p in mesh.polygons)
            materials.extend(color_names[p.material_index] for p in mesh.polygons)
            evaluated.to_mesh_clear()
        return BVHTree.FromPolygons(points,polygons),materials

    head_tree,head_materials = tree_for([head])
    probes = []
    for (i,k),j in pixels.items():
        cell = (i,j,k)
        for direction,corners in DIRECTIONS:
            if tuple(p+d for p,d in zip(cell,direction)) in head_cells:
                continue
            normal = Vector(direction)
            a,b,_,d = (Vector(tuple((p+c)*step for p,c in zip(cell,corner))) for corner in corners)
            for u,v in ((.5,.5),(.12,.12),(.12,.88),(.88,.12),(.88,.88)):
                origin = a+(b-a)*u+(d-a)*v+normal*step*.3
                _,_,index,distance = head_tree.ray_cast(origin,-normal,step*.6)
                assert index is not None, (cell,direction)
                probes.append(((i,k),direction,origin,normal,head_materials[index],distance))
    combinations = [(s,"Neutral") for s in EYES]+[("Open",s) for s in MOUTHS if s != "Neutral"]
    failures = []
    counts = Counter()
    for eyes,mouth in combinations:
        select_states(eyes,mouth)
        bpy.context.view_layer.update()
        tree,materials = tree_for([head,face])
        for (i,k),direction,origin,normal,base_color,base_distance in probes:
            x,z = (i+.5)*step,(k+.5)*step
            color = eye_pixel(eyes,x,z)
            if color is None:
                color = mouth_pixel(mouth,x,z)
            expected_color = config["palette"][color-1]["name"] if color is not None else base_color
            _,_,index,distance = tree.ray_cast(origin,-normal,step*.6)
            actual = materials[index] if index is not None else None
            # Colored surfaces must be in front of gray, never coplanar with it.
            valid = actual == expected_color and (color is None or distance < base_distance-step*.01)
            kind = "front" if direction == (0,-1,0) else "sidewall"
            counts[kind] += 1
            counts["painted" if color is not None else "cleared"] += 1
            if not valid:
                counts["failed"] += 1
                if len(failures)<20:
                    failures.append({"states":[eyes,mouth],"pixel":[i,k],"normal":direction,
                                     "expected":expected_color,"actual":actual,"distance":distance})
    select_states()
    bpy.context.view_layer.update()
    return {"passed":not counts["failed"] and counts["sidewall"]>0,
            "state_combinations":len(combinations),"probes":dict(counts),"failures":failures}


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
    surface_report = verify_face_surface(rig,objects,config)
    checks["face_front_and_sidewall_colors_all_states"] = surface_report["passed"]
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
    imported_surface_report = verify_face_surface(imported_rig,imported,config)
    checks["glb_reimport_face_sidewalls_all_states"] = imported_surface_report["passed"]
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
              "face_surface":surface_report,"glb_face_surface":imported_surface_report,
              "blender_version":bpy.app.version_string,"triangles":triangles,
              "files_sha256":{NAME+ext:hashlib.sha256((ROOT/(NAME+ext)).read_bytes()).hexdigest() for ext in (".blend",".glb",".vox")}}
    (ROOT/"qa/verification.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    if not report["passed"]:
        raise RuntimeError("Animation verification failed: "+", ".join(k for k,v in checks.items() if not v))
    return report
