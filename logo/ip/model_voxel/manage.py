#!/usr/bin/env python3
"""CatGray voxel edition. Run with standard Python 3.9+, Blender on PATH."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender",default=os.environ.get("BLENDER_BIN"))
    parser.add_argument("--threads",type=int,default=4)
    parser.add_argument("command",choices=("rebuild","preview","pose-preview","render","encode","export","verify","verify-rig"))
    parser.add_argument("--quick",action="store_true",help="640px / 16 samples for preview")
    args = parser.parse_args()
    if args.threads < 1:
        parser.error("--threads must be positive")
    binary = args.blender or shutil.which("blender")
    if not binary:
        mac = Path("/Applications/Blender.app/Contents/MacOS/Blender")
        binary = str(mac) if mac.is_file() else None
    if not binary:
        parser.error("Blender not found; set BLENDER_BIN or pass --blender")
    log = ROOT/"qa/logs"/(args.command+".log")
    log.parent.mkdir(parents=True,exist_ok=True)
    cmd = [binary,"-b","--factory-startup","--threads",str(args.threads),
           "--python-exit-code","1","--python",str(ROOT/"scripts/blender_model.py"),
           "--",args.command]
    if args.quick:
        cmd.append("--quick")
    print(f"Running {args.command}; log: {log}",flush=True)
    try:
        with log.open("w") as stream:
            result = subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    except OSError as error:
        parser.exit(2,str(error)+"\n")
    if result.returncode:
        print(log.read_text(errors="replace")[-6000:],file=sys.stderr)
        return result.returncode if result.returncode > 0 else 1
    print("Completed",flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
