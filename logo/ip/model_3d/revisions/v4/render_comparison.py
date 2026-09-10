"""Render archived v3 and current v4 at an identical orthographic scale."""
import bpy
import math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CatGray_IP.blend'))
current = bpy.data.collections['CATGRAY • Character']
current_root = next(obj for obj in current.objects if obj.type == 'EMPTY')
with bpy.data.libraries.load(str(OUT/'revisions/v3/CatGray_IP.blend'), link=False) as (src, dst):
    dst.collections = ['CATGRAY • Character']
previous = dst.collections[0]
bpy.context.scene.collection.children.link(previous)
previous_root = next(obj for obj in previous.objects if obj.type == 'EMPTY')
current_root.location.x = 2.17
previous_root.location.x = -2.17

scene = bpy.context.scene
camera = bpy.data.objects['Camera • Front']
camera.location = (0, -18, 2.40)
camera.rotation_euler = (Vector((0, 0, 2.40))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 9.70
scene.camera = camera

label_material = bpy.data.materials.new('Comparison labels')
label_material.diffuse_color = (.055, .065, .075, 1)
label_material.use_nodes = True
label_material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.055, .065, .075, 1)
for x, label in ((-2.17, 'V3'), (2.17, 'V4')):
    data = bpy.data.curves.new('Version label '+label, 'FONT')
    data.body = label
    data.align_x = 'CENTER'
    data.size = .18
    obj = bpy.data.objects.new('Version label '+label, data)
    scene.collection.objects.link(obj)
    data.materials.append(label_material)
    obj.location = (x, -1.7, 4.84)
    obj.rotation_euler = (math.pi/2, 0, 0)

scene.render.resolution_x = 1800
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.cycles.samples = 64
scene.render.filepath = str(OUT/'preview_comparison.png')
bpy.ops.render.render(write_still=True)
print('V3_V4_COMPARISON_COMPLETE', flush=True)
