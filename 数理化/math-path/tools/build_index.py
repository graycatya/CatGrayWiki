"""从全量 OCR 语料生成「课本题号索引」JS 数据。

输入：<full 目录>/<册目录>/page-*.txt（由 ocr_batch.py 生成）
输出：math-path/js/textbook-index.js

按 OCR 文本中出现的「第 X 章」把页面分段，统计每章的例题编号、
小节编号、练习所在页与估计题量；教参另生成摘要。
公式区域 OCR 会打散，因此这里只索引「题号/标题」这类可靠文本。
"""
import glob
import json
import os
import re

ROOT = "C:/Users/ADMINI~1.DES/AppData/Local/Temp/mathocr/full"
OUT = "C:/Users/Administrator.DESKTOP-AK3752I/WorkBuddy/2026-11-08-14-31-49/math-path/js/textbook-index.js"

BOOK_DIRS = {
    "a1": "alg1", "alg2": "alg2", "alg3": "alg3",
    "ana": "analytic", "geo": "solid", "cal": "calc",
}
REF_DIRS = {
    "ref1": "代数 第一册 教参", "ref2": "代数 第二册 教参", "ref3": "代数 第三册 教参",
    "ref4": "平面解析几何 教参", "ref5": "微积分初步 教参", "ref6": "立体几何 教参",
}
CN = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def cn2int(s):
    if s in CN:
        return CN[s]
    if s.startswith("十") and len(s) > 1:
        return 10 + CN.get(s[1:], 0)
    return None


def page_no(path):
    m = re.search(r"(\d+)\.txt$", os.path.basename(path))
    return int(m.group(1)) if m else 0


def read_pages(dirname):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, dirname, "page-*.txt"))):
        out.append((page_no(f), open(f, encoding="utf-8").read()))
    return out


def build_book(dirname):
    pages = read_pages(dirname)
    if not pages:
        return None
    bounds = []
    seen = set()
    titles = {}
    for n, txt in pages:
        found = []
        for line in txt.splitlines():
            m = re.match(r"^第([一二三四五六七八九十]+)章\s*([^\n]{0,24})$", line.strip())
            if not m:
                continue
            ch = cn2int(m.group(1))
            if ch and ch <= 10:
                found.append(ch)
                if m.group(2).strip():
                    titles.setdefault(ch, m.group(2).strip()[:20])
        # 目录页会在同一页列出多个章名，不能当作章边界
        if len(set(found)) > 1:
            continue
        for ch in dict.fromkeys(found):
            if ch not in seen:
                seen.add(ch)
                bounds.append((ch, n, titles.get(ch, "")))
    bounds.sort(key=lambda x: x[1])
    chapters = {}
    last_page = pages[-1][0]
    for i, (ch, start, title) in enumerate(bounds):
        end = bounds[i + 1][1] if i + 1 < len(bounds) else last_page + 1
        examples, sections, exercise_pages, exercise_max = [], [], [], 0
        for n, txt in pages:
            if not (start <= n < end):
                continue
            for e in re.findall(r"例\s*([0-9０-９]{1,2})", txt):
                e = e.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
                if e.isdigit() and e not in examples:
                    examples.append(e)
            for sn, st in re.findall(r"^\s*([1-9]\.[1-9]\d?)\s+([^\n]{1,26})$", txt, re.M):
                st = st.strip()
                if not re.match(r"^[\u4e00-\u9fa5]", st):
                    continue
                if len(st) > 16 or "，" in st or "。" in st:
                    continue
                if re.search(r"[0-9A-Za-z=+×·:;]", st):
                    continue
                label = sn + " " + st
                if label not in sections:
                    sections.append(label)
            if "练习" in txt or "习题" in txt:
                exercise_pages.append(n)
                nums = [int(x) for x in re.findall(r"^\s*(\d{1,2})\s*[.、．]", txt, re.M)]
                nums = [x for x in nums if 1 <= x <= 40]
                if nums:
                    exercise_max = max(exercise_max, max(nums))
        examples.sort(key=lambda x: int(x))
        chapters[str(ch)] = {
            "start": start, "end": end - 1, "title": title,
            "examples": examples[:40], "sections": sections[:20],
            "exercisePages": exercise_pages[:20], "exerciseMax": exercise_max,
        }
    return {"pages": len(pages), "chapters": chapters}


def build_ref(dirname, label):
    pages = read_pages(dirname)
    if not pages:
        return None
    hits = {"练习": 0, "习题": 0, "提示": 0, "课时": 0, "教学要求": 0, "教材分析": 0}
    for _, txt in pages:
        for k in hits:
            if k in txt:
                hits[k] += 1
    return {"label": label, "pages": len(pages), "hits": hits}


def main():
    idx, refs = {}, {}
    for d, book in BOOK_DIRS.items():
        r = build_book(d)
        if r:
            idx[book] = r
            print(book, r["pages"], "页，章", sorted(r["chapters"].keys()))
    for d, label in REF_DIRS.items():
        r = build_ref(d, label)
        if r:
            refs[d] = r
            print(d, r["pages"], "页", r["hits"])
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("/* 自动生成：tools/build_index.py，依据全量 OCR 语料，仅供检索定位 */\n")
        f.write("(function(){\nvar MP = window.MathPath;\n")
        f.write("MP.TEXTBOOK_INDEX = " + json.dumps(idx, ensure_ascii=False, indent=1) + ";\n")
        f.write("MP.TEXTBOOK_REFS = " + json.dumps(refs, ensure_ascii=False, indent=1) + ";\n")
        f.write("})();\n")
    print("写出", OUT)


if __name__ == "__main__":
    main()
