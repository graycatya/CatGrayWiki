#!/usr/bin/env python3
"""CatGray v10 build entry point. Standard Python 3.9+; no pip packages."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
JOBS={
    'doctor':[('scripts/check_environment.py',[])],
    'rebuild':[('scripts/rig_cat.py',[])],
    'rig':[('scripts/rig_cat.py',['--no-export'])],
    'export':[('scripts/export_rig.py',[])],
    'preview':[('scripts/qa/preview_wave_arc.py',[])],
    'render':[('scripts/render_animations.py',[]),('scripts/render_wave_side.py',[])],
    'render-main':[('scripts/render_animations.py',[])],
    'render-side':[('scripts/render_wave_side.py',[])],
    'encode-main':[('scripts/render_animations.py',['--encode-only'])],
    'verify':[('scripts/qa/verify_rig.py',[]),('scripts/qa/verify_wave_revision.py',[]),('scripts/qa/verify_animated_export.py',[]),('scripts/qa/verify_videos.py',[])],
    'build-base':[('scripts/geometry/build_base.py',['--build-only'])],
}

def blender_path(explicit):
    requested=explicit or os.environ.get('BLENDER_BIN')
    if requested:
        candidate=Path(requested).expanduser()
        if candidate.is_file():return str(candidate)
        resolved=shutil.which(requested)
        if resolved:return resolved
        raise FileNotFoundError(f'Blender executable not found: {requested}')
    found=shutil.which('blender')
    if found:return found
    mac=Path('/Applications/Blender.app/Contents/MacOS/Blender')
    if mac.is_file():return str(mac)
    raise FileNotFoundError('Set BLENDER_BIN to the Blender executable, or pass --blender. See docs/WORKFLOW.md.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender',help='Blender executable path (or set BLENDER_BIN)')
    parser.add_argument('--threads',type=int,default=4,help='Blender CPU threads; default: 4')
    parser.add_argument('command',choices=JOBS,help='See docs/WORKFLOW.md for inputs and overwritten outputs')
    args=parser.parse_args()
    if args.threads<1:parser.error('--threads must be positive')
    try:binary=blender_path(args.blender)
    except FileNotFoundError as error:parser.exit(2,str(error)+'\n')
    for directory in ['qa','qa/logs','previews','animations']:(ROOT/directory).mkdir(parents=True,exist_ok=True)
    for script,extra in JOBS[args.command]:
        log=ROOT/'qa/logs'/(Path(script).stem+'.log')
        cmd=[binary,'--background','--factory-startup','--threads',str(args.threads),'--python-exit-code','1','--python',str(ROOT/script)]
        if extra:cmd+=['--',*extra]
        print(f'Running {script}\nLog: {log}',flush=True)
        with log.open('w',encoding='utf-8') as stream:
            result=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        if result.returncode:
            print(log.read_text(errors='replace')[-6000:],file=sys.stderr)
            return result.returncode if result.returncode>0 else 1
        print(f'Completed {script}',flush=True)
    return 0

if __name__=='__main__':raise SystemExit(main())
