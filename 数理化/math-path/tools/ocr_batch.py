"""多进程全量 OCR：把一个父目录下每册的页面 PNG 转成文本语料。

用法：
  python tools/ocr_batch.py <页面父目录> <输出父目录> [--workers 6] [--only alg1,calc]

目录约定：
  <页面父目录>/<册名>/page-0001.png ...
  <输出父目录>/<册名>/page-0001.txt + book.md（按页合并）

特性：
  - 已存在的 .txt 自动跳过，可断点续跑
  - 原子写，避免中断产生半截文件
  - 每个进程只加载一次 OCR 模型
  - 公式（分式/极限/上下标）通用 OCR 会打散，文本只作检索定位用

依赖隔离 venv：rapidocr_onnxruntime（重建命令见 ocr_pages.py 文件头）。
"""
import argparse
import glob
import os
import re
import time
from multiprocessing import Pool

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

_OCR = None


def _init():
    global _OCR
    from rapidocr_onnxruntime import RapidOCR
    # 课本均为正向印刷，关闭方向分类；限制检测输入并限线程，避免多进程争抢 CPU
    _OCR = RapidOCR(use_cls=False, det_limit_side_len=480,
                    intra_op_num_threads=2, inter_op_num_threads=1)


def _key(name):
    m = re.search(r"(\d+)", os.path.basename(name))
    return int(m.group(1)) if m else 0


def _work(task):
    src, dst = task
    if os.path.exists(dst):
        return 0
    try:
        result, _ = _OCR(src)
    except Exception:
        return -1
    if result:
        rows = []
        for box, text, score in result:
            y = min(p[1] for p in box) if box else 0
            rows.append((y, text))
        rows.sort(key=lambda r: r[0])
        body = "\n".join(t for _, t in rows)
    else:
        body = ""
    tmp = dst + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(body)
    os.replace(tmp, dst)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    dirs = sorted(d for d in os.listdir(args.root) if os.path.isdir(os.path.join(args.root, d)))
    if args.only:
        wanted = set(args.only.split(","))
        dirs = [d for d in dirs if d in wanted]

    tasks = []
    for d in dirs:
        src_dir = os.path.join(args.root, d)
        out_dir = os.path.join(args.out, d)
        os.makedirs(out_dir, exist_ok=True)
        for f in sorted(os.listdir(src_dir), key=_key):
            if not f.lower().endswith(".png"):
                continue
            dst = os.path.join(out_dir, "page-%04d.txt" % _key(f))
            tasks.append((os.path.join(src_dir, f), dst))

    total = len(tasks)
    todo = sum(1 for _, d in tasks if not os.path.exists(d))
    print("共 %d 页，待识别 %d 页，%d 进程" % (total, todo, args.workers), flush=True)
    t0 = time.time()
    done = 0
    with Pool(args.workers, initializer=_init) as pool:
        for _ in pool.imap_unordered(_work, tasks, chunksize=4):
            done += 1
            if done % 100 == 0:
                print("进度 %d/%d，用时 %.0fs" % (done, total, time.time() - t0), flush=True)

    for d in dirs:
        out_dir = os.path.join(args.out, d)
        chunks = []
        for f in sorted(glob.glob(os.path.join(out_dir, "page-*.txt")), key=_key):
            chunks.append("### " + os.path.basename(f) + "\n" + open(f, encoding="utf-8").read().strip())
        with open(os.path.join(out_dir, "book.md"), "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(chunks))
    print("完成，用时 %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
