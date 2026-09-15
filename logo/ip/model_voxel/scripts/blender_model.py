"""Build, export, render and verify the articulated voxel edition inside Blender."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voxel_model import ROOT, NAME, generate, settings, surface_mesh, write_vox
from rig_voxel import RIG, CLIPS, PLAYLIST, create_rig, build_actions, skins, rest_pose, set_action
from facial_voxel import face_keys


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def linear(value):
    return value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4


def material(name, hex_color):
    rgb = tuple(linear(int(hex_color[i:i+2],16)/255) for i in (0,2,4))
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb,1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb,1)
    shader.inputs["Roughness"].default_value = .83
    shader.inputs["Specular IOR Level"].default_value = .12
    return mat


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def studio():
    scene = bpy.context.scene
    collection = bpy.data.collections.new("STUDIO")
    scene.collection.children.link(collection)
    def move(obj):
        for owner in list(obj.users_collection):
            owner.objects.unlink(obj)
        collection.objects.link(obj)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.012))
    floor = bpy.context.object
    floor.name = "Studio floor"
    move(floor)
    floor.data.materials.append(material("Studio warm white","E7E4DE"))
    for name,location,power,size in (
        ("Key",(-3,-5,8),650,4), ("Fill",(5,-1,5),300,5),
        ("Rim",(0,5,7),550,3)):
        data = bpy.data.lights.new(name,"AREA")
        data.energy, data.shape, data.size = power,"DISK",size
        obj = bpy.data.objects.new(name,data)
        collection.objects.link(obj)
        obj.location = location
        aim(obj,(0,0,2.3))
    for name,location,scale in (
        ("front",(0,-14,2.40),5.6), ("side",(14,0,2.40),5.6),
        ("back",(0,14,2.40),5.6), ("hero",(7,-12,6.6),6.0),
        ("rear_quarter",(-7,12,6.6),6.0)):
        data = bpy.data.cameras.new("Camera_"+name)
        data.type, data.ortho_scale = "ORTHO",scale
        obj = bpy.data.objects.new(data.name,data)
        collection.objects.link(obj)
        obj.location = location
        aim(obj,(0,0,2.35))
    scene.camera = bpy.data.objects["Camera_hero"]
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (.70,.76,.85,1)
    background.inputs["Strength"].default_value = .45
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    # Open on an uncluttered material-colored view of the character.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                space = area.spaces.active
                space.overlay.show_extras = False
                space.region_3d.view_distance = 8.0
                space.region_3d.view_location = (0,0,2.35)
                space.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
                space.shading.color_type = "MATERIAL"


def select_character():
    bpy.ops.object.select_all(action="DESELECT")
    rig = bpy.data.objects[RIG]
    for obj in skins()+[rig]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    return rig


def export():
    rig = select_character()
    # Only reusable Actions go into GLB; the native playlist stays in .blend.
    for track in list(rig.animation_data.nla_tracks):
        if track.name == PLAYLIST:
            rig.animation_data.nla_tracks.remove(track)
    for track in list(face_keys().animation_data.nla_tracks):
        if track.name == PLAYLIST:
            face_keys().animation_data.nla_tracks.remove(track)
    # Make the exported time origin explicit. The native Actions remain at
    # frames 1..N+1 in the saved .blend; this in-memory export starts at 0 s.
    for clip in CLIPS:
        action = bpy.data.actions[clip["name"]]
        start = action.frame_range[0]
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:
                            key.co.x -= start
                            key.handle_left.x -= start
                            key.handle_right.x -= start
    set_action(rig,CLIPS[0]["name"])
    bpy.context.scene.frame_set(0)
    bpy.ops.export_scene.gltf(
        filepath=str(ROOT/(NAME+".glb")), export_format="GLB",
        use_selection=True, export_animations=True, export_animation_mode="ACTIONS",
        export_force_sampling=False, export_bake_animation=False, export_frame_range=False,
        export_anim_single_armature=False, export_rest_position_armature=True,
        export_merge_animation="ACTION", export_morph=True, export_morph_normal=False,
        export_morph_animation=True, export_morph_reset_sk_data=True,
        export_anim_slide_to_zero=True, export_reset_pose_bones=True,
        export_influence_nb=4, export_all_influences=False, export_def_bones=False,
        export_leaf_bone=False, export_cameras=False, export_lights=False,
        export_materials="EXPORT", export_yup=True)


def build():
    config = settings()
    voxels = generate(config)
    vertices, faces, _ = surface_mesh(voxels,config["voxel_size"])
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    materials = [material(entry["name"],entry["hex"]) for entry in config["palette"]]
    rig,parts,face_info = create_rig(voxels,config["voxel_size"],materials)
    grid = write_vox(ROOT/(NAME+".vox"),voxels,config["palette"])
    studio()
    rig_info = build_actions(rig)
    select_character()
    notes = bpy.data.texts.new("使用说明 • 体素骨骼与动画")
    notes.write("体素动画 v3：18 根骨骼，17 个身体部件，1 个像素表情网格，16 个形态键。\n"
                "时间轴包含身体、独立头部、眨眼、嘴型与四种情绪；24 FPS，空格播放。\n"
                "选择 CATGRAY_VOXEL_RIG 后进入姿态模式编辑。需要透视骨骼时开启 In Front。\n"
                "编辑单个 Action 前，关闭骨架与 Voxel_Face 形态键的播放预览 NLA 轨道。\n"
                "头部动作只键控 Head/Ear 通道。表情 Action 的 KEY 插槽控制 Voxel_Face 形态键。\n"
                "走动与跑动为原地循环；Jump 在 CTRL_Root 中包含竖直位移。\n"
                "每个部件只绑定一根骨骼；无 IK 约束、驱动器或外部插件。\n")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(NAME+".blend")))
    export()
    info = {
        "version": config["version"], "style": "voxel", "status": "rigged_with_animations",
        "blender_version": bpy.app.version_string, "voxel_size": config["voxel_size"],
        **grid, "occupied_voxels": len(voxels), "mesh_objects": len(parts),
        "vertices": sum(p["vertices"] for p in parts), "surface_quads": sum(p["quads"] for p in parts),
        "triangles": sum(p["quads"] for p in parts)*2,
        "rest_exterior_vertices":len(vertices),"rest_exterior_quads":len(faces),"parts":parts,
        "materials": config["palette"], "palette_usage": dict(Counter(voxels.values())),
        "dimensions_blender_units": [round(v*config["voxel_size"],6) for v in grid["grid_dimensions"]],
        "rig": rig_info, "face":face_info,"animations": rig_info["clips"], "external_textures": [],
        "coordinate_system": "Blender: Z up, front -Y; GLB: standard glTF Y up",
        "vox_coordinates": "Nonnegative grid indices; add grid_minimum then multiply by voxel_size",
        "reference_design": "../references + model_3d v10 bare-body design",
        "build_inputs": ["source/settings.json","scripts/voxel_model.py","scripts/blender_model.py","scripts/rig_voxel.py","scripts/facial_voxel.py"],
    }
    save_json(ROOT/"model_info.json",info)
    print(f"VOXEL_BUILD: {len(voxels)} voxels, {info['triangles']} triangles, {rig_info['bones']} bones",flush=True)


def preview(quick=False):
    rest_pose(bpy.data.objects[RIG])
    scene = bpy.context.scene
    scene.cycles.samples = 16 if quick else 48
    scene.render.resolution_x = scene.render.resolution_y = 640 if quick else 1000
    for view in ("hero","front","side","back","rear_quarter"):
        scene.camera = bpy.data.objects["Camera_"+view]
        bpy.data.objects["Studio floor"].hide_render = view in ("front","side","back")
        scene.render.filepath = str(ROOT/"previews"/("preview_"+view+".png"))
        bpy.ops.render.render(write_still=True)
    scene.camera = bpy.data.objects["Camera_hero"]
    bpy.data.objects["Studio floor"].hide_render = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("rebuild","preview","pose-preview","render","encode","export","verify","verify-rig"))
    parser.add_argument("--quick",action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    for folder in ("previews","qa"):
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    if args.command == "rebuild":
        build()
    else:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/(NAME+".blend")))
        from animation_media import preview_poses,render
        from verify_animation import verify as verify_animated
        {"preview":lambda:preview(args.quick),"pose-preview":preview_poses,"render":render,
         "encode":lambda:render(encode_only=True),"export":export,
         "verify":lambda:verify_animated(include_videos=True),"verify-rig":verify_animated}[args.command]()


if __name__ == "__main__":
    main()
