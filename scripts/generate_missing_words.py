#!/usr/bin/env python3
"""
一键生成缺词表: 下载当日知乎热榜 -> 自定义词库分词 -> 比对 -> 缺词.txt
供 AI 后续查看/追加

流程:
  1. 下载热榜: scripts/download_zhihu_hotlist.py (uapis + Playwright stealth)
  2. 分词: jieba + cn_dicts_dazhu/custom_fenci_dict.txt (参考 yuliao_fenci_to_txt.py)
  3. 比对: 统计分词去重后在词库外的词 -> 缺词.txt

用法:
  python scripts/generate_missing_words.py --limit 30
  python scripts/generate_missing_words.py --limit 30 --hot-txt data/corpus/zhihu_hotlist_2026-08-30.txt

输出:
  - 热榜: data/corpus/zhihu_hotlist_YYYY-MM-DD.txt
  - 分词: /tmp/zhihu_hotlist_fenci.txt (或 data/corpus/zhihu_hotlist_YYYY-MM-DD_fenci.txt)
  - 缺词: data/corpus/zhihu_missing_YYYY-MM-DD.txt  (AI 直接查看此文件)
"""

import argparse
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOT = ROOT / "data" / "corpus" / f"zhihu_hotlist_{date.today().isoformat()}.txt"
DEFAULT_FENCI = Path("/tmp/zhihu_hotlist_fenci.txt")
DEFAULT_MISSING = ROOT / "data" / "corpus" / f"zhihu_missing_{date.today().isoformat()}.txt"
CUSTOM_DICT = ROOT / "cn_dicts_dazhu" / "custom_fenci_dict.txt"

def run_hot(limit: int, hot_txt: Path):
    print(f"=== 1/3 下载热榜 -> {hot_txt} ===")
    cmd = [sys.executable, str(ROOT / "scripts" / "download_zhihu_hotlist.py"), "--limit", str(limit), "--out", str(hot_txt)]
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"完成: {hot_txt} ({hot_txt.stat().st_size} bytes)")

def run_fenci(hot_txt: Path, fenci_txt: Path):
    print(f"=== 2/3 分词 {hot_txt} -> {fenci_txt} ===")
    try:
        import jieba
    except ImportError:
        print("jieba 未安装: pip install jieba --break-system-packages")
        sys.exit(1)

    def is_all_punctuation(text):
        return bool(re.match(r'^[^\w\s]+$', text))
    def replace_punctuation_with_newline(text):
        return re.sub(r'[.,!?;:。，！？；：<>《》]', '\n', text).strip()
    def is_all_chinese(s):
        return bool(re.compile(r'[\u4e00-\u9fa5]+').fullmatch(s))

    if not CUSTOM_DICT.exists():
        print(f"自定义词库不存在，生成: {CUSTOM_DICT}")
        subprocess.run([sys.executable, str(ROOT / "others" / "program" / "mnbvc" / "generate_custom_fenci_dict.py")], check=True)

    print(f"加载自定义词库: {CUSTOM_DICT}")
    jieba.load_userdict(str(CUSTOM_DICT))

    with open(hot_txt, 'r', encoding='utf-8') as rf, open(fenci_txt, 'w', encoding='utf-8') as wf:
        written = 0
        for line in rf:
            line = line.strip()
            if not line:
                continue
            for new_line in replace_punctuation_with_newline(line).split("\n"):
                new_line = new_line.strip()
                if not new_line or len(new_line) <= 4 or not is_all_chinese(new_line):
                    continue
                seg_list = jieba.cut(new_line, cut_all=False)
                text = ""
                for seg in seg_list:
                    seg = seg.strip()
                    if seg in '，。？：！“”、；,.;:\'…[]【】《》<>{}-?!' or is_all_punctuation(seg):
                        continue
                    text += seg + " "
                text = text.strip()
                if not text:
                    continue
                wf.write(text + "\n")
                written += 1
    print(f"完成: {fenci_txt} ({written} 行)")

def run_missing(fenci_txt: Path, missing_txt: Path):
    print(f"=== 3/3 比对 -> {missing_txt} ===")
    if not CUSTOM_DICT.exists() or not fenci_txt.exists():
        print(f"缺少 {CUSTOM_DICT} 或 {fenci_txt}")
        sys.exit(1)
    dict_words = set()
    with open(CUSTOM_DICT, 'r', encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            dict_words.add(line.split()[0])
    print(f"词库总数: {len(dict_words)}")

    seg_words = []
    unique_seg = set()
    with open(fenci_txt, 'r', encoding='utf-8') as f:
        for line in f:
            tokens = line.strip().split()
            seg_words.extend(tokens)
            unique_seg.update(tokens)
    cnt = Counter(seg_words)
    missing = sorted([w for w in unique_seg if w not in dict_words])
    present = len(unique_seg) - len(missing)
    print(f"分词去重: {len(unique_seg)} / 总词数 {len(seg_words)}")
    print(f"在词库: {present} ({present/len(unique_seg)*100:.2f}%)  缺失: {len(missing)} ({len(missing)/len(unique_seg)*100:.2f}%)")
    print("\n缺失 Top20:")
    for w in sorted(missing, key=lambda x: cnt[x], reverse=True)[:20]:
        print(f"  {w}\t{cnt[w]}")

    missing_txt.parent.mkdir(parents=True, exist_ok=True)
    # 写入缺词.txt: 每行 "词\t频次" 供 AI 查看
    with open(missing_txt, 'w', encoding='utf-8') as out:
        out.write(f"# 生成时间 {date.today().isoformat()}  热榜 {fenci_txt}\n")
        out.write(f"# 在库 {present}/{len(unique_seg)}  缺失 {len(missing)}\n")
        for w in sorted(missing, key=lambda x: cnt[x], reverse=True):
            out.write(f"{w}\t{cnt[w]}\n")
    print(f"\n缺词已写入: {missing_txt} ({len(missing)} 词)")
    print(f"AI 查看: cat {missing_txt}")

def main():
    parser = argparse.ArgumentParser(description="一键生成缺词表")
    parser.add_argument("--limit", type=int, default=30, help="热榜数量 (default 30)")
    parser.add_argument("--hot-txt", type=Path, default=DEFAULT_HOT, help="热榜 txt 路径")
    parser.add_argument("--fenci-txt", type=Path, default=DEFAULT_FENCI, help="分词 txt 路径")
    parser.add_argument("--missing-txt", type=Path, default=DEFAULT_MISSING, help="缺词 txt 路径")
    parser.add_argument("--skip-hot", action="store_true", help="跳过下载，直接用现有 hot-txt")
    args = parser.parse_args()

    if not args.skip_hot:
        run_hot(args.limit, args.hot_txt)
    else:
        print(f"跳过下载，使用现有: {args.hot_txt}")

    run_fenci(args.hot_txt, args.fenci_txt)
    run_missing(args.fenci_txt, args.missing_txt)
    print("\n全部完成，AI 可直接查看缺词表:")
    print(f"  cat {args.missing_txt}")

if __name__ == "__main__":
    main()
