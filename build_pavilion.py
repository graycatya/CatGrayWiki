import bpy, math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.5, metallic=0.0, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = 4.0
    return mat

red = material('朱红木柱', (0.42, 0.025, 0.018), 0.32)
dark = material('深色瓦片', (0.035, 0.045, 0.055), 0.28)
gold = material('鎏金装饰', (0.65, 0.28, 0.045), 0.26, 0.65)
stone = material('青石台基', (0.18, 0.22, 0.22), 0.82)
wood = material('深木栏杆', (0.16, 0.045, 0.025), 0.38)
water = material('池水', (0.015, 0.12, 0.16), 0.12, 0.15)
green = material('竹叶', (0.025, 0.22, 0.07), 0.7)
lantern = material('灯笼发光', (0.7, 0.12, 0.025), 0.38, emission=(1.0, 0.12, 0.025))
ground = material('地面', (0.07, 0.11, 0.09), 0.95)

def cube(name, location, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object; obj.name = name; obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new('柔和倒角', 'BEVEL'); modifier.width = bevel; modifier.segments = 2
    return obj

def cylinder(name, location, radius, depth, mat, vertices=24, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation or (0, 0, 0))
    obj = bpy.context.object; obj.name = name; obj.data.materials.append(mat); return obj

def torus(name, location, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=32, minor_segments=10, location=location)
    obj = bpy.context.object; obj.name = name; obj.data.materials.append(mat); return obj

# Courtyard, pond, platform and steps
cube('庭院地面', (0, 0, -0.35), (8, 8, 0.35), ground)
cube('水池', (0, -4.2, -0.02), (5.8, 1.55, 0.1), water, 0.15)
for x, y, size in [(-4.5, -3.6, 0.55), (-2.8, -4.8, 0.4), (2.7, -4.0, 0.5), (4.5, -4.8, 0.35)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=size, location=(x, y, 0.15)); bpy.context.object.data.materials.append(stone)
cube('台基', (0, 0, 0.05), (3.7, 3.0, 0.35), stone, 0.12)
cube('前台阶', (0, -3.25, 0.0), (2.3, 0.55, 0.18), stone, 0.08)
cube('上层木地板', (0, 0, 0.48), (3.35, 2.65, 0.12), wood, 0.05)

# Vermilion pillars and capitals
for x in (-2.75, 2.75):
    for y in (-2.1, 2.1):
        cylinder('朱红立柱', (x, y, 2.65), 0.22, 4.25, red, 20)
        cylinder('柱础', (x, y, 0.72), 0.42, 0.22, gold, 20)
        cube('柱头', (x, y, 4.75), (0.42, 0.42, 0.12), gold, 0.05)

# Railings
for y in (2.35, -2.35):
    for x in (-1.85, 0, 1.85): cylinder('栏杆竖木', (x, y, 1.25), 0.09, 1.25, wood, 12)
    cube('栏杆横木', (0, y, 1.75), (2.85, 0.10, 0.10), wood, 0.03)
for x in (-3.0, 3.0):
    for y in (-0.9, 0.9): cylinder('侧栏竖木', (x, y, 1.25), 0.09, 1.25, wood, 12)
    cube('侧栏横木', (x, 0, 1.75), (0.10, 2.05, 0.10), wood, 0.03)

# Layered octagonal roof and finial
for z, radius, depth in [(5.0, 4.25, 0.22), (5.28, 3.75, 0.18), (5.52, 3.1, 0.15)]:
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=radius, radius2=0.35, depth=depth, location=(0, 0, z), rotation=(0, 0, math.radians(22.5)))
    bpy.context.object.name = '重檐瓦顶'; bpy.context.object.data.materials.append(dark)
cylinder('屋脊鎏金', (0, 0, 5.86), 0.18, 0.45, gold, 16)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.28, location=(0, 0, 6.12)); bpy.context.object.data.materials.append(gold)
for sx in (-1, 1):
    for sy in (-1, 1): cylinder('檐角装饰', (sx * 3.62, sy * 3.0, 5.18), 0.1, 0.9, gold, 12, (0, math.radians(-35 * sy), math.radians(12 * sx)))

# Glowing red lanterns
for x, y in [(-2.75, -2.1), (2.75, -2.1)]:
    cylinder('灯笼挂杆', (x, y, 4.25), 0.045, 0.65, gold, 12)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.34, location=(x, y, 3.78))
    obj = bpy.context.object; obj.name = '朱红灯笼'; obj.scale = (0.72, 0.72, 1.15); obj.data.materials.append(lantern)
    torus('灯笼金箍', (x, y, 3.78), 0.26, 0.035, gold); torus('灯笼下箍', (x, y, 3.43), 0.20, 0.03, gold)
    cylinder('灯笼穗', (x, y, 3.14), 0.035, 0.5, gold, 10)
    bpy.ops.object.light_add(type='POINT', location=(x, y, 3.8)); light = bpy.context.object; light.name = '灯笼暖光'; light.data.energy = 70; light.data.color = (1.0, 0.18, 0.045); light.data.shadow_soft_size = 0.5

# Background bamboo
for x in (-6.2, 5.8):
    for index in range(4):
        xx = x + (index - 1.5) * 0.22
        cylinder('竹竿', (xx, 2.9, 1.5 + index * 0.12), 0.07, 3.2, green, 10, (0, math.radians((index - 1.5) * 4), math.radians((index - 2) * 3)))
        for leaf_index in range(5):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.35, location=(xx + (leaf_index % 2) * 0.16, 2.9, 2.6 + leaf_index * 0.42))
            obj = bpy.context.object; obj.name = '竹叶'; obj.scale = (0.32, 0.16, 0.75); obj.data.materials.append(green)

# Night lighting and camera
world = bpy.data.worlds.new('夜色世界'); bpy.context.scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.008, 0.015, 0.028, 1); world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.22
bpy.ops.object.light_add(type='AREA', location=(3, -4, 8)); key = bpy.context.object; key.name = '月光'; key.data.energy = 850; key.data.shape = 'DISK'; key.data.size = 5; key.data.color = (0.35, 0.5, 1.0); key.rotation_euler = (math.radians(25), 0, math.radians(145))
bpy.ops.object.light_add(type='AREA', location=(-5, -1, 4)); fill = bpy.context.object; fill.name = '暖色补光'; fill.data.energy = 500; fill.data.size = 4; fill.data.color = (1.0, 0.18, 0.06); fill.rotation_euler = (math.radians(65), 0, math.radians(-55))
bpy.ops.object.camera_add(location=(10, -13, 8.2)); camera = bpy.context.object; camera.name = '亭子主相机'; bpy.context.scene.camera = camera; camera.data.lens = 52
camera.rotation_euler = (Vector((0, 0, 2.45)) - camera.location).to_track_quat('-Z', 'Y').to_euler()

scene = bpy.context.scene; scene.render.engine = 'BLENDER_EEVEE_NEXT'; scene.render.resolution_x = 900; scene.render.resolution_y = 700; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.render.filepath = 'chinese_pavilion.png'; scene.view_settings.look = 'AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath='chinese_pavilion.blend'); bpy.ops.render.render(write_still=True)
