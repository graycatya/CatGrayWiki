"""Continuous garment construction and sculpted legs for the CatGray mascot.

The face is deliberately left in build_cat.py. This module only builds the body.
"""
import bpy
import bmesh
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def build_body(*, mesh, curve, ellipsoid, patch, ring_mesh, interpolate,
               front_surface, fur, cloth, white, material):
    tau=math.tau
    seams=material('Hoodie | recessed seam shade','3F3D3D',.9)
    rib=material('Hoodie | soft rib knit','514F4F',.93)
    rolled=material('Hoodie | rounded folded edge','5A5858',.88)
    thread=material('Hoodie | quiet topstitch','696565',.9)

    def apply_modifier(obj, modifier):
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    def union(name,parts,voxel=.010,smooth=6):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in parts:
            obj.select_set(True)
            bpy.context.view_layer.objects.active=obj
            for mod in list(obj.modifiers): apply_modifier(obj,mod)
        bpy.context.view_layer.objects.active=parts[0]
        bpy.ops.object.join()
        obj=bpy.context.object
        obj.name=name
        # Weld the longitudinal seams on the lofts before making one volume.
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0003)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        obj.data.remesh_voxel_size=voxel
        bpy.ops.object.voxel_remesh()
        mod=obj.modifiers.new('Relax sculpted junctions','SMOOTH')
        mod.factor=.70;mod.iterations=smooth
        apply_modifier(obj,mod)
        for p in obj.data.polygons:p.use_smooth=True
        mod=obj.modifiers.new('Finish smooth silhouette','SUBSURF')
        mod.levels=1;mod.render_levels=1
        return obj

    def loft(name,table,mat,sign=1,sub=1,sections=58,around=72):
        # z, center X, center Y, X radius, Y radius. Smooth silhouette in both views.
        vertices=[];faces=[]
        for j in range(sections+1):
            z=table[0][0]+(table[-1][0]-table[0][0])*j/sections
            cx,cy,rx,ry=[interpolate(table,z,c) for c in range(1,5)]
            for i in range(around):
                a=tau*i/around
                vertices.append((sign*(cx+rx*math.cos(a)),cy+ry*math.sin(a),z))
        for j in range(sections):
            for i in range(around):
                k=j*around+i;kn=j*around+(i+1)%around
                faces.append((k,kn,kn+around,k+around))
        faces.append(tuple(reversed(range(around))))
        faces.append(tuple(sections*around+i for i in range(around)))
        obj=mesh(name,vertices,faces,mat,sub=sub)
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free()
        return obj

    torso_table=[(.448,.545,-.43,.46),(.475,.615,-.505,.525),
                 (.565,.654,-.548,.572),(.775,.665,-.567,.600),
                 (1.010,.607,-.522,.575),(1.185,.520,-.427,.470),
                 (1.335,.392,-.326,.364),(1.475,.270,-.254,.282),
                 (1.550,.165,-.168,.183)]
    torso=ring_mesh('Hoodie • torso before tailoring',torso_table,cloth,power=2.35,nz=78,nt=112)
    sleeves=[]
    sleeve_table=[(.515,.753,-.015,.125,.191),(.545,.752,-.015,.151,.210),
                  (.665,.739,-.007,.170,.226),(.830,.692,.008,.191,.240),
                  (1.020,.595,.018,.211,.252),(1.180,.481,.025,.207,.243),
                  (1.295,.390,.022,.135,.183),(1.335,.367,.023,.032,.050)]
    for sign,label in ((-1,'L'),(1,'R')):
        sleeves.append(loft('Sleeve '+label+' • shoulder volume',sleeve_table,cloth,sign,sub=1))
    garment=union('Hoodie • continuous torso and sleeves',[torso,*sleeves],.0115,8)

    # Tiny broad creases at the waist and under the arm, rather than a rigid tube.
    for v in garment.data.vertices:
        x,y,z=v.co;ax=abs(x)
        if y<-.18 and .53<z<.94 and .35<ax<.72:
            envelope=math.exp(-((ax-.55)/.125)**2)
            fold=.010*math.exp(-((z-(.626+.38*(ax-.45)))/.031)**2)
            fold-=.005*math.exp(-((z-(.675+.38*(ax-.45)))/.040)**2)
            v.co.y-=envelope*fold
    bpy.context.view_layer.update()
    tree=BVHTree.FromObject(garment,bpy.context.evaluated_depsgraph_get())

    def surface(x,z,offset=.012,back=False):
        start=Vector((x,2 if back else -2,z))
        direction=Vector((0,-1 if back else 1,0))
        hit,normal,index,distance=tree.ray_cast(start,direction,4)
        if hit is not None:return hit.y+(offset if back else -offset)
        y=front_surface(x,z,offset,torso_table,2.35)
        return -y if back else y

    # One pelvis and two complete leg/foot lofts. No separate ellipsoid shoes.
    leg_table=[(.000,.255,-.080,.145,.171),(.018,.255,-.080,.200,.226),
               (.065,.255,-.086,.225,.255),(.128,.255,-.068,.218,.243),
               (.212,.256,-.008,.196,.209),(.330,.255,.034,.213,.243),
               (.455,.239,.038,.266,.293),(.565,.220,.034,.273,.303),
               (.605,.220,.034,.242,.270)]
    leg_parts=[loft('Leg '+label+' • complete paw silhouette',leg_table,fur,sign,sub=1)
               for sign,label in ((-1,'L'),(1,'R'))]
    leg_parts.append(ellipsoid('Body • concealed pelvis',(0,.045,.485),(.485,.285,.160),fur))
    legs=union('Body • connected pelvis legs and paws',leg_parts,.0095,9)
    bottom=min(v.co.z for v in legs.data.vertices)
    for v in legs.data.vertices:
        v.co.z-=bottom
        # A soft but truly grounded sole, still tangent to the rounded toes.
        if v.co.z<.014:v.co.z=0

    for sign,label in ((-1,'L'),(1,'R')):
        # Sleeve bands have fabric thickness; a single quiet seam defines the hem.
        cuff_table=[(.513,.752,-.015,.139,.203),(.521,.752,-.015,.153,.216),
                    (.565,.752,-.015,.157,.219),(.587,.750,-.014,.154,.214),
                    (.595,.748,-.013,.145,.205)]
        loft('Cuff '+label+' • rounded rib band',cuff_table,rib,sign,sub=1,sections=18,around=64)
        cuff_line=[(sign*(.752+.151*math.cos(tau*i/64)),
                    -.015+.216*math.sin(tau*i/64),.530) for i in range(64)]
        curve('Cuff '+label+' • inset hem stitch',cuff_line,.0045,seams,True)
        hand_table=[(.386,.750,-.020,.007,.013),(.407,.750,-.020,.075,.112),
                    (.455,.752,-.020,.120,.168),(.518,.752,-.017,.129,.180),
                    (.564,.750,-.014,.116,.166),(.609,.748,-.008,.087,.138)]
        loft('Hand '+label+' • relaxed mitten',hand_table,fur,sign,sub=1,sections=35,around=64)

    # A single annular hood: its neckline runs into the head, the front forms a
    # low V, and the back hangs against the shoulders as one continuous cloth.
    n=160;steps=26
    vertices=[];faces=[];outer=[];inner=[]
    for j in range(steps+1):
        t=j/steps
        for i in range(n):
            a=tau*i/n;s=math.sin(a);c=math.cos(a)
            xi=.305*s
            if c>=0:
                yi=-.535*c
                zi=1.245+.225*abs(s)**1.25
                xo=.648*s
                zo=1.170+.065*abs(s)**1.10
                yo=-.600*c
            else:
                yi=-.307*c;zi=1.470
                xo=.637*s
                zo=1.018+.217*abs(s)**1.20
                yo=-.655*c
            x=xi+(xo-xi)*t
            z=zi+(zo-zi)*t+.025*math.sin(math.pi*t)
            y=yi+(yo-yi)*t
            if c>=0:
                y-=.035*math.sin(math.pi*t)*c
                if c>.10:y=min(y,surface(x,z,.015))
            else:
                y+=.090*math.sin(math.pi*t)*(-c)
                if c<-.10:y=max(y,surface(x,z,.023,back=True))
            # Fit the entire cloth sheet to the actual sculpted shoulders. The
            # outer sewn hem rests on the garment instead of hovering beyond it.
            p=Vector((x,y,z))
            nearest,normal,index,distance=tree.find_nearest(p)
            if nearest is not None:
                fitted=nearest+normal*(.018+.027*math.sin(math.pi*t))
                p=p.lerp(fitted,.85+.15*t)
            vertices.append(tuple(p))
            if j==0:inner.append(tuple(p))
            if j==steps:outer.append(tuple(p))
    for j in range(steps):
        for i in range(n):
            k=j*n+i;kn=j*n+(i+1)%n
            faces.append((k,k+n,kn+n,kn))
    hood=mesh('Hood • continuous folded cloth',vertices,faces,cloth)
    relax=hood.modifiers.new('Relax cloth along shoulders','SMOOTH')
    relax.factor=.45;relax.iterations=5
    apply_modifier(hood,relax)
    inner=[tuple(v.co) for v in hood.data.vertices[:n]]
    outer=[tuple(v.co) for v in hood.data.vertices[-n:]]
    sub=hood.modifiers.new('Smooth cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=hood.modifiers.new('Soft cloth thickness','SOLIDIFY')
    solid.thickness=.055;solid.offset=-1;solid.use_even_offset=True
    curve('Hood • soft rolled outer hem',outer[::2],.012,rolled,True)
    curve('Hood • fine perimeter seam',[(x,y-.003 if y<0 else y+.003,z+.003) for x,y,z in outer[::2]],.0038,seams,True)
    curve('Hood • neckline fold',inner[::2],.011,rolled,True)

    # The small undershirt wedge sits on the chest inside the V opening.
    patch('Neckline • inset white undershirt',[(-.235,1.385),(.235,1.385),(.073,1.260),(0,1.228),(-.073,1.260)],
          lambda x,z:surface(x,z,.006),white,.003,10)

    # Waistband follows the same garment surface, rather than stacked wire rings.
    ring_verts=[];ring_faces=[];around=144
    for j in range(9):
        t=j/8;z=.467+.077*t
        for i in range(around):
            a=tau*i/around;s=math.sin(a);c=math.cos(a)
            rx=interpolate(torso_table,z,1)
            x=rx*math.copysign(abs(s)**(2/2.35),s)
            fr=interpolate(torso_table,z,2);bk=interpolate(torso_table,z,3)
            y=(fr+bk)*.5-(bk-fr)*.5*math.copysign(abs(c)**(2/2.35),c)
            # The centerline is inset at both edges, with a rounded knit band.
            expansion=.006+.009*math.sin(math.pi*t)
            ring_verts.append((x*(1+expansion),y*(1+expansion),z))
    for j in range(8):
        for i in range(around):
            k=j*around+i;kn=j*around+(i+1)%around
            ring_faces.append((k,kn,kn+around,k+around))
    waist=mesh('Hoodie • soft waistband',ring_verts,ring_faces,rib,sub=1)
    solid=waist.modifiers.new('Knit thickness','SOLIDIFY');solid.thickness=.020;solid.offset=-1

    # A ruled fabric patch avoids the overshoot of skinny closed spline outlines.
    def fabric_grid(name,rows,columns,point,mat,thickness=.009):
        verts=[point(i/columns,j/rows) for j in range(rows+1) for i in range(columns+1)]
        faces=[]
        for j in range(rows):
            for i in range(columns):
                k=j*(columns+1)+i
                faces.append((k,k+1,k+columns+2,k+columns+1))
        obj=mesh(name,verts,faces,mat)
        solid=obj.modifiers.new('Sewn fabric thickness','SOLIDIFY');solid.thickness=thickness;solid.offset=-1
        return obj

    def pocket_top(t):
        a,b,c,d=(.080,.780),(.135,.670),(.280,.625),(.520,.640)
        return tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*d[k] for k in (0,1))

    # Tailored split kangaroo pocket with a clean continuous hand opening.
    for sign,label in ((-1,'L'),(1,'R')):
        def pocket_point(u,v):
            x,top=pocket_top(u);x*=sign
            bottom=.550+.004*math.sin(math.pi*u)
            z=bottom+(top-bottom)*v
            offset=.008+.005*math.sin(math.pi*u)*math.sin(math.pi*v)
            return (x,surface(x,z,offset),z)
        fabric_grid('Pocket '+label+' • sewn fabric panel',24,52,pocket_point,cloth,.009)
        opening=[]
        for i in range(65):
            x,z=pocket_top(i/64);x*=sign
            opening.append((x,surface(x,z,.014),z))
        curve('Pocket '+label+' • hand opening',opening,.0045,seams)
        stitch=[]
        for i in range(45):
            x=sign*(.093+.413*i/44);z=.560
            stitch.append((x,surface(x,z,.014),z))
        curve('Pocket '+label+' • topstitch',stitch,.0020,thread)

    def placket_point(u,v):
        x=-.098+.108*u;z=.543+.663*v
        return (x,surface(x,z,.010+.002*math.sin(math.pi*u)),z)
    fabric_grid('Hoodie • flat zipper placket',64,6,placket_point,cloth,.009)
    zipper=[(-.042,z) for z in (.543,.70,.90,1.08,1.220)]
    curve('Hoodie • centered zipper seam',[(x,surface(x,z,.024),z) for x,z in zipper],.0058,seams)
    ellipsoid('Hoodie • small zipper pull',(-.042,surface(-.042,1.073,.035),1.073),(.015,.009,.027),seams,32,20)
    for x,zend in ((-.165,.866),(.150,.913)):
        points=[]
        for xx,z in [(x,1.228),(x*.94,1.16),(x*1.03,1.03),(x*.95,zend)]:
            points.append((xx,surface(xx,z,.028),z))
        curve('Hoodie • soft drawcord '+str(x),points,.0105,seams)
        xx,yy,zz=points[-1]
        ellipsoid('Hoodie • drawcord tip '+str(x),(xx,yy,zz+.006),(.012,.012,.026),seams,24,16)

    return {'revision':'v2_continuous_body','garment_object':garment.name,
            'legs_object':legs.name,'hood_object':hood.name,
            'notes':'Continuous shoulders and sleeves, draped thick hood, integrated legs and paws.'}
