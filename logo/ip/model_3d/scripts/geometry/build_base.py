"""Build the approved static source geometry; use manage.py build-base.
Blender 5.2.1 validated. Outputs source/CatGray_Base.blend, never the rig.
"""
import bpy
import bmesh
import math
import json
import sys
from pathlib import Path
from mathutils import Vector
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'source'
REF = ROOT.parent/'references'
TEXTURES = ROOT/'textures'
PREVIEWS = ROOT/'previews'
for directory in (OUT,TEXTURES,PREVIEWS):directory.mkdir(exist_ok=True)
QUICK = '--quick' in sys.argv
BUILD_ONLY = '--build-only' in sys.argv
TAU = math.tau
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):
    bpy.data.materials.remove(data)

model = bpy.data.collections.new('CATGRAY • Character')
bpy.context.scene.collection.children.link(model)
studio = bpy.data.collections.new('STUDIO • Cameras and lighting')
bpy.context.scene.collection.children.link(studio)
references = bpy.data.collections.new('REFERENCES • Original three views')
bpy.context.scene.collection.children.link(references)
references.hide_render = True

def move_to(obj, collection=model):
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def linear(v):
    return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4

def material(name, hexcolor, roughness=.64, metallic=0):
    rgb = tuple(int(hexcolor[i:i+2], 16)/255 for i in (0, 2, 4))
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*(linear(c) for c in rgb), 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    return mat

fur = material('Fur | reference #979797', '979797')
eargray = material('Ear rims | reference #747474', '747474', .78)
eargray.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.18
pink = material('Inner ears | reference #FFA3A3', 'FFA3A3', .78)
pink.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.18
tongue_mat = material('Tongue | warm pink', 'FF939A', .5)
dark = material('Outlines and seams | charcoal', '232320', .67)
nose_mat = material('Nose | reference #2D2D2D', '2D2D2D', .5)
iris_outer = material('Iris | deep amber edge', '995207', .34)
iris_gold = material('Iris | golden orange', 'F79708', .3)
iris_light = material('Iris | lower honey highlight', 'FFC451', .34)
for eye_mat in (iris_outer,iris_gold):
    tint=eye_mat.node_tree.nodes.new('ShaderNodeVertexColor');tint.layer_name='EyeTint'
    eye_mat.node_tree.links.new(tint.outputs['Color'],eye_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
pupil = material('Pupil | round black', '080A09', .32)
pupil.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
sparkle = material('Eyes | painted white catchlights', 'FFFFFF', .25)
sparkle.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value = (1,1,1,1)
sparkle.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value = .25

def mesh(name, vertices, faces, mat, uv=None, sub=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    model.objects.link(obj)
    data.materials.append(mat)
    if mat in (iris_outer,iris_gold):
        tint=data.color_attributes.new(name='EyeTint',type='FLOAT_COLOR',domain='POINT')
        upper,lower=((.52,.27,.025),(.80,.42,.018)) if mat==iris_outer else ((.75,.38,.006),(1,.65,.025))
        for i,v in enumerate(data.vertices):
            t=max(0,min(1,(2.835+.33-v.co.z)/.66))
            tint.data[i].color=(*(linear(upper[k]+t*(lower[k]-upper[k])) for k in range(3)),1)
    for p in data.polygons:
        p.use_smooth = True
    if uv:
        layer = data.uv_layers.new(name='SurfaceUV')
        for poly in data.polygons:
            for li in poly.loop_indices:
                layer.data[li].uv = uv[data.loops[li].vertex_index]
    if sub:
        mod = obj.modifiers.new('Smooth surface', 'SUBSURF')
        mod.levels = sub
        mod.render_levels = sub
    return obj

def ellipsoid(name, location, scale, mat, segments=64, rings=40):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = move_to(bpy.context.object)
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def curve(name, points, radius, mat, cyclic=False):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 24
    data.bevel_depth = radius
    data.bevel_resolution = 4
    data.use_fill_caps = True
    spline = data.splines.new('BEZIER')
    spline.bezier_points.add(len(points)-1)
    for b, co in zip(spline.bezier_points, points):
        b.co = co
        b.handle_left_type = b.handle_right_type = 'AUTO'
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    model.objects.link(obj)
    data.materials.append(mat)
    return obj

def interpolate(table, z, column):
    if z <= table[0][0]: return table[0][column]
    if z >= table[-1][0]: return table[-1][column]
    for i in range(len(table)-1):
        if table[i][0] <= z <= table[i+1][0]:
            a, b = table[i], table[i+1]
            t = (z-a[0])/(b[0]-a[0])
            prev, nxt = table[max(i-1,0)], table[min(i+2,len(table)-1)]
            ma = (b[column]-prev[column])/(b[0]-prev[0])
            mb = (nxt[column]-a[column])/(nxt[0]-a[0])
            return ((2*t**3-3*t*t+1)*a[column] + (t**3-2*t*t+t)*(b[0]-a[0])*ma
                    +(-2*t**3+3*t*t)*b[column]+(t**3-t*t)*(b[0]-a[0])*mb)

# Frontal widths remain traced from the original front/back silhouettes.
# A fuller upper occiput and straighter rear wall replace the spherical back.
# The three drawings are stylized rather than exact orthographic projections.
# Ring columns: height, half width, front Y, rear Y.
HEAD = [
    (1.405,.001,.12,.12), (1.445,.47,-.37,.64),
    (1.51,.79,-.70,.95), (1.64,1.11,-1.00,1.23),
    (1.82,1.34,-1.24,1.43), (2.04,1.51,-1.43,1.55),
    (2.27,1.64,-1.56,1.62), (2.51,1.72,-1.60,1.645),
    (2.78,1.76,-1.51,1.63), (3.03,1.76,-1.37,1.595),
    (3.28,1.72,-1.27,1.54), (3.57,1.63,-1.18,1.435),
    (3.83,1.47,-1.02,1.265), (4.03,1.25,-.83,1.055),
    (4.20,.91,-.58,.755), (4.30,.54,-.34,.400),
    (4.355,.001,-.03,-.03)
]
POWER = 1.72

def ring_xyz(theta,z,table=HEAD,power=POWER):
    rx=max(.001,interpolate(table,z,1))
    fr=interpolate(table,z,2)
    bk=interpolate(table,z,3)
    mid=(fr+bk)*.5
    ry=(bk-fr)*.5
    s,c=math.sin(theta),math.cos(theta)
    return (rx*math.copysign(abs(s)**(2/power),s),
            mid-ry*math.copysign(abs(c)**(2/power),c),z)

def front_surface(x,z,offset=0,table=HEAD,power=POWER):
    rx=max(.001,interpolate(table,z,1))
    fr=interpolate(table,z,2)
    bk=interpolate(table,z,3)
    h=max(0,1-(min(abs(x)/rx,.9999))**power)**(1/power)
    return (fr+bk)*.5-(bk-fr)*.5*h-offset

def ring_mesh(name,table,mat,power=POWER,nz=110,nt=160):
    vertices=[]; faces=[]; uv=[]
    for j in range(nz+1):
        v=j/nz
        z=table[0][0]+(table[-1][0]-table[0][0])*v
        for i in range(nt+1):
            vertices.append(ring_xyz(TAU*i/nt,z,table,power))
            uv.append((i/nt,v))
    for j in range(nz):
        for i in range(nt):
            k=j*(nt+1)+i
            faces.append((k,k+1,k+nt+2,k+nt+1))
    faces.append(tuple(reversed(range(nt))))
    k=nz*(nt+1)
    faces.append(tuple(k+i for i in range(nt)))
    obj=mesh(name,vertices,faces,mat,uv)
    # Weld the UV seam geometrically while retaining independent UV loops.
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free()
    return obj

# Paint the markings into a UV texture. They never float above the skin.
# The contour landmarks and base colors are traced from the supplied drawings.
W,H=2048,1536
uu,vv=np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H)
zz=HEAD[0][0]+vv*(HEAD[-1][0]-HEAD[0][0])
theta=uu*TAU
rx=np.array([interpolate(HEAD,float(z),1) for z in zz[:,0]])[:,None]
xx=rx*np.sign(np.sin(theta))*np.abs(np.sin(theta))**(2/POWER)
mark=np.zeros((H,W),dtype=float)
# Smooth vector contours traced from the four forehead stripes. Extending the
# same contours over the crown avoids projection seams at the top of the head.
for tip,top,zmin,width in ((-.38,-.595,3.755,.122),(-.095,-.18,3.810,.102),
                           (.145,.215,3.807,.102),(.442,.565,3.815,.112)):
    t=np.clip((zz-zmin)/.53,0,1)
    center=tip+(top-tip)*t**.72
    halfwidth=width*t**.60
    distance=np.abs(xx-center)-halfwidth
    stripe_strength=np.clip(.5-distance/.005,0,1)*(zz>zmin)
    mark=np.maximum(mark,stripe_strength)
for center in (math.pi*.5,math.pi*1.5):
    dt=np.abs((theta-center+math.pi)%TAU-math.pi)
    for zbase,length,height in ((2.70,.30,.053),(2.38,.41,.060),(2.09,.29,.052)):
        zcenter=zbase+.20*np.cos(dt*1.9)
        val=(dt/length)**2+((zz-zcenter)/height)**2
        mark=np.maximum(mark,np.clip((1-val)*15,0,1))
base=np.array([151,151,151],dtype=float)/255
stripe=np.array([116,116,116],dtype=float)/255
rgba=np.ones((H,W,4),dtype=np.float32)
rgba[:,:,:3]=base+(stripe-base)*mark[:,:,None]
tex=bpy.data.images.new('CatGray_Fur_BaseColor',width=W,height=H,alpha=True)
tex.pixels.foreach_set(rgba.ravel())
tex.filepath_raw=str(TEXTURES/'CatGray_Fur_BaseColor.png')
tex.file_format='PNG'
tex.save()
# Reload from disk so Blender treats these as sRGB base-color samples, exactly
# like the solid fur material. Generated image buffers otherwise stay linear.
tex=bpy.data.images.load(str(TEXTURES/'CatGray_Fur_BaseColor.png'),check_existing=False)
tex.pack()
headmat=fur.copy(); headmat.name='Fur | UV painted tabby stripes'
node=headmat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=tex
headmat.node_tree.links.new(node.outputs['Color'],headmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
head=ring_mesh('Head • continuous shaped surface',HEAD,headmat,nz=180,nt=256)
head['revision']='v3: fuller upper occiput, straighter rear contour, retained frontal widths'

# Rounded 3D ear shells, with inset pink patches facing forwards and sideways.
def closed_catmull(points,steps=10):
    result=[]
    for i in range(len(points)):
        p0,p1,p2,p3=[Vector(points[j%len(points)]) for j in (i-1,i,i+1,i+2)]
        for k in range(steps):
            t=k/steps
            result.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    return result

def patch(name,outline,project,mat,bulge=.025,rings=10,outline_mat=None,outline_radius=.012):
    edge=closed_catmull([(x,z,0) for x,z in outline],8)
    cx=sum(p.x for p in edge)/len(edge); cz=sum(p.y for p in edge)/len(edge)
    n=len(edge); verts=[]; faces=[]
    for j in range(rings+1):
        r=max(.0001,j/rings)
        for p in edge:
            x=cx+(p.x-cx)*r; z=cz+(p.y-cz)*r
            verts.append((x,project(x,z)-bulge*(1-r*r),z))
    for j in range(rings):
        for i in range(n):
            k=j*n+i; kn=j*n+(i+1)%n
            faces.append((k,kn,kn+n,k+n))
    faces.append(tuple(reversed(range(n))))
    obj=mesh(name,verts,faces,mat)
    # Mirroring an outline must not reverse the shell's solidification direction.
    if sum(p.normal.y*p.area for p in obj.data.polygons)>0:
        for p in obj.data.polygons:p.flip()
        obj.data.update()
    if outline_mat:
        curve(name+' • perimeter',[(p.x,project(p.x,p.y)-.001,p.y) for p in edge],outline_radius,outline_mat,True)
    return obj

sys.path.insert(0,str(Path(__file__).resolve().parent))
from soft_ears import build_ears
ear_revision=build_ears(mesh=mesh,closed_catmull=closed_catmull,fur=fur,pink=pink,eargray=eargray)

# Eyes: shallow convex surfaces anchored to the head, round pupil, amber iris.
EYE_Z=2.835
EYE_R=.390
def eye_y(x,z,cx):
    q=min(1,((x-cx)/EYE_R)**2+((z-EYE_Z)/EYE_R)**2)
    return front_surface(x,z,.014+.065*(1-q))

def eye_ring(name,cx,ra,rb,mat,offset=0):
    verts=[]; faces=[]; n=128; rows=8
    for j in range(rows+1):
        r=max(.0001,ra+(rb-ra)*j/rows)
        for i in range(n):
            a=TAU*i/n; x=cx+r*math.cos(a); z=EYE_Z+r*math.sin(a)
            verts.append((x,eye_y(x,z,cx)-offset,z))
    for j in range(rows):
        for i in range(n):
            k=j*n+i;kn=j*n+(i+1)%n
            faces.append((k,k+n,kn+n,kn))
    return mesh(name,verts,faces,mat)

for cx,label in ((-.765,'L'),(.775,'R')):
    eye_ring('Eye '+label+' • charcoal socket',cx,0,EYE_R,dark)
    eye_ring('Eye '+label+' • amber outer edge',cx,0,.331,iris_outer,.004)
    eye_ring('Eye '+label+' • orange iris',cx,0,.298,iris_gold,.008)
    eye_ring('Eye '+label+' • pupil',cx,0,.241,pupil,.015)
    # The thin warm lower crescent is part of the original eye design.
    points=[]
    for i in range(30):
        a=math.radians(228+92*i/29)
        x=cx+.283*math.cos(a);z=EYE_Z+.283*math.sin(a)
        points.append((x,eye_y(x,z,cx)-.019,z))
    curve('Eye '+label+' • honey crescent',points,.020,iris_light)
    dx=-.207 if label=='L' else .205
    for idx,(ox,oz,sz) in enumerate([(dx,.124,.065),(.205,-.135,.024)]):
        x=cx+ox;z=EYE_Z+oz
        ellipsoid('Eye '+label+' • catchlight '+str(idx+1),(x,eye_y(x,z,cx)-.034,z),(sz,.014,sz*1.15),sparkle,40,24)

# Face edges are embedded into the skin; shallow relief provides volume.
# Dense samples are projected after interpolation to avoid floating Beziers.
def face_line(name,xzs,radius=.012,offset=.004,cyclic=False):
    source=[Vector((x,z,0)) for x,z in xzs]
    samples=[]
    segments=len(source) if cyclic else len(source)-1
    for i in range(segments):
        def point(j):
            return source[j%len(source)] if cyclic else source[max(0,min(len(source)-1,j))]
        p0,p1,p2,p3=[point(j) for j in (i-1,i,i+1,i+2)]
        for k in range(16):
            t=k/16
            v=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
            samples.append((v.x,front_surface(v.x,v.y,offset),v.y))
    if not cyclic:
        x,z=xzs[-1];samples.append((x,front_surface(x,z,offset),z))
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D'
    data.bevel_depth=radius;data.bevel_resolution=4;data.use_fill_caps=True
    spline=data.splines.new('POLY');spline.points.add(len(samples)-1)
    for p,co in zip(spline.points,samples):p.co=(*co,1)
    spline.use_cyclic_u=cyclic
    obj=bpy.data.objects.new(name,data);model.objects.link(obj);data.materials.append(dark)
    return obj

nose_outline=[(-.14,2.565),(-.02,2.591),(.14,2.565),(.106,2.515),(0,2.492),(-.097,2.515)]
patch('Face • little charcoal nose',nose_outline,lambda x,z:front_surface(x,z,-.001),nose_mat,.026,14)
tongue_outline=[(-.122,2.356),(0,2.374),(.124,2.356),(.062,2.219),(0,2.151),(-.067,2.226)]
patch('Face • pink tongue',tongue_outline,lambda x,z:front_surface(x,z,.0005),tongue_mat,.007,14)
face_line('Face • pink tongue • perimeter',tongue_outline,.012,.004,True)
for name,xzs in [('philtrum',[(0,2.516),(0,2.447)]),
                 ('smile L',[(0,2.443),(-.065,2.371),(-.165,2.343),(-.245,2.354)]),
                 ('smile R',[(0,2.443),(.065,2.371),(.165,2.343),(.245,2.354)])]:
    face_line('Face • '+name,xzs)

# Lift the unchanged head/face as a unit above the taller body.
# Geometry and relative placement of all approved facial objects stay intact.
HEAD_LIFT = 1.405*.15
for obj in list(model.objects):
    if obj.name.startswith(('Head ', 'Eye ', 'Ear ', 'Face ')):
        obj.location.z += HEAD_LIFT

# One unclothed skin volume with a short inset neck and a painted belly oval.
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bare_body import build_body
body_revision=build_body(mesh=mesh,curve=curve,ellipsoid=ellipsoid,patch=patch,
                         ring_mesh=ring_mesh,interpolate=interpolate,
                         front_surface=front_surface,fur=fur,material=material,out=TEXTURES)

# A single continuous gray curled tail. It joins the lower back under the skin.
tail_points=[(-.10,.28,.555),(-.36,.65,.575),(-.79,1.03,.661),
             (-1.18,1.27,.862),(-1.36,1.45,1.17),(-1.30,1.53,1.34),
             (-1.12,1.60,1.355),(-1.02,1.63,1.20)]
tail_points=[(x*1.08,y*1.06,z*1.15) for x,y,z in tail_points]
curve('Tail • continuous upright curl',tail_points,.140,fur)
ellipsoid('Tail • rounded tip',tail_points[-1],(.140,.140,.140),fur,48,32)

# Model root: select this object to move or resize the entire character.
root=bpy.data.objects.new('CATGRAY_IP • Model root',None)
model.objects.link(root)
root.empty_display_type='PLAIN_AXES'
root.empty_display_size=.30
for obj in list(model.objects):
    if obj!=root: obj.parent=root
root['reference']='正视.png / 侧视.png / 背视.png'
root['style']='Gray tabby, circular amber eyes, unclothed short body, white oval belly, curled tail'
root['revision']='v5: reference ear outline and colors, smaller inner ears, relaxed arms; v4 proportions'
root['scale_note']='Reference proportions; no real-world dimension supplied. Z-up, front -Y.'
root['production_note']='Static character; separate editable meshes, no rig or animation.'

# Original reference images are packed into the .blend and disabled in renders.
for filename,loc,rot in [('正视.png',(0,2.8,2.23),(math.pi/2,0,0)),
                         ('侧视.png',(-3,0,2.23),(math.pi/2,0,math.pi/2)),
                         ('背视.png',(0,-2.8,2.23),(math.pi/2,0,math.pi))]:
    img=bpy.data.images.load(str(REF/filename),check_existing=True);img.pack()
    obj=bpy.data.objects.new('Reference • '+filename,None);references.objects.link(obj)
    obj.empty_display_type='IMAGE';obj.data=img
    obj.empty_display_size=5.20;obj.color[3]=.45
    obj.location=loc;obj.rotation_euler=rot
    obj.hide_render=True;obj.hide_set(True)

scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24 if QUICK else 96
scene.cycles.use_denoising=True
scene.cycles.device='CPU'
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    for backend in ('METAL','OPTIX','CUDA'):
        try:
            prefs.compute_device_type=backend;prefs.get_devices()
            devices=[d for d in prefs.devices if d.type==backend]
            if devices:
                for d in prefs.devices:d.use=d in devices
                scene.cycles.device='GPU'
                print('RENDER_DEVICE',backend,[d.name for d in devices],flush=True)
                break
        except Exception:
            continue
except Exception:
    pass
scene.cycles.max_bounces=6
scene.world.color=(.45,.45,.45)
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.72,.76,.80,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
scene.view_settings.view_transform='Standard'
scene.view_settings.look='None'
scene.view_settings.exposure=0
scene.view_settings.gamma=1
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=False
scene.render.resolution_percentage=100

floor_mat=material('Studio | warm neutral backdrop','E7E5E1',.95)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003))
floor=move_to(bpy.context.object,studio);floor.name='Studio floor';floor.data.materials.append(floor_mat)

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def area(name,loc,power,size,color,target=(0,0,2.2)):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    obj=bpy.data.objects.new(name,data);studio.objects.link(obj);obj.location=loc;aim(obj,target)
    return obj

area('Large softbox • front left',(-4,-6,8),380,5.0,(1,.98,.96))
area('Fill • front right',(4,-4,5),260,4.0,(.96,.98,1))
area('Back softbox',(2,5,7),400,4.0,(1,1,1))

def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=scale
    obj=bpy.data.objects.new(name,data);studio.objects.link(obj);obj.location=loc;aim(obj,target)
    return obj

cams={
    'front':camera('Camera • Front',(0,-12,2.33),(0,0,2.33),5.40),
    'side':camera('Camera • Side',(12,0,2.33),(0,0,2.33),5.40),
    'back':camera('Camera • Back',(0,12,2.33),(0,0,2.33),5.40),
    'hero':camera('Camera • Three quarter',(7,-12,6.25),(0,0,2.34),5.82),
    'body':camera('Camera • Body detail',(2.6,-8,2.7),(0,0,1.06),2.55),
    'face_side':camera('Camera • Face contact detail',(8,-7,3.15+HEAD_LIFT),(0,-1.51,2.39+HEAD_LIFT),.70),
    'ear':camera('Camera • Soft ear detail',(6,-8,6),(1.51,.24,3.94+HEAD_LIFT),1.52),
    'ear_edge':camera('Camera • Ear thickness detail',(8.04,4.98,6.30),(1.54,.30,4.22),1.52),
    'rear_quarter':camera('Camera • Rear quarter',(7,12,5.95),(0,0,2.34),5.82),
}
scene.camera=cams['hero']
scene.render.resolution_x=1200;scene.render.resolution_y=1200
# Open the native file in a helpful three-quarter material viewport.
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_distance=8
            a.spaces.active.region_3d.view_location=(0,0,2.2)
            a.spaces.active.region_3d.view_rotation=cams['hero'].rotation_euler.to_quaternion()
            a.spaces.active.shading.type='MATERIAL'
            a.spaces.active.overlay.show_extras=False
            a.spaces.active.overlay.show_floor=False
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CatGray_Base.blend'))

# GLB includes only the character. Curves are converted in a temporary export copy.
export_coll=bpy.data.collections.new('EXPORT • temporary evaluated meshes')
scene.collection.children.link(export_coll)
deps=bpy.context.evaluated_depsgraph_get()
export_objects=[]
for obj in list(model.objects):
    if obj.type not in {'MESH','CURVE'}: continue
    data=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps)
    clone=bpy.data.objects.new(obj.name,data);export_coll.objects.link(clone)
    clone.matrix_world=obj.matrix_world.copy()
    export_objects.append(clone)
bpy.ops.object.select_all(action='DESELECT')
for obj in export_objects:obj.select_set(True)
bpy.context.view_layer.objects.active=export_objects[0]
stats={'objects':len(export_objects),'vertices':sum(len(o.data.vertices) for o in export_objects),
       'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in export_objects),
       'materials':sorted({m.name for o in export_objects for m in o.data.materials if m}),
       'dimensions_blender_units':[round(v,4) for v in (
          max(v.co.x for o in export_objects for v in o.data.vertices)-min(v.co.x for o in export_objects for v in o.data.vertices),
          max(v.co.y for o in export_objects for v in o.data.vertices)-min(v.co.y for o in export_objects for v in o.data.vertices),
          max(v.co.z for o in export_objects for v in o.data.vertices)-min(v.co.z for o in export_objects for v in o.data.vertices))]}
# World-space bounds include objects with applied local translations, such as paws.
coords=[o.matrix_world@Vector(v) for o in export_objects for v in o.bound_box]
stats['body_revision']=body_revision
stats['ear_revision']=ear_revision
stats['head_revision']={'geometry':'Preserved v3 head and face','translation_z':HEAD_LIFT}
stats['world_bounds']={'min':[min(v[i] for v in coords) for i in range(3)],'max':[max(v[i] for v in coords) for i in range(3)]}
stats['dimensions_blender_units']=[round(stats['world_bounds']['max'][i]-stats['world_bounds']['min'][i],4) for i in range(3)]
(OUT/'base_info.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
for obj in export_objects:bpy.data.objects.remove(obj,do_unlink=True)
bpy.data.collections.remove(export_coll)

for name in (() if BUILD_ONLY else ('front','side','back','hero','body','face_side','rear_quarter','ear','ear_edge')):
    scene.camera=cams[name]
    scene.render.resolution_x=800 if QUICK else 1200
    scene.render.resolution_y=800 if QUICK else 1200
    scene.render.filepath=str(PREVIEWS/('preview_'+name+'.png'))
    print('RENDER_VIEW',name,flush=True)
    bpy.ops.render.render(write_still=True)
scene.camera=cams['hero']
scene.render.filepath=str(PREVIEWS/'preview_hero.png')
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CatGray_Base.blend'))
print('CATGRAY_COMPLETE',json.dumps(stats),flush=True)
