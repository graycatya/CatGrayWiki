"""Rounded, closed cat ears with pink material integrated into the front skin."""
import math
import bmesh


def build_ears(*, mesh, closed_catmull, fur, pink, eargray):
    # A complete convex ear outline with its inner/root edges buried in the
    # approved head. Explicit Beziers avoid the concave lobes of the v4 rim.
    segments = [
        ((.72,4.10),(1.00,4.25),(1.49,4.36),(1.60,4.33)),
        ((1.60,4.33),(1.79,4.28),(1.86,3.68),(1.70,3.42)),
        ((1.70,3.42),(1.58,3.20),(1.23,3.14),(1.00,3.25)),
        ((1.00,3.25),(.76,3.35),(.58,3.82),(.72,4.10)),
    ]
    perimeter = []
    from mathutils import Vector
    for controls in segments:
        a,b,c,d = [Vector((x,z,0)) for x,z in controls]
        for i in range(32):
            t=i/32
            perimeter.append((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d)
    for p in perimeter:
        p.x = 1.43+(p.x-1.43)*.95
        p.y = 3.99+(p.y-3.99)*.95
    cx,cz = 1.4205,3.952
    pink_radius = .57
    pink_angle = math.asin(pink_radius)
    angles = sorted(set([math.pi*i/64 for i in range(1, 64)] + [pink_angle]))
    count = len(perimeter)
    result = []

    def plane(x):
        return .16 + .72*(abs(x)-1.4)

    for sign, label in ((-1, 'L'), (1, 'R')):
        vertices = [(sign*cx, plane(cx)-.085+.008, cz)]
        for phi in angles:
            radius = math.sin(phi)
            for p in perimeter:
                x = cx + (p.x-cx)*radius
                z = cz + (p.y-cz)*radius
                y = plane(x)-.085*math.cos(phi)
                # A shallow inner cup joins the thick, softly rounded ear rim.
                if phi < pink_angle:
                    y += .008*(1-(radius/pink_radius)**2)**2
                vertices.append((sign*x, y, z))
        rear = len(vertices)
        vertices.append((sign*cx, plane(cx)+.085, cz))
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
        ear = mesh('Ear '+label+' • reference gray shell and smaller pink inset',
                   vertices, faces, eargray)
        ear.data.materials.append(pink)
        for polygon, is_pink in zip(ear.data.polygons, pink_faces):
            polygon.material_index = int(is_pink)
        bm = bmesh.new(); bm.from_mesh(ear.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(ear.data); bm.free()
        sub = ear.modifiers.new('Soft ear surface', 'SUBSURF')
        sub.levels = 1; sub.render_levels = 1
        ear['design'] = 'Convex reference ear; gray #747474, smaller pink #FFA3A3, hidden root'
        ear['pink_radius'] = pink_radius
        ear['shell_color'] = '#747474'
        ear['inner_color'] = '#FFA3A3'
        result.append(ear)
    return {'revision': 'v5 convex reference ears with smaller pink region',
            'objects': [obj.name for obj in result],
            'outline_curves': False, 'shell_thickness': .17,
            'shell_srgb': '#747474', 'pink_srgb': '#FFA3A3',
            'pink_radius': pink_radius}
