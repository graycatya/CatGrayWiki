# SPDX-License-Identifier: Apache-2.0
"""Two-stage, vector-only Blender desktop-pet exporter.

1. blender -b -t 4 --python this.py -- --blend SOURCE --stage STAGE
2. python this.py --stage STAGE --output OUTPUT (numpy, shapely)

Uses source project pose helpers, never saves the blend. Intermediate face
coordinates come directly from evaluated meshes, not rendered pixels.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

W, H, FPS = 768, 832, 24
HELPERS = ('export_desktop_pet.py', 'desktop_pet_actions.py', 'desktop_pet_speech.py',
           'rig_voxel.py', 'facial_voxel.py', 'voxel_model.py')

def helper_hashes(root):
    return {name: hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()
            for name in HELPERS}

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'))+'\n')

def transform():
    return {'o':{'a':0,'k':100},'r':{'a':0,'k':0},'p':{'a':0,'k':[0,0,0]},'a':{'a':0,'k':[0,0,0]},'s':{'a':0,'k':[100,100,100]}}

def sample_blend(args):
    import bpy
    import numpy as np
    root=args.blend.resolve().parent.parent
    sys.path.insert(0,str(root/'scripts'))
    from export_desktop_pet import PLAN, pose
    from rig_voxel import RIG
    bpy.ops.wm.open_mainfile(filepath=str(args.blend.resolve()))
    scene=bpy.context.scene
    rig=bpy.data.objects[RIG]
    camera=scene.camera
    assert camera and camera.data.type=='ORTHO'
    scene.render.resolution_x=W;scene.render.resolution_y=H
    scene.render.resolution_percentage=100
    frame=camera.data.view_frame(scene=scene)
    left,right=min(v.x for v in frame),max(v.x for v in frame)
    bottom,top=min(v.y for v in frame),max(v.y for v in frame)
    camera_inverse=camera.matrix_world.inverted()
    light=np.array([-.35,-.8,1.]);light/=np.linalg.norm(light)
    args.stage.mkdir(parents=True,exist_ok=True)
    metadata={'source':str(args.blend.resolve()),'sourceSHA256':hashlib.sha256(args.blend.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'size':[W,H],'fps':FPS,'actions':[],'camera':camera.name,'method':'evaluated Blender mesh planes, orthographic projection, exact affine-depth occlusion; no raster tracing'}
    metadata['poseHelpersSHA256']=helper_hashes(root)
    for name,duration,action,loop in PLAN:
        if args.action and name!=args.action: continue
        count=round(duration*FPS)
        metadata['actions'].append({'name':name,'frames':count,'loop':loop})
        with gzip.open(args.stage/(name+'.jsonl.gz'),'wt') as output:
            for f in range(count if not args.smoke else 1):
                pose(rig,name,f/FPS,duration,action)
                bpy.context.view_layer.update()
                dg=bpy.context.evaluated_depsgraph_get();faces=[]
                for obj in scene.objects:
                    if obj.type!='MESH' or obj.hide_render or obj.name=='Studio floor': continue
                    evaluated=obj.evaluated_get(dg);mesh=evaluated.to_mesh()
                    world=obj.matrix_world
                    matrix=np.array(camera_inverse@world)
                    xyz=np.empty(len(mesh.vertices)*3,dtype=np.float64)
                    mesh.vertices.foreach_get('co',xyz)
                    xyz=xyz.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
                    xy=np.column_stack(((xyz[:,0]-left)*W/(right-left),(top-xyz[:,1])*H/(top-bottom)))
                    normal_matrix=world.to_3x3().inverted().transposed()
                    camera_rotation=camera_inverse.to_3x3()
                    colors={}
                    active_vertices=None
                    keys=obj.data.shape_keys
                    if obj.name=='Voxel_Face' and keys:
                        basis=np.empty(len(mesh.vertices)*3)
                        keys.key_blocks[0].data.foreach_get('co',basis)
                        basis=basis.reshape(-1,3)
                        active_vertices=np.zeros(len(mesh.vertices),dtype=bool)
                        for key in keys.key_blocks[1:]:
                            if key.value>.5:
                                coords=np.empty(len(mesh.vertices)*3)
                                key.data.foreach_get('co',coords)
                                active_vertices |= np.linalg.norm(coords.reshape(-1,3)-basis,axis=1)>.1
                    for polygon in mesh.polygons:
                        if active_vertices is not None and not all(active_vertices[v] for v in polygon.vertices):
                            continue
                        nworld=normal_matrix@polygon.normal
                        nworld.normalize();n=camera_rotation@nworld
                        if n.z<=1e-7: continue
                        ids=list(polygon.vertices); points=xy[ids]
                        if len(points)<3 or polygon.area<1e-10: continue
                        slot=polygon.material_index
                        if slot not in colors:
                            mat=mesh.materials[slot] if slot<len(mesh.materials) else None
                            color=mat.diffuse_color[:3] if mat else (.5,.5,.5)
                            if mat and mat.use_nodes:
                                node=mat.node_tree.nodes.get('Principled BSDF')
                                if node:color=node.inputs['Base Color'].default_value[:3]
                            colors[slot]=np.array([12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055 for c in color])
                        shade=.74+.26*max(0,float(np.dot(nworld,light)))
                        rgb=np.round(colors[slot]*shade,5).tolist()
                        # Camera-space Z is affine over the projected plane.
                        dx=-n.x*(right-left)/W/n.z
                        dy=n.y*(top-bottom)/H/n.z
                        point=xyz[ids[0]]
                        dc=float(np.dot(n,point))/n.z-n.x*left/n.z-n.y*top/n.z
                        faces.append([rgb,[round(dx,10),round(dy,10),round(dc,10)],np.round(points,6).tolist()])
                    evaluated.to_mesh_clear()
                output.write(json.dumps(faces,separators=(',',':'))+'\n')
                if f%24==0:print('SAMPLE',name,f,'/',count,'faces',len(faces),flush=True)
        print('SAMPLED',name,flush=True)
    write_json(args.stage/'source.json',metadata)
    if not args.smoke:
        pose(rig,'idle',0,4,None)
        scene.render.engine='CYCLES';scene.cycles.device='CPU'
        scene.cycles.samples=16;scene.cycles.use_denoising=True
        scene.render.film_transparent=True
        scene.render.image_settings.file_format='PNG'
        scene.render.image_settings.color_mode='RGBA'
        floor=bpy.data.objects.get('Studio floor')
        if floor:floor.hide_render=True
        scene.render.filepath=str(args.stage/'fallback.png')
        bpy.ops.render.render(write_still=True)

def half_plane(delta,bounds):
    import numpy as np
    from shapely.geometry import Polygon
    x0,y0,x1,y1=bounds
    corners=[(x0-1,y0-1),(x1+1,y0-1),(x1+1,y1+1),(x0-1,y1+1)]
    points=[]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        da,db=np.dot(delta,[*a,1]),np.dot(delta,[*b,1])
        if da>=0:points.append(a)
        if (da>=0)!=(db>=0):
            f=da/(da-db);points.append((a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1])))
    return Polygon(points) if len(points)>=3 else Polygon()

def visible_shapes(faces):
    import numpy as np
    import shapely
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    grouped={}
    for color,plane,points in faces:
        polygon=shapely.set_precision(shapely.make_valid(Polygon(points)),.001)
        if polygon.area>1e-6:
            grouped.setdefault((tuple(color),tuple(round(v,6) for v in plane)),[]).append(polygon)
    polygons=[];planes=[];colors=[]
    for (color,plane),parts in grouped.items():
        merged=unary_union(parts).simplify(.001,preserve_topology=True)
        for piece in shapely.get_parts(merged):
            if piece.geom_type=='Polygon' and piece.area>1e-5:
                polygons.append(piece);planes.append(plane);colors.append(color)
    polygons=np.array(polygons,dtype=object);planes=np.array(planes)
    pairs=shapely.STRtree(polygons).query(polygons,predicate='intersects')
    pairs=pairs[:,pairs[0]<pairs[1]]
    delta=planes[pairs[0]]-planes[pairs[1]]
    # Blender single-precision normals introduce tiny differences between
    # physically coplanar voxel faces. Ignore sub-0.001 world-unit depth noise.
    distinct=(np.abs(delta)@np.array([W,H,1.]))>.001
    pairs=pairs[:,distinct]
    overlaps=shapely.intersection(polygons[pairs[0]],polygons[pairs[1]])
    cuts={}
    for (a,b),overlap in zip(pairs.T,overlaps):
        if overlap.area<1e-6:continue
        delta=planes[a]-planes[b]
        coords=shapely.get_coordinates(overlap);depth=coords@delta[:2]+delta[2]
        lo,hi=depth.min(),depth.max()
        if max(abs(lo),abs(hi))<.001:continue
        if lo>=-1e-8:cuts.setdefault(b,[]).append(overlap)
        elif hi<=1e-8:cuts.setdefault(a,[]).append(overlap)
        else:
            front=overlap.intersection(half_plane(delta,overlap.bounds))
            cuts.setdefault(b,[]).append(front);cuts.setdefault(a,[]).append(overlap.difference(front))
    visible={}
    for i,p in enumerate(polygons):
        result=p.difference(unary_union(cuts[i])) if i in cuts else p
        if not result.is_empty:visible.setdefault(colors[i],[]).append(result)
    groups=[];bounds=[]
    for color,parts in visible.items():
        merged=unary_union(parts).simplify(.0001,preserve_topology=True)
        paths=[]
        for piece in shapely.get_parts(merged):
            if piece.geom_type!='Polygon' or piece.area<.002:continue
            bounds.append(piece.bounds)
            piece=shapely.geometry.polygon.orient(piece,sign=-1)
            for ring in [piece.exterior,*piece.interiors]:
                vertices=np.round(np.asarray(ring.coords)[:-1],4).tolist()
                paths.append({'ty':'sh','ks':{'a':0,'k':{'i':[[0,0]]*len(vertices),'o':[[0,0]]*len(vertices),'v':vertices,'c':True}}})
        if paths:groups.append({'ty':'gr','it':paths+[{'ty':'fl','c':{'a':0,'k':list(color)},'o':{'a':0,'k':100},'r':1},{'ty':'tr',**transform()}]})
    assert bounds,'Empty frame'
    assert min(b[0] for b in bounds)>0 and min(b[1] for b in bounds)>0
    assert max(b[2] for b in bounds)<W and max(b[3] for b in bounds)<H,'Clipped frame'
    return groups

def convert_line(line):
    return visible_shapes(json.loads(line))

def convert(args):
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    import shutil
    metadata=json.loads((args.stage/'source.json').read_text())
    args.output.mkdir(parents=True,exist_ok=True)
    actions={};report={**metadata,'source':'desktop_pet/CatGray_DesktopPet.blend','actions':{}}
    report['generatorSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['poseHelpersSHA256']=metadata.get('poseHelpersSHA256') or helper_hashes(Path(metadata['source']).parent.parent)
    previous=json.loads((args.output/'generation.json').read_text()) if (args.output/'generation.json').exists() else {}
    for info in metadata['actions']:
        name=info['name']
        if args.action and name!=args.action:continue
        path=args.output/(name+'.json')
        old=previous.get('actions',{}).get(name,{})
        if (previous.get('sourceSHA256')==metadata['sourceSHA256'] and
                previous.get('generatorSHA256')==report['generatorSHA256'] and
                previous.get('poseHelpersSHA256')==report['poseHelpersSHA256'] and
                old.get('frames')==info['frames'] and path.exists() and
                hashlib.sha256(path.read_bytes()).hexdigest()==old.get('sha256')):
            actions[name]={'loops':-1 if info['loop'] else 1,'right':{'source':path.name}}
            report['actions'][name]=old
            print('REUSED',name,flush=True)
            continue
        layers=[];assets=[];cache={} 
        with gzip.open(args.stage/(name+'.jsonl.gz'),'rt') as source, ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for f,shapes in enumerate(pool.map(convert_line,source,buffersize=24)):
                digest=hashlib.sha256(json.dumps(shapes,separators=(',',':')).encode()).hexdigest()
                if digest not in cache:
                    ref=f'{name}_{len(cache)}';cache[digest]=ref
                    assets.append({'id':ref,'w':W,'h':H,'layers':[{'ddd':0,'ind':1,'ty':4,'nm':ref,'sr':1,'ks':transform(),'ao':0,'ip':0,'op':info['frames'],'st':0,'bm':0,'shapes':shapes}]})
                layers.append({'ddd':0,'ind':f+1,'ty':0,'nm':f'{name} {f}','refId':cache[digest],'w':W,'h':H,'sr':1,'ks':transform(),'ao':0,'ip':f,'op':f+1,'st':0,'bm':0})
                if f%24==0:print('VECTOR',name,f,'/',info['frames'],flush=True)
        count=len(layers)
        animation={'v':'5.12.2','fr':FPS,'ip':0,'op':count,'w':W,'h':H,'nm':'CatGray '+name,'ddd':0,'assets':assets,'layers':layers}
        path=args.output/(name+'.json');write_json(path,animation)
        assert path.stat().st_size<64*1024*1024
        actions[name]={'loops':-1 if info['loop'] else 1,'right':{'source':path.name}}
        report['actions'][name]={'frames':count,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'uniqueFrames':len(assets)}
        print('EXPORTED',name,path.stat().st_size,flush=True)
    package={'schemaVersion':1,'id':'catgray-desktop-pet-lottie','name':'CatGray Voxel Lottie','renderer':'lottie','logicalSize':[192,208],'footAnchor':[96,191.36],'bubbleAnchor':[96,12],'defaultAction':'idle','defaultFacing':'right','allowMirror':True,'fallbackImage':'fallback.png','regions':[{'id':'body','shape':'ellipse','rect':[40,12,120,184],'clickable':True,'draggable':True}],'actions':actions}
    write_json(args.output/'mascot.json',package);write_json(args.output/'generation.json',report)
    root=Path(metadata['source']).parent
    shutil.copyfile(root/'LICENSE.txt',args.output/'LICENSE.txt')
    # Fallback is explicitly a separate image, never embedded in vector JSON.
    shutil.copyfile(args.stage/'fallback.png',args.output/'fallback.png')
    shutil.copyfile(Path(__file__),args.output/Path(__file__).name)
    (args.output/'README.md').write_text('# CatGray Blender 矢量 Lottie\n\n直接读取 desktop_pet/CatGray_DesktopPet.blend 的求值网格和动作，使用原正交相机投影，按面的仿射深度进行遮挡裁剪。不是精灵描摹。768×832 坐标画布，24 FPS，纯矢量面与固定方向光照；无纹理、嵌入位图或外链。体素轮廓本身保留棱角；材质和光照为矢量平面着色，与 Cycles 的阴影存在差异。\n\n完整十动作包入口为 mascot.json；generation.json 记录 blend 和动作文件校验和。fallback.png 仅用于渲染不可用时。角色授权见 LICENSE.txt。生成器用法见脚本头部，第一阶段需要原项目 scripts 下的姿态辅助脚本，第二阶段需要 numpy、shapely。\n')

if __name__=='__main__':
    argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    p=argparse.ArgumentParser();p.add_argument('--blend',type=Path);p.add_argument('--stage',required=True,type=Path);p.add_argument('--output',type=Path);p.add_argument('--workers',type=int,default=min(12,os.cpu_count() or 1));p.add_argument('--action');p.add_argument('--smoke',action='store_true');a=p.parse_args(argv)
    if a.workers<1:p.error('--workers must be positive')
    if not a.blend and not a.output:p.error('--output is required for conversion')
    if a.blend:sample_blend(a)
    else:convert(a)
