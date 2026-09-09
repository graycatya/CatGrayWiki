"""Bare CatGray body with one connected skin and a baked oval belly marking.

Coordinates follow build_cat.py: X left/right, -Y front, Z up. The neck is
deliberately broad and extends inside the head. Geometry and belly dimensions
are exposed below so the silhouette can be adjusted without changing the UVs.
"""
import math
from pathlib import Path
import struct
import zlib

import bpy
import bmesh
import numpy as np


BODY_TOP = 1.64
VOXEL_SIZE = .015
SMOOTH_ITERATIONS = 14
SUBDIVISION_LEVELS = 1
TEXTURE_SIZE = 2048
BELLY_WIDTH = .78
BELLY_HEIGHT = .92
BELLY_CENTER_Z = .91
BELLY_EDGE_WIDTH = .0078
FUR_RGB = (151, 151, 151)
BELLY_RGB = (244, 243, 240)

# z, half width, front Y, rear Y. There is no hem or waist step: the lower
# abdomen rounds smoothly into the pelvis and the upper chest into the neck.
TORSO_PROFILE = [
    (.335, .105, -.030, .095),
    (.390, .255, -.140, .235),
    (.465, .405, -.285, .330),
    (.560, .500, -.390, .410),
    (.715, .580, -.465, .465),
    (.890, .602, -.477, .481),
    (1.080, .566, -.427, .452),
    (1.245, .500, -.360, .405),
    (1.400, .440, -.290, .350),
    (1.520, .410, -.267, .330),
    (BODY_TOP, .330, -.235, .295),
]

# z, center X, center Y, X radius, Y radius. Each complete arm is a single
# tapered volume, with a rounded paw tip and a broad concealed shoulder.
ARM_PROFILE = [
    (.388, .730, -.018, .006, .009),
    (.410, .732, -.020, .065, .082),
    (.456, .739, -.020, .110, .139),
    (.555, .744, -.017, .127, .177),
    (.700, .730, -.007, .145, .198),
    (.855, .679, .009, .178, .220),
    (1.035, .572, .018, .211, .240),
    (1.230, .454, .023, .207, .232),
    (1.360, .376, .027, .154, .185),
    (1.475, .305, .028, .125, .150),
    (1.580, .280, .028, .075, .105),
    (1.635, .280, .028, .025, .040),
]

# The toes, instep and legs share a loft; there are no separate shoe spheres.
LEG_PROFILE = [
    (.000, .248, -.090, .143, .175),
    (.018, .248, -.092, .191, .224),
    (.065, .248, -.094, .222, .256),
    (.133, .248, -.069, .216, .240),
    (.218, .250, -.007, .189, .204),
    (.325, .247, .032, .203, .231),
    (.430, .237, .037, .235, .264),
    (.535, .220, .037, .263, .286),
    (.610, .216, .034, .236, .266),
]


def _write_png(path, rgba):
    """Write exact sRGB bytes, avoiding Blender generated-image transforms."""
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff))

    height, width = rgba.shape[:2]
    # The image was calculated bottom-up to match UV coordinates. PNG rows
    # run top-down, so reverse them before writing the scanlines.
    raw = b''.join(b'\x00' + row.tobytes() for row in rgba[::-1])
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
        + chunk(b'sRGB', b'\x00')
        + chunk(b'IDAT', zlib.compress(raw, 6))
        + chunk(b'IEND', b''))


def build_body(*, mesh, curve, ellipsoid, patch, ring_mesh, interpolate,
               front_surface, fur, material, out):
    """Build the skin mesh and packed image; return JSON-safe revision data.

    The helper signature matches the other body builder for straightforward
    integration. curve, patch, front_surface and material are accepted for
    compatibility but no extra surface pieces are needed for this body.
    """
    out = Path(out)

    def apply_modifier(obj, modifier):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    def loft(name, profile, sign=1, sections=64, around=72):
        verts, faces = [], []
        for j in range(sections + 1):
            z = profile[0][0] + (profile[-1][0] - profile[0][0]) * j / sections
            cx, cy, rx, ry = [interpolate(profile, z, c) for c in range(1, 5)]
            for i in range(around):
                theta = math.tau * i / around
                verts.append((sign * (cx + rx * math.cos(theta)),
                              cy + ry * math.sin(theta), z))
        for j in range(sections):
            for i in range(around):
                k = j * around + i
                nxt = j * around + (i + 1) % around
                faces.append((k, nxt, nxt + around, k + around))
        faces.append(tuple(reversed(range(around))))
        faces.append(tuple(sections * around + i for i in range(around)))
        return mesh(name, verts, faces, fur)

    parts = [ring_mesh('Body volume • torso and broad neck', TORSO_PROFILE,
                       fur, power=2.0, nz=90, nt=112)]
    parts.append(ellipsoid('Body volume • pelvis', (0, .040, .458),
                           (.430, .305, .181), fur))
    for sign, label in ((-1, 'L'), (1, 'R')):
        parts.append(loft('Body volume • arm ' + label, ARM_PROFILE, sign))
        parts.append(loft('Body volume • leg and paw ' + label, LEG_PROFILE,
                          sign, sections=58))

    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            apply_modifier(obj, modifier)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = 'Body • continuous bare skin and painted oval belly'

    # Voxel remeshing requires watertight input. Join the duplicate seam on
    # the torso loft and correct normals after the mirrored arm/leg lofts.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.0003)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(body.data)
    bm.free()
    body.data.remesh_voxel_size = VOXEL_SIZE
    body.data.use_remesh_preserve_volume = True
    bpy.ops.object.voxel_remesh()
    smooth = body.modifiers.new('Blend the continuous skin junctions', 'SMOOTH')
    smooth.factor = .72
    smooth.iterations = SMOOTH_ITERATIONS
    apply_modifier(body, smooth)

    # Move only by the tiny remeshing offset, then flatten the lowest part of
    # both soles. The feet remain continuous with the short legs.
    bottom = min(v.co.z for v in body.data.vertices)
    for vertex in body.data.vertices:
        vertex.co.z -= bottom
        if vertex.co.z < .012:
            vertex.co.z = 0
    body.data.update()
    for polygon in body.data.polygons:
        polygon.use_smooth = True

    # Two non-overlapping planar UV islands occupy the two atlas halves.
    # Front/back classification is along the body center, far from the belly
    # outline, so the white region never bleeds onto the back. The arm and
    # paw UV coordinates retain their real X values and remain outside it.
    for old_uv in list(body.data.uv_layers):
        body.data.uv_layers.remove(old_uv)
    uv = body.data.uv_layers.new(name='BodyBellyUV')
    uv.active_render = True
    for polygon in body.data.polygons:
        front = polygon.center.y < .020
        for loop_index in polygon.loop_indices:
            co = body.data.vertices[body.data.loops[loop_index].vertex_index].co
            u = .25 + .23 * co.x + (0 if front else .5)
            v = .02 + .96 * co.z / 1.70
            uv.data[loop_index].uv = (u, v)

    size = TEXTURE_SIZE
    uu = (np.arange(size, dtype=np.float32)[None, :] + .5) / size
    vv = (np.arange(size, dtype=np.float32)[:, None] + .5) / size
    xx = (uu - .25) / .23
    zz = (vv - .02) * 1.70 / .96
    distance = np.sqrt((xx / (BELLY_WIDTH / 2)) ** 2
                       + ((zz - BELLY_CENTER_Z) / (BELLY_HEIGHT / 2)) ** 2)
    # A sub-pixel/small physical transition follows the same ellipse. No
    # raised border, decal shell or separate white material is involved.
    edge = BELLY_EDGE_WIDTH / (BELLY_WIDTH / 2)
    alpha = np.clip((1 + edge / 2 - distance) / edge, 0, 1)
    alpha = alpha * alpha * (3 - 2 * alpha)
    alpha *= (uu < .5)
    gray = np.asarray(FUR_RGB, dtype=np.float32)
    white = np.asarray(BELLY_RGB, dtype=np.float32)
    pixels = np.empty((size, size, 4), dtype=np.uint8)
    pixels[:, :, :3] = np.rint(gray + (white - gray) * alpha[:, :, None])
    pixels[:, :, 3] = 255
    texture_path = out / 'CatGray_BareBody_BaseColor.png'
    _write_png(texture_path, pixels)
    texture = bpy.data.images.load(str(texture_path), check_existing=False)
    texture.name = 'CatGray_BareBody_BaseColor'
    texture.colorspace_settings.name = 'sRGB'
    texture.pack()

    skin = fur.copy()
    skin.name = 'Fur | bare body with UV painted white oval'
    nodes = skin.node_tree.nodes
    image_node = nodes.new('ShaderNodeTexImage')
    image_node.name = 'Baked front belly basecolor'
    image_node.label = 'Gray fur and front-only warm white oval'
    image_node.image = texture
    image_node.interpolation = 'Linear'
    image_node.extension = 'EXTEND'
    uv_node = nodes.new('ShaderNodeUVMap')
    uv_node.uv_map = uv.name
    skin.node_tree.links.new(uv_node.outputs['UV'], image_node.inputs['Vector'])
    skin.node_tree.links.new(image_node.outputs['Color'],
                            nodes.get('Principled BSDF').inputs['Base Color'])
    body.data.materials.clear()
    body.data.materials.append(skin)
    for polygon in body.data.polygons:
        polygon.material_index = 0

    # Verify the topology before adding the final smooth surface. These are
    # useful build facts for the manifest and catch any accidental detachment.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    remaining = set(bm.verts)
    components = 0
    while remaining:
        components += 1
        todo = [remaining.pop()]
        while todo:
            vertex = todo.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    todo.append(other)
    non_manifold_edges = sum(not edge.is_manifold for edge in bm.edges)
    bm.free()
    if components != 1 or non_manifold_edges:
        raise RuntimeError('Bare body must be one closed skin volume: '
                           f'{components} components, '
                           f'{non_manifold_edges} non-manifold edges')

    sub = body.modifiers.new('Smooth continuous body silhouette', 'SUBSURF')
    sub.levels = SUBDIVISION_LEVELS
    sub.render_levels = SUBDIVISION_LEVELS
    body['surface_design'] = 'One bare skin; front belly is part of basecolor image'
    body['belly_width'] = BELLY_WIDTH
    body['belly_height'] = BELLY_HEIGHT
    body['belly_center_z'] = BELLY_CENTER_Z
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    final_mesh = evaluated.to_mesh()
    triangle_count = sum(len(p.vertices) - 2 for p in final_mesh.polygons)
    evaluated.to_mesh_clear()

    return {
        'revision': 'bare body with continuous shoulders and short legs',
        'body_object': body.name,
        'skin_connected_components': components,
        'skin_non_manifold_edges': non_manifold_edges,
        'evaluated_triangles': triangle_count,
        'voxel_size': VOXEL_SIZE,
        'width_with_arms': round(float(body.dimensions.x), 4),
        'height': round(float(body.dimensions.z), 4),
        'neck_profile_width_at_z_1_4': .880,
        'belly': {
            'type': 'packed sRGB basecolor image, front surface only',
            'texture': texture_path.name,
            'resolution': [size, size],
            'width': BELLY_WIDTH,
            'height': BELLY_HEIGHT,
            'center_z': BELLY_CENTER_Z,
            'edge_width': BELLY_EDGE_WIDTH,
            'fur_srgb': '#979797',
            'belly_srgb': '#F4F3F0',
        },
    }
