"""Encode four state reviews from the current transparent Sprite source frames.
Standard Python + ffmpeg; videos add a light inspection background only.
"""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]/'desktop_pet'
OUT=ROOT/'review'
OUT.mkdir(exist_ok=True)
for name,duration in [('thinking',3),('working',2),('waiting',4),('speaking',3)]:
    subprocess.run(['ffmpeg','-y','-v','error','-threads','2',
        '-f','lavfi','-i',f'color=c=0xe8edf3:s=384x416:r=8:d={duration}',
        '-framerate','8','-i',str(ROOT/'frames'/f'{name}_%03d.png'),
        '-filter_complex_threads','1','-filter_complex',
        '[1:v]scale=384:416:flags=neighbor[pet];[0:v][pet]overlay=shortest=1:format=auto,format=yuv420p[v]',
        '-map','[v]','-an','-c:v','libx264','-crf','18','-movflags','+faststart',
        str(OUT/f'{name}.mp4')],check=True)
    print('REVIEW ENCODED',name,flush=True)
