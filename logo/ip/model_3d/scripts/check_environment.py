"""Check the actual Blender Python runtime, not the system interpreter."""
import bpy,bmesh,mathutils,numpy,sys,platform,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assert bpy.app.version>=(5,2,0),f'Use the validated Blender 5.2.1 runtime; found {bpy.app.version_string}'
probe=bpy.data.actions.new('Environment API probe')
assert hasattr(probe,'slots'), 'Action slot API unavailable'
bpy.data.actions.remove(probe)
bpy.ops.export_scene.gltf.get_rna_type();bpy.ops.import_scene.gltf.get_rna_type()
for f in ['source/CatGray_Base.blend','source/base_info.json','textures/CatGray_Fur_BaseColor.png','textures/CatGray_BareBody_BaseColor.png']:
    assert (root/f).exists(),f'Missing asset: {f}'
for f in ['正视.png','侧视.png','背视.png']:assert (root.parent/'references'/f).exists(),f
r={'passed':True,'blender':bpy.app.version_string,'python':sys.version.split()[0],'numpy':numpy.__version__,'platform':platform.platform(),'validated_blender':'5.2.1','version_matches':bpy.app.version[:3]==(5,2,1)}
print('ENVIRONMENT_OK',json.dumps(r,ensure_ascii=False))
(root/'qa/environment_verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
if not r['version_matches']:print('NOTE: This Blender version has not been validated for the release; run verify after rebuilding.')
