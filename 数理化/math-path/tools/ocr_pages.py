"""把已渲染的课本页面 PNG 批量转成文本，供核对/修订课程内容使用。

依赖：隔离 venv 里的 rapidocr_onnxruntime（重建命令见 README 下方注释）。
用法：
  python tools/ocr_pages.py <图片目录> <输出目录> [--start 1] [--end 20]

说明：
  - 图片命名需为 page-0001.png 这样可排序的形式。
  - 已生成的 .txt 会跳过，可断点续跑。
  - 数学公式（分式、极限号、上下标、根号）通用 OCR 会打散，
    这类内容必须回看原页图片，文本仅作检索与定位用。

重建 OCR 环境（若临时目录被清理）：
  /d/programinglanguage/python312/python.exe -m venv /tmp/mathocr/venv
  /tmp/mathocr/venv/Scripts/python.exe -m pip install rapidocr_onnxruntime
"""
import argparse
import os
import re
import sys
import time

from rapidocr_onnxruntime import RapidOCR


def page_key(name):
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--pages", default="", help="逗号分隔的指定页码，如 25,40,55")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(args.src) if f.lower().endswith(".png")],
        key=page_key,
    )
    if args.pages:
        wanted = set(int(x) for x in args.pages.split(",") if x.strip())
        files = [f for f in files if page_key(f) in wanted]
    else:
        files = [f for f in files if args.start <= page_key(f) <= (args.end or 10 ** 9)]
    if not files:
        print("没有找到页面图片")
        return 1

    ocr = RapidOCR()
    done = 0
    t0 = time.time()
    merged = []
    for i, name in enumerate(files, 1):
        n = page_key(name)
        dst = os.path.join(args.out, "page-%04d.txt" % n)
        if os.path.exists(dst):
            body = open(dst, encoding="utf-8").read()
            merged.append("## page-%04d\n\n%s" % (n, body))
            continue
        result, _ = ocr(os.path.join(args.src, name))
        if result:
            rows = []
            for box, text, score in result:
                y = min(p[1] for p in box) if box else 0
                rows.append((y, text))
            rows.sort(key=lambda r: r[0])
            body = "\n".join(t for _, t in rows)
        else:
            body = ""
        with open(dst, "w", encoding="utf-8") as f:
            f.write(body)
        merged.append("## page-%04d\n\n%s" % (n, body))
        done += 1
        if done % 10 == 0:
            print("已处理 %d/%d 页，用时 %.1fs" % (i, len(files), time.time() - t0), flush=True)

    with open(os.path.join(args.out, "book.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(merged))
    print("完成：%d 页，新识别 %d 页，用时 %.1fs" % (len(files), done, time.time() - t0))
    print("输出：", os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
