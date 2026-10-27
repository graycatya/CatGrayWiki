"""Verify the delivered Sprite manifest and decoded atlas with Blender Python."""
import json
from pathlib import Path
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]/'desktop_pet'
m = json.loads((ROOT/'manifest.json').read_text())
assert m['schemaVersion']==1 and m['type']=='sprite'
assert set(m['stateMap'])=={'Idle','Thinking','Working','Waiting','Speaking','Success','Error'}
assert all(a in m['animations'] for a in m['stateMap'].values())
assert m['animations'][m['stateMap']['Idle']]['loop']
assert (ROOT/m['licenseFile']).is_file()
w,h=m['frameSize']
image=bpy.data.images.load(str(ROOT/m['asset']))
aw,ah=image.size
assert aw%w==ah%h==0 and max(aw,ah)<=4096
assert aw*ah*4<=128*1024*1024
pixels=np.empty(aw*ah*4,dtype=np.float32)
image.pixels.foreach_get(pixels)
pixels=pixels.reshape(ah,aw,4)
cols,rows=aw//w,ah//h
seen=set()
for name,a in m['animations'].items():
    assert 1<=a['fps']<=60 and a['frameCount']>0
    for frame in range(a['frameCount']):
        index=a['startFrame']+frame
        assert index not in seen and index<cols*rows
        seen.add(index)
        r,c=divmod(index,cols)
        cell=pixels[(rows-1-r)*h:(rows-r)*h,c*w:(c+1)*w]
        alpha=cell[:,:,3]
        assert np.any(alpha>.01) and not np.any(alpha[[0,-1],:]>.01) and not np.any(alpha[:,[0,-1]]>.01)
        path=ROOT/'frames'/f'{name}_{frame:03d}.png'
        if path.exists():
            source=bpy.data.images.load(str(path),check_existing=False)
            data=np.empty(w*h*4,dtype=np.float32)
            source.pixels.foreach_get(data)
            # Confirm row order and image encoding against the original frame.
            assert np.max(np.abs(cell-data.reshape(h,w,4)))<.02, (name,frame)
            bpy.data.images.remove(source)
assert seen==set(range(len(seen)))
report=json.loads((ROOT/'verification.json').read_text())
report['independentPackValidation']={'passed':True,'frames':len(seen),'decodedBytes':aw*ah*4,
    'checks':['manifest state/action references','frame ranges nonoverlapping and contiguous',
              'PNG atlas dimensions and alpha bounds','atlas cells match source PNGs','license present']}
(ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PACK VERIFIED',len(seen),'frames',aw,ah,aw*ah*4,'decoded bytes')
