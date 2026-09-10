"""Rounded, closed cat ears with pink material integrated into the front skin."""
import math
import bmesh


def build_ears(*, mesh, closed_catmull, fur, pink):
    # The broad tip turns over a rounded arc; no sharp corner or outline tube.
    outline = [(1.08, 4.00, 0), (1.39, 4.115, 0), (1.58, 4.245, 0),
               (1.70, 4.245, 0), (1.785, 4.125, 0), (1.805, 3.96, 0),
               (1.785, 3.755, 0), (1.70, 3.60, 0), (1.43, 3.66, 0)]
    perimeter = closed_catmull(outline, 12)
    cx = sum(p.x for p in perimeter)/len(perimeter)
    cz = sum(p.y for p in perimeter)/len(perimeter)
    pink_angle = math.asin(.73)
    angles = sorted(set([math.pi*i/64 for i in range(1, 64)] + [pink_angle]))
    count = len(perimeter)
    result = []

    def plane(x):
        return .12 + .60*(abs(x)-1.4)

    for sign, label in ((-1, 'L'), (1, 'R')):
        vertices = [(sign*cx, plane(cx)-.115+.014, cz)]
        for phi in angles:
            radius = math.sin(phi)
            for p in perimeter:
                x = cx + (p.x-cx)*radius
                z = cz + (p.y-cz)*radius
                y = plane(x)-.115*math.cos(phi)
                # A shallow inner cup joins the thick, softly rounded ear rim.
                if phi < pink_angle:
                    y += .014*(1-(radius/.73)**2)**2
                vertices.append((sign*x, y, z))
        rear = len(vertices)
        vertices.append((sign*cx, plane(cx)+.115, cz))
        faces = []
        pink_faces = []
        for i in range(count):
            faces.append((0, 1+i, 1+(i+1)%count))
            pink_faces.append(True)
        for j in range(len(angles)-1):
            for i in range(count):
                a = 1+j*count+i
                b = 1+j*count+(i+1)%count
                faces.append((a, b, b+count, a+count))
                pink_faces.append(angles[j+1] <= pink_angle+1e-8)
        last = 1+(len(angles)-1)*count
        for i in range(count):
            faces.append((last+i, rear, last+(i+1)%count))
            pink_faces.append(False)
        ear = mesh('Ear '+label+' • soft rounded shell and inset pink',
                   vertices, faces, fur)
        ear.data.materials.append(pink)
        for polygon, is_pink in zip(ear.data.polygons, pink_faces):
            polygon.material_index = int(is_pink)
        bm = bmesh.new(); bm.from_mesh(ear.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(ear.data); bm.free()
        sub = ear.modifiers.new('Soft ear surface', 'SUBSURF')
        sub.levels = 1; sub.render_levels = 1
        ear['design'] = 'Rounded volumetric ear; integral pink surface, no outline curves'
        result.append(ear)
    return {'revision': 'v4 rounded ears without drawn borders',
            'objects': [obj.name for obj in result],
            'outline_curves': False, 'shell_thickness': .23}
