"""CatGray solid voxel design and MagicaVoxel 150 writer; standard library only.

Grid cell centers: ((x + .5) * step, (y + .5) * step, (z + .5) * step).
Blender coordinates are Z up, front -Y. Colors use one-based VOX indices.
"""
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
NAME = "CatGray_Voxel"
DIRECTIONS = (
    ((1, 0, 0), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((-1, 0, 0), ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1))),
    ((0, 1, 0), ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
    ((0, 0, -1), ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0))),
)

# z, half-width, front and rear depths. Deliberate broad, stepped contours.
HEAD = [
    (1.65, .52, -.40, .60), (1.80, 1.04, -.85, 1.00),
    (2.05, 1.42, -1.15, 1.27), (2.35, 1.65, -1.37, 1.43),
    (2.70, 1.75, -1.40, 1.48), (3.35, 1.73, -1.27, 1.43),
    (3.70, 1.60, -1.13, 1.32), (4.00, 1.36, -.92, 1.08),
    (4.20, .94, -.62, .73), (4.30, .44, -.26, .35),
]
BODY = [
    (.35, .35, -.24, .30), (.55, .54, -.40, .44),
    (.90, .64, -.49, .50), (1.20, .62, -.44, .47),
    (1.50, .50, -.33, .39), (1.85, .38, -.25, .32),
]
TAIL = [(-.10, .35, .60), (-.45, .65, .60), (-.95, .95, .70),
        (-1.35, 1.10, .90), (-1.53, 1.18, 1.20),
        (-1.50, 1.20, 1.48), (-1.32, 1.22, 1.60)]


def settings():
    config = json.loads((ROOT / "source/settings.json").read_text())
    if not .06 <= config["voxel_size"] <= .16:
        raise ValueError("voxel_size must be between 0.06 and 0.16")
    if len(config["palette"]) != 11:
        raise ValueError("This design requires the eleven semantic palette entries")
    return config


def profile_at(profile, z):
    if not profile[0][0] <= z <= profile[-1][0]:
        return None
    for a, b in zip(profile, profile[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + t * (b[i] - a[i]) for i in (1, 2, 3))


def in_loft(x, y, p, power=2.6):
    if p is None:
        return False
    width, front, back = p
    mid = (front + back) / 2
    return (abs(x / width) ** power
            + abs((y - mid) / ((back - front) / 2)) ** power <= 1)


def segment_distance(point, a, b):
    ab = tuple(b[i] - a[i] for i in range(3))
    t = sum((point[i] - a[i]) * ab[i] for i in range(3)) / sum(v*v for v in ab)
    t = max(0, min(1, t))
    return sum((point[i] - a[i] - t * ab[i]) ** 2 for i in range(3)) ** .5


def triangle_contains(x, z, a, b, c):
    def cross(p, q):
        return (q[0]-p[0])*(z-p[1]) - (q[1]-p[1])*(x-p[0])
    signs = (cross(a, b), cross(b, c), cross(c, a))
    return min(signs) >= 0 or max(signs) <= 0


def face_color(x, z):
    # Bigger iris rings and square glints are drawn for the voxel grid.
    for cx in (-.80, .80):
        dx, dz = x-cx, z-3.00
        radius = math.hypot(dx, dz)
        if radius <= .455:
            color = 5
            if radius <= .385:
                color = 6
            if radius <= .345:
                color = 7 if dz > -.12 else 8
            if radius <= .255:
                color = 9
            # Mirrored large glints and one-pixel secondary glints.
            glint_x = -.12 if cx < 0 else .12
            if abs(dx-glint_x) <= .08 and abs(dz-.14) <= .08:
                color = 10
            if abs(dx+glint_x) <= .035 and abs(dz+.20) <= .04:
                color = 10
            return color
    if abs(x) <= .16 and 2.65 <= z <= 2.76:
        return 5
    if abs(x) <= .055 and 2.51 <= z < 2.65:
        return 5
    if abs(x) <= .26 and 2.45 <= z <= 2.54:
        return 5
    if 2.17 <= z < 2.45:
        width = .07 + .13 * (z-2.17)/.28
        if abs(x) <= width:
            return 11 if abs(x) < width-.065 and z > 2.23 else 5
    return None


def generate(config):
    step = config["voxel_size"]
    voxels, head_cells, body_cells = {}, set(), set()
    for k in range(math.ceil(4.8/step)):
        z = (k+.5)*step
        hp, bp = profile_at(HEAD, z), profile_at(BODY, z)
        for i in range(math.floor(-1.9/step), math.ceil(1.9/step)):
            x = (i+.5)*step
            ax = abs(x)
            ear = triangle_contains(ax, z, (.90, 3.70), (1.83, 3.75), (1.62, 4.76))
            pink = triangle_contains(ax, z, (1.16, 3.93), (1.66, 3.95), (1.57, 4.53))
            for j in range(math.floor(-1.6/step), math.ceil(1.6/step)):
                y = (j+.5)*step
                key, color = (i, j, k), None
                if -.12 <= y <= .38 and ear:
                    color = 3 if y < .05 and pink else 2
                if in_loft(x, y, bp, 2.6):
                    color = 1
                    body_cells.add(key)
                # Short block paws connect to the underside of the torso.
                if z <= .65 and abs(ax-.30) <= .23 and -.39 <= y <= .30:
                    if not (abs(ax-.30) > .17 and y < -.30):
                        color = 1
                # Relaxed arms, with one cell of clearance below the shoulder.
                if .55 <= z <= 1.72:
                    arm_x = .84 if z < 1.35 else .84-(z-1.35)*.60
                    if abs(ax-arm_x) <= .16 and abs(y) <= .22:
                        color = 1
                if x < .10 and y >= .20 and z <= 1.80:
                    if any(segment_distance((x,y,z), a,b) <= .16
                           for a,b in zip(TAIL, TAIL[1:])):
                        color = 1
                if in_loft(x, y, hp):
                    color = 1
                    head_cells.add(key)
                    # Four forehead stripes run continuously over the crown.
                    if z > 3.78:
                        t = min(1, (z-3.78)/.48)
                        if any(abs(ax-c) < .065+.035*t for c in (.20+.02*t, .57+.07*t)):
                            color = 2
                    # Three stair-step cheek stripes on each side, wrapping rearward.
                    if ax > 1.38 and y > -.90:
                        if any(abs(z-(level+.11*(ax-1.4))) < .065
                               for level in (2.30, 2.60, 2.90)):
                            color = 2
                if color is not None:
                    voxels[key] = color
    # Paint only the visible front layer, so facial colors cannot bleed to the back.
    for cells, is_head in ((head_cells, True), (body_cells, False)):
        front = {}
        for i,j,k in cells:
            front[i,k] = min(j, front.get((i,k), j))
        for (i,k), j in front.items():
            x,z = (i+.5)*step, (k+.5)*step
            color = face_color(x,z) if is_head else (
                4 if (x/.44)**2 + ((z-1.07)/.54)**2 <= 1 else None)
            if color is not None:
                voxels[i,j,k] = color
    # Fill rare diagonal-only contacts where the arms/tail meet the body.
    # Four faces sharing one edge would otherwise make the surface non-manifold.
    for _ in range(8):
        additions = set()
        minimum = tuple(min(p[i] for p in voxels)-1 for i in range(3))
        maximum = tuple(max(p[i] for p in voxels)+1 for i in range(3))
        for x in range(minimum[0], maximum[0]):
            for y in range(minimum[1], maximum[1]):
                for z in range(minimum[2], maximum[2]):
                    p = (x,y,z)
                    for a,b in ((0,1),(0,2),(1,2)):
                        square = [tuple(p[i] + (u if i == a else v if i == b else 0)
                                        for i in range(3)) for u,v in ((0,0),(1,0),(0,1),(1,1))]
                        present = tuple(q in voxels for q in square)
                        if present in ((True,False,False,True),(False,True,True,False)):
                            additions.update(q for q in square if q not in voxels)
        if not additions:
            return voxels
        voxels.update((p,1) for p in additions)
    raise RuntimeError("Unable to close diagonal voxel contacts")


def surface_mesh(voxels, step):
    vertices, faces, colors, indices = [], [], [], {}
    for (x,y,z), color in sorted(voxels.items()):
        for (dx,dy,dz), corners in DIRECTIONS:
            if (x+dx, y+dy, z+dz) in voxels:
                continue
            face = []
            for a,b,c in corners:
                key = (x+a, y+b, z+c)
                if key not in indices:
                    indices[key] = len(vertices)
                    vertices.append(tuple(v*step for v in key))
                face.append(indices[key])
            faces.append(face)
            colors.append(color-1)
    return vertices, faces, colors


def write_vox(path, voxels, palette):
    minimum = tuple(min(p[i] for p in voxels) for i in range(3))
    size = tuple(max(p[i] for p in voxels)-minimum[i]+1 for i in range(3))
    if max(size) > 256:
        raise ValueError("VOX 150 coordinates must fit into one byte")
    def chunk(name, content=b"", children=b""):
        return name + struct.pack("<II",len(content),len(children)) + content + children
    data = b"".join(bytes((*(p[i]-minimum[i] for i in range(3)),c))
                    for p,c in sorted(voxels.items()))
    rgba = b"".join(bytes.fromhex(c["hex"])+b"\xff" for c in palette)
    rgba += b"\x00\x00\x00\xff" * (256-len(palette))
    children = (chunk(b"SIZE",struct.pack("<3I",*size))
                + chunk(b"XYZI",struct.pack("<I",len(voxels))+data)
                + chunk(b"RGBA",rgba))
    path.write_bytes(b"VOX " + struct.pack("<I",150) + chunk(b"MAIN",children=children))
    return {"grid_minimum": minimum, "grid_dimensions": size}


def read_vox(path):
    """Read the single-model subset emitted here; reject corrupt chunk lengths."""
    data = path.read_bytes()
    if data[:8] != b"VOX \x96\x00\x00\x00" or data[8:12] != b"MAIN":
        raise ValueError("Expected a MagicaVoxel 150 MAIN chunk")
    content, children = struct.unpack_from("<II",data,12)
    if content != 0 or children+20 != len(data):
        raise ValueError("Invalid MAIN length")
    offset, size, voxels, palette = 20, None, None, None
    while offset < len(data):
        kind = data[offset:offset+4]
        n, m = struct.unpack_from("<II",data,offset+4)
        start, end = offset+12, offset+12+n
        if end+m > len(data):
            raise ValueError("Truncated VOX chunk")
        payload = data[start:end]
        if kind == b"SIZE":
            size = struct.unpack("<3I",payload)
        elif kind == b"XYZI":
            count, = struct.unpack_from("<I",payload)
            if len(payload) != 4+count*4:
                raise ValueError("Invalid XYZI count")
            voxels = {tuple(payload[i:i+3]):payload[i+3] for i in range(4,len(payload),4)}
            if len(voxels) != count:
                raise ValueError("Duplicate voxel coordinates")
        elif kind == b"RGBA":
            if n != 1024:
                raise ValueError("Invalid palette size")
            palette = [tuple(payload[i:i+4]) for i in range(0,n,4)]
        offset = end+m
    if not size or not voxels or not palette:
        raise ValueError("Missing SIZE, XYZI or RGBA")
    if not all(all(0 <= p[i] < size[i] for i in range(3)) and 1 <= c <= 255
               for p,c in voxels.items()):
        raise ValueError("Voxel outside grid or invalid color index")
    return size, voxels, palette
