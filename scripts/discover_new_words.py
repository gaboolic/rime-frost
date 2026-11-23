#!/usr/bin/env python3
"""
从大规模语料中发现词库未收录的新词。

思路:
  1. 归一化语料: 只保留中文连续片段, 每行一段, 便于多次扫描
  2. 统计 1~4 元组频率 (Apriori 剪枝, 避免全量 4-gram)
  3. 用 PMI (凝固度) + 左右邻字熵 (自由度) 筛选成词候选
  4. 过滤已收录词、繁体字、低频碎片, 自动注音并分级
  5. 输出候选 TSV; 高置信度词可直接追加到词库

用法:
  python scripts/discover_new_words.py --corpus yuliao/ --out data/candidates/new_words_2026-11-21.tsv
  python scripts/discover_new_words.py --corpus zhihu.txt --max-chars 5000000 --top 100
  python scripts/discover_new_words.py --corpus yuliao/ --apply-to cn_dicts/others.dict.yaml

说明:
  - 语料支持 .txt / .jsonl / .jsonl.gz; JSONL 默认取 text 字段, 可用 --field 指定
  - 745M 字语料约需 20~40 分钟、数 GB 内存; 先用 --max-chars 5000000 试跑
  - 大语料建议: --min-freq 20 --max-n 3, 内存更省; 加 --skip-token-check 可再省半小时
  - 自动入库只收极少数高置信度词, 其余写入 .review.tsv 供人工确认
"""

import argparse
import gzip
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DICT = ROOT / "cn_dicts_dazhu" / "custom_fenci_dict.txt"
CHARSET_FILE = ROOT / "cn_dicts" / "8105.dict.yaml"
SURNAME_FILE = ROOT / "others" / "百家姓.txt"

CJK_RE = re.compile(r"[\u4e00-\u9fff]+")
BOUNDARY = "\x01"  # 句首/句尾占位符, 让边界也参与邻字熵
PLACE_SUFFIX = set("市县区镇村路街省州岛山河湖江港湾堡庄屯旗盟郡府")
TEXT_FIELDS = ("text", "content", "body", "title", "answer")


# ---------------------------------------------------------------- 语料读取

def iter_files(paths):
    for path in paths:
        path = Path(path)
        if path.is_dir():
            for p in sorted(path.rglob("*")):
                if p.is_file() and p.suffix.lower() in (".txt", ".jsonl", ".json", ".gz"):
                    yield p
        elif path.is_file():
            yield path
        else:
            print(f"跳过不存在的路径: {path}", file=sys.stderr)


def open_text(path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def extract_text(obj, field):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        # --field 支持逗号分隔多个字段 (如 MNBVC 的 "问,答")
        if field:
            parts = [
                obj[key]
                for key in (k.strip() for k in field.split(","))
                if key and isinstance(obj.get(key), str) and obj.get(key)
            ]
            if parts:
                return "\n".join(parts)
        for key in TEXT_FIELDS:
            value = obj.get(key)
            if isinstance(value, str):
                return value
    return ""


def is_jsonl(path):
    name = path.name.lower()
    return name.endswith((".jsonl", ".json", ".jsonl.gz", ".json.gz"))


def iter_texts(path, field):
    with open_text(path) as f:
        if is_jsonl(path):
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = extract_text(obj, field)
                if text:
                    yield text
        else:
            # 纯文本也按行流式读取, 避免大文件一次性读进内存
            for line in f:
                line = line.strip()
                if line:
                    yield line


def normalize_corpus(paths, out_path, field, max_chars):
    """把语料归一化成每行一段中文, 返回总字数。"""
    total = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for path in iter_files(paths):
            for text in iter_texts(path, field):
                for run in CJK_RE.findall(text):
                    if len(run) < 2:
                        continue
                    out.write(run + "\n")
                    total += len(run)
                    if max_chars and total >= max_chars:
                        return total
    return total


# ---------------------------------------------------------------- 词典与字表

def load_charset():
    chars = set()
    for line in open(CHARSET_FILE, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or line in ("---", "..."):
            continue
        if "\t" not in line:
            continue
        char = line.split("\t")[0]
        if len(char) == 1:
            chars.add(char)
    return chars


def load_surnames():
    surnames = set()
    if not SURNAME_FILE.exists():
        return surnames
    for line in open(SURNAME_FILE, encoding="utf-8", errors="ignore"):
        for char in CJK_RE.findall(line):
            surnames.update(char)
    return surnames


def iter_dict_file(file):
    """逐行读出词库里的词, 跳过注释和 YAML 头。"""
    for line in open(file, encoding="utf-8", errors="ignore"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped in ("---", "..."):
            continue
        head = stripped.split("\t")[0].split(" ")[0]
        if ":" in head:
            continue
        if "\t" in stripped:
            word = stripped.split("\t")[0].strip()
        else:
            parts = stripped.split()
            if len(parts) < 2:
                continue
            word = parts[0]
        if word:
            yield word


def load_dict_words(path):
    words = set()
    # 总是扫描实际词库文件, 避免 custom_fenci_dict.txt 过期导致已收录词被当成新词
    for pattern in ("cn_dicts/*.dict.yaml", "cn_dicts_cell/*.dict.yaml"):
        for file in ROOT.glob(pattern):
            words.update(iter_dict_file(file))
    if path.exists():
        for line in open(path, encoding="utf-8", errors="ignore"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            words.add(stripped.split()[0])
    return words


def affix_counts(dict_words, candidates):
    """统计候选作为更长词库词的前缀/后缀出现次数, 用于识别黏着片段。

    例如「河流域」是「黄河流域」「长江流域」…的后缀, 本身不是独立词。
    """
    wanted = set(candidates)
    prefix = Counter()
    suffix = Counter()
    for word in dict_words:
        n = len(word)
        for k in range(2, min(4, n - 1) + 1):
            head = word[:k]
            if head in wanted:
                prefix[head] += 1
            tail = word[-k:]
            if tail in wanted:
                suffix[tail] += 1
    return prefix, suffix


# ---------------------------------------------------------------- 统计

def count_2grams(norm_path):
    chars = Counter()
    grams = Counter()
    with open(norm_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line) < 2:
                continue
            for char in line:
                chars[char] += 1
            padded = BOUNDARY + line + BOUNDARY
            for i in range(len(padded) - 1):
                gram = padded[i:i + 2]
                grams[gram] = grams.get(gram, 0) + 1
    return chars, grams


def count_ngrams(norm_path, lower_grams, size):
    """只统计左右子串都高频的 n 元组 (Apriori 剪枝)。"""
    grams = Counter()
    with open(norm_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line) < 2:
                continue
            padded = BOUNDARY + line + BOUNDARY
            n = len(padded)
            for i in range(n - size + 1):
                if padded[i:i + size - 1] not in lower_grams:
                    continue
                if padded[i + 1:i + size] not in lower_grams:
                    continue
                gram = padded[i:i + size]
                grams[gram] = grams.get(gram, 0) + 1
    return grams


def prune(counter, min_freq):
    return Counter({g: n for g, n in counter.items() if n >= min_freq})


def count_tokens(norm_path, wanted):
    """用 jieba 分词统计候选作为独立词出现的次数, 用于识别跨词边界的碎片。"""
    import jieba

    jieba.setLogLevel(60)
    tokens = Counter()
    with open(norm_path, encoding="utf-8") as f:
        for line in f:
            for token in jieba.cut(line.strip(), cut_all=False, HMM=True):
                if token in wanted:
                    tokens[token] += 1
    return tokens


def entropy(neighbors):
    total = sum(neighbors.values())
    if total <= 0:
        return 0.0
    return -sum((n / total) * math.log2(n / total) for n in neighbors.values())


def finalize_neighbor_stats(wanted, left, right):
    """由邻字分布得到左右熵, 以及最大单一扩展频率 (识别截断碎片)。"""
    ent = {}
    ext = {}
    for gram in wanted:
        lc = left.get(gram)
        rc = right.get(gram)
        ent[gram] = (entropy(lc) if lc else 0.0, entropy(rc) if rc else 0.0)
        best = 0
        if lc:
            best = max(best, max(lc.values()))
        if rc:
            best = max(best, max(rc.values()))
        ext[gram] = best
    return ent, ext


def neighbor_stats(grams, upper_grams):
    """从已统计的 (n+1)-gram 表推算候选的邻字熵与最大扩展频率。"""
    wanted = set(grams)
    left = defaultdict(Counter)
    right = defaultdict(Counter)
    for gram, count in upper_grams.items():
        prefix, suffix = gram[:-1], gram[1:]
        if prefix in wanted:
            right[prefix][gram[-1]] += count
        if suffix in wanted:
            left[suffix][gram[0]] += count
    return finalize_neighbor_stats(wanted, left, right)


def stream_neighbor_stats(norm_path, size, wanted):
    """扫描语料直接统计邻字熵, 不保存整张 size-gram 表 (省内存)。"""
    left = defaultdict(Counter)
    right = defaultdict(Counter)
    with open(norm_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line) < 2:
                continue
            padded = BOUNDARY + line + BOUNDARY
            for i in range(len(padded) - size + 1):
                gram = padded[i:i + size]
                prefix, suffix = gram[:-1], gram[1:]
                if prefix in wanted:
                    right[prefix][gram[-1]] += 1
                if suffix in wanted:
                    left[suffix][gram[0]] += 1
    return finalize_neighbor_stats(wanted, left, right)


def pmi(gram, counts, total):
    """PMI: 候选词整体频率与各切分部分频率的比值, 取最差切分。"""
    count = counts.get(gram, 0)
    if count <= 0 or len(gram) < 2:
        return -99.0
    best = 99.0
    for k in range(1, len(gram)):
        left, right = gram[:k], gram[k:]
        cl = counts.get(left, 0)
        cr = counts.get(right, 0)
        if cl <= 0 or cr <= 0:
            return -99.0
        value = math.log2((count / total) / ((cl / total) * (cr / total)))
        best = min(best, value)
    return best


# ---------------------------------------------------------------- 注音与标记

def word_pinyin(word):
    import pypinyin
    from pypinyin import Style, pinyin

    readings = pinyin(word, style=Style.NORMAL, heteronym=False)
    syllables = [r[0] for r in readings]
    # 多音字: 该字有多个读音, 且词组没有收录在 pypinyin 短语表里
    heteronyms = pinyin(word, style=Style.NORMAL, heteronym=True)
    ambiguous = []
    for char, variants in zip(word, heteronyms):
        distinct = list(dict.fromkeys(variants))
        if len(distinct) > 1 and word not in pypinyin.phrases_dict.phrases_dict:
            ambiguous.append(char)
    return " ".join(syllables), ambiguous


def is_name_like(word, surnames, tag):
    if tag.startswith("nr"):
        return True
    if 2 <= len(word) <= 3 and word[0] in surnames and len(word) >= 2:
        return True
    return False


def is_place_like(word):
    return len(word) >= 2 and word[-1] in PLACE_SUFFIX


FUNCTION_TAGS = {"q", "m", "r", "u", "uj", "ul", "ud", "ug", "uz", "p", "c", "d", "f", "y", "e", "o", "x"}


def split_fragment(word, dict_words):
    """能被切成「已知词 + 单字虚词」的, 多半是跨词边界的碎片。"""
    for k in range(1, len(word)):
        left, right = word[:k], word[k:]
        if len(right) == 1 and left in dict_words and pos_tag(right) in FUNCTION_TAGS:
            return True
        if len(left) == 1 and right in dict_words and pos_tag(left) in FUNCTION_TAGS:
            return True
    return False


def pos_tag(word):
    import jieba.posseg as pseg

    tags = [pair.flag for pair in pseg.cut(word)]
    return tags[0] if tags else "x"


# ---------------------------------------------------------------- 输出与入库

def write_candidates(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("word\tfreq\tpmi\tleft_h\tright_h\ttoken_ratio\tscore\tpinyin\tflags\n")
        for row in rows:
            f.write("\t".join("" if x is None else str(x) for x in row) + "\n")


def append_to_dict(target, rows, source):
    target = Path(target)
    existing = load_dict_words(target)
    entries = []
    for row in rows:
        word, _, _, _, _, _, _, pinyin, flags = row
        if word in existing or "name?" in flags or "place?" in flags or "polyphone?" in flags or "pos=" in flags or "fragment?" in flags or "truncated?" in flags or "affix?" in flags:
            continue
        entries.append((word, pinyin))
    if not entries:
        print("没有可入库的高置信度词。")
        return 0

    entries.sort()
    with open(target, "a", encoding="utf-8") as f:
        f.write(f"# {date.today().isoformat()} 新词发现自动补录（语料: {source}）\n")
        for word, pinyin in entries:
            f.write(f"{word}\t{pinyin}\t0\n")
    print(f"已追加 {len(entries)} 个词到 {target}")
    return len(entries)


# ---------------------------------------------------------------- 主流程

def main():
    parser = argparse.ArgumentParser(description="从语料中发现词库未收录的新词")
    parser.add_argument("--corpus", nargs="+", required=True, help="语料文件或目录, 可多个")
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "candidates" / f"new_words_{date.today().isoformat()}.tsv")
    parser.add_argument("--dict", type=Path, default=DEFAULT_DICT, help="已收录词表 (默认 custom_fenci_dict.txt)")
    parser.add_argument("--field", default="text", help="JSONL 取哪个字段 (默认 text)")
    parser.add_argument("--max-chars", type=int, default=0, help="最多处理多少字, 0 为不限")
    parser.add_argument("--max-n", type=int, default=3, choices=(2, 3, 4), help="最长候选词字数 (默认 3; 4 字会多跑一遍 5-gram)")
    parser.add_argument("--min-freq", type=int, default=10, help="2 字词最低频次 (默认 10)")
    parser.add_argument("--min-pmi", type=float, default=3.0, help="最低凝固度 PMI (默认 3.0)")
    parser.add_argument("--min-entropy", type=float, default=0.8, help="最低左右邻字熵 (默认 0.8)")
    parser.add_argument("--top", type=int, default=200, help="终端打印前多少个候选")
    parser.add_argument("--apply-to", type=Path, default=None, help="把高置信度词追加到该词库文件")
    parser.add_argument("--auto-score", type=float, default=25.0, help="自动入库最低分数 (默认 25, 很保守)")
    parser.add_argument("--auto-freq", type=int, default=30, help="自动入库最低频次 (默认 30)")
    parser.add_argument("--allow-polyphone", action="store_true", help="允许多音字存疑的词自动入库")
    parser.add_argument("--skip-token-check", action="store_true", help="跳过 jieba 分词校验 (大语料可省约半小时)")
    parser.add_argument("--keep-norm", action="store_true", help="保留归一化后的中间文件")
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    norm_path = args.out.parent / f".norm_{os.getpid()}.txt"

    print("=== 1/4 归一化语料 ===")
    total = normalize_corpus(args.corpus, norm_path, args.field, args.max_chars)
    if total == 0:
        print("语料为空, 退出。")
        norm_path.unlink(missing_ok=True)
        return
    print(f"中文语料: {total} 字 -> {norm_path}")

    print("=== 2/4 统计 n-gram ===")
    chars, c2 = count_2grams(norm_path)
    c2 = prune(c2, args.min_freq)
    print(f"1-gram: {len(chars)}  2-gram: {len(c2)}")

    counts = {}
    counts.update(chars)
    counts.update(c2)
    c3 = Counter()
    c4 = Counter()
    # c3 既用于 3-gram 候选, 也用于 2 字词的邻字熵
    c3 = prune(count_ngrams(norm_path, c2, 3), max(3, args.min_freq // 2))
    counts.update(c3)
    print(f"3-gram: {len(c3)}")
    if args.max_n >= 4:
        # 只有需要 4 字候选时才保存 4-gram 表; 3 字词的熵改用流式扫描
        c4 = prune(count_ngrams(norm_path, c3, 4), max(2, args.min_freq // 4))
        counts.update(c4)
        print(f"4-gram: {len(c4)}")

    print("=== 3/4 计算凝固度与自由度 ===")
    dict_words = load_dict_words(args.dict)
    charset = load_charset()
    surnames = load_surnames()
    print(f"词库: {len(dict_words)} 词  字表: {len(charset)} 字")

    # 先做便宜的基础过滤, 只对通过的候选算邻字熵
    raw = []
    for gram, freq in counts.items():
        if len(gram) < 2 or len(gram) > args.max_n:
            continue
        if gram in dict_words:
            continue
        if any(char not in charset for char in gram):
            continue
        min_freq = args.min_freq if len(gram) == 2 else max(3, args.min_freq // 2)
        if freq < min_freq:
            continue
        score_pmi = pmi(gram, counts, total)
        if score_pmi < args.min_pmi:
            continue
        raw.append((gram, freq, score_pmi))
    print(f"基础过滤后候选: {len(raw)}")

    print("=== 分词校验 ===")
    wanted = {gram for gram, _, _ in raw}
    if args.skip_token_check:
        token_counts = None
        print("已跳过 jieba 分词校验 (--skip-token-check)")
    else:
        token_counts = count_tokens(norm_path, wanted)
        print(f"其中 jieba 作为独立词切出的候选: {len(token_counts)}")

    prefix_counts, suffix_counts = affix_counts(dict_words, wanted)
    print(f"作为更长词库词前缀/后缀的候选: {len(set(prefix_counts) | set(suffix_counts))}")

    by_len = {2: set(), 3: set(), 4: set()}
    for gram, _, _ in raw:
        by_len[len(gram)].add(gram)
    ent = {}
    ext = {}
    if by_len[2] and c3:
        e, x = neighbor_stats(by_len[2], c3)
        ent.update(e)
        ext.update(x)
    if by_len[3]:
        # 有 4-gram 表就直接用, 否则流式扫描语料 (省内存)
        if c4:
            e, x = neighbor_stats(by_len[3], c4)
        else:
            print("流式统计 3 字词邻字熵 ...")
            e, x = stream_neighbor_stats(norm_path, 4, by_len[3])
        ent.update(e)
        ext.update(x)
    if by_len[4]:
        print("流式统计 4 字词邻字熵 ...")
        e, x = stream_neighbor_stats(norm_path, 5, by_len[4])
        ent.update(e)
        ext.update(x)

    candidates = []
    for gram, freq, score_pmi in raw:
        left_h, right_h = ent.get(gram, (0.0, 0.0))
        min_h = min(left_h, right_h)
        if min_h < args.min_entropy:
            continue

        token_ratio = token_counts.get(gram, 0) / freq if token_counts is not None and freq else None
        ext_ratio = ext.get(gram, 0) / freq if freq else 0.0
        pinyin_text, ambiguous = word_pinyin(gram)
        tag = pos_tag(gram)
        flags = []
        if ambiguous:
            flags.append("polyphone?" + "/".join(ambiguous))
        if is_name_like(gram, surnames, tag):
            flags.append("name?")
        if is_place_like(gram):
            flags.append("place?")
        if tag.startswith(("x", "u", "p", "c", "r")):
            flags.append(f"pos={tag}")
        fragment = split_fragment(gram, dict_words)
        if fragment:
            flags.append("fragment?")
        truncated = ext_ratio >= 0.9
        if truncated:
            flags.append("truncated?")
        affix = max(prefix_counts.get(gram, 0), suffix_counts.get(gram, 0)) >= 3
        if affix:
            flags.append("affix?")
        if token_ratio is not None and token_ratio < 0.05:
            flags.append("oov?")

        penalty = 0.0
        if fragment:
            penalty += 3.0
        if truncated:
            penalty += 3.0
        if affix:
            penalty += 3.0
        if token_ratio is not None and token_ratio < 0.05:
            penalty += 1.0
        if "name?" in flags or "place?" in flags:
            penalty += 1.0
        if any(f.startswith("pos=") for f in flags):
            penalty += 2.0
        # 凝固度 (PMI) 是最可靠的成词信号, 频率和自由度只做辅助
        tr = token_ratio or 0.0
        score = 2.0 * max(0.0, score_pmi) + 0.5 * math.log2(freq) + 0.5 * min_h + 2.0 * tr - penalty
        candidates.append([gram, freq, round(score_pmi, 2), round(left_h, 2), round(right_h, 2),
                           None if token_ratio is None else round(token_ratio, 3),
                           round(score, 2), pinyin_text, ",".join(flags)])

    candidates.sort(key=lambda row: row[6], reverse=True)
    write_candidates(args.out, candidates)

    auto = [row for row in candidates
            if row[6] >= args.auto_score and row[1] >= args.auto_freq
            and "name?" not in row[8] and "place?" not in row[8]
            and "pos=" not in row[8] and "fragment?" not in row[8]
            and "truncated?" not in row[8]
            and "affix?" not in row[8]
            and (row[5] is None or row[5] >= 0.2)
            and (args.allow_polyphone or "polyphone?" not in row[8])]
    if args.skip_token_check:
        # 没有分词校验时自动入库风险太高, 只输出待确认
        auto = []
        print("已跳过分词校验, 本次不自动入库, 请人工审核 .review.tsv")
    auto_words = {row[0] for row in auto}
    review = [row for row in candidates if row[0] not in auto_words]
    review_path = args.out.with_suffix(".review.tsv")
    write_candidates(review_path, review)

    print(f"=== 4/4 候选: {len(candidates)}  自动入库: {len(auto)}  待人工确认: {len(review)} ===")
    print(f"候选文件: {args.out}")
    print(f"待确认文件: {review_path}")
    print("\nTop 候选:")
    for row in candidates[:args.top]:
        print(f"  {row[0]}\t频次={row[1]}\tPMI={row[2]}\t熵={row[3]}/{row[4]}\t词比={row[5]}\t分={row[6]}\t{row[7]}\t{row[8]}")

    if args.apply_to:
        append_to_dict(args.apply_to, auto, ", ".join(str(p) for p in args.corpus))

    if not args.keep_norm:
        norm_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
