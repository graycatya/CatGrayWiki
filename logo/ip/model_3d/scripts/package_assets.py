"""Normalize packed image paths and mark the approved Blender file as final."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=[]
for path in [ROOT/'source/CatGray_Base.blend',ROOT/'CatGray_IP.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    packed=[]
    for image in bpy.data.images:
        if image.source!='FILE':continue
        name=Path(bpy.path.abspath(image.filepath)).name
        candidates=[ROOT/'textures'/name,ROOT.parent/'references'/name]
        found=next((p for p in candidates if p.exists()),None)
        if found:
            if not image.packed_file:image.pack()
            image.filepath=bpy.path.relpath(str(found),start=str(path.parent))
        assert image.packed_file, f'Unpacked image: {image.name} ({image.filepath})'
        packed.append({'image':image.name,'path':image.filepath,'packed':True})
    if path.name=='CatGray_IP.blend':
        rig=bpy.data.objects['CATGRAY_RIG'];rig['release_status']='v10 final • approved 2026-09-15'
        bpy.context.scene['release_version']='v10'
        helpers=rig.data.collections.get('腿部变形 • IK driven')
        if helpers:helpers.name='辅助 • Arm sections / Leg IK'
        text=bpy.data.texts.get('使用说明 • 骨骼与动画')
        if text and 'docs/WORKFLOW.md' not in text.as_string():text.write('\n\nv10 已定版。环境与脚本：docs/WORKFLOW.md；统一入口：manage.py。\n')
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    report.append({'file':str(path.relative_to(ROOT)),'images':packed})
(ROOT/'qa/package_verification.json').write_text(json.dumps({'passed':True,'version':'v10','files':report},ensure_ascii=False,indent=2))
print('PACKAGE_VERIFIED',json.dumps(report,ensure_ascii=False))
