"""Audit baked hand/arm clearance against head, torso and keyboard surfaces.

Blender Python; samples every half frame at the 24 FPS authoring rate.
Tests evaluated geometry (not IK endpoints). Attached upper-arm/torso joints
are excluded; head/arm, forearm/torso, and working arm/keyboard are checked.
Tolerance is 0.01 Blender unit (one tenth of a voxel). This scoped regression
check complements front/side visual review; it is not a general physics solver.
"""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desktop_pet_actions as pet
from rig_voxel import RIG

TOLERANCE=.01


def geometry(objects,graph):
    vertices,polygons=[],[]
    for obj in objects:
        evaluated=obj.evaluated_get(graph)
        mesh=evaluated.to_mesh()
        base=len(vertices)
        vertices.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
        polygons.extend(tuple(base+i for i in p.vertices) for p in mesh.polygons)
        evaluated.to_mesh_clear()
    probes=vertices+[sum((vertices[i] for i in p),Vector())/len(p) for p in polygons]
    bounds=[(min(v[i] for v in vertices),max(v[i] for v in vertices)) for i in range(3)]
    return probes,BVHTree.FromPolygons(vertices,polygons),bounds


def penetration(source,target):
    probes=source[0]
    tree,bounds=target[1:]
    maximum=0
    for v in probes:
        if any(v[i]<=bounds[i][0]+TOLERANCE or v[i]>=bounds[i][1]-TOLERANCE for i in range(3)):
            continue
        near,normal,_,distance=tree.find_nearest(v)
        if (v-near).dot(normal)<-TOLERANCE:
            maximum=max(maximum,distance)
    return maximum


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'desktop_pet/CatGray_DesktopPet.blend'))
    rig=bpy.data.objects[RIG]
    scene=bpy.context.scene
    arms=['Voxel_'+part+side for part in ['UpperArm.','Forearm.'] for side in ['L','R']]
    keyboard=list(bpy.data.collections[pet.PROP_COLLECTION].objects)
    report={'passed':True,'tolerance':TOLERANCE,'sampling':'24 FPS, half-frame increments',
            'scope':['upper arms/head','forearms/head','forearms/torso','working arms/keyboard'],
            'exclusions':['attached upper-arm/torso joints','other body part pairs'], 'actions':{}}
    for action,duration in pet.DURATIONS.items():
        pet.activate(rig,'Pet_'+action)
        incidents=[]
        for half in range(duration*48+1):
            frame=1+half/2
            scene.frame_set(int(frame),subframe=frame%1)
            bpy.context.view_layer.update()
            graph=bpy.context.evaluated_depsgraph_get()
            meshes={name:geometry([bpy.data.objects[name]],graph) for name in arms+['Voxel_Head','Voxel_Body']}
            if action=='Working':
                meshes['Keyboard']=geometry(keyboard,graph)
            for name in arms:
                for target in ['Voxel_Head','Voxel_Body']+(['Keyboard'] if action=='Working' else []):
                    if name.startswith('Voxel_UpperArm') and target=='Voxel_Body':
                        continue
                    depth=max(penetration(meshes[name],meshes[target]),penetration(meshes[target],meshes[name]))
                    if depth>TOLERANCE:
                        incidents.append({'frame':frame,'parts':[name,target],'depth':round(depth,6)})
        report['actions'][action]={'samples':duration*48+1,'incidents':incidents}
        if incidents:
            report['passed']=False
        print('CLEARANCE',action,'incidents',len(incidents),flush=True)
    (ROOT/'desktop_pet/clearance_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['passed'], 'Arm penetration found; see clearance_verification.json'
    print('BAKED ARM CLEARANCE VERIFIED')

if __name__=='__main__':
    main()
