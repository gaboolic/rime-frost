# 语料新词发现

`discover_new_words.py` 用大规模中文语料找出词库里还没有的词（比如「软解」「充会电」这类新词、口语词、专业词）。

它不依赖任何外部词表：只统计语料里的 n-gram 频率，用**凝固度（PMI）**和**左右邻字熵**判断一个字串到底是不是一个词，再自动注音、打标记，输出一份按可信度排序的候选表供人工审核。

## 依赖

```bash
pip install jieba pypinyin
```

## 快速试跑

先用少量语料确认环境和效果：

```bash
python3 scripts/discover_new_words.py \
  --corpus data/corpus \
  --max-chars 3000000 \
  --top 30
```

输出：

- `data/candidates/new_words_<日期>.tsv`：全部候选
- `data/candidates/new_words_<日期>.review.tsv`：需要人工确认的候选

## 在 745M 字语料上运行

仓库 README 提到词库是基于 745,396,750 字语料统计的。把语料目录（`.txt` / `.jsonl` / `.jsonl.gz`）传给 `--corpus` 即可：

```bash
python3 scripts/discover_new_words.py \
  --corpus yuliao/ \
  --min-freq 20 \
  --max-n 3 \
  --out data/candidates/new_words_full.tsv
```

说明：

- 语料支持 `.txt`、`.jsonl`、`.jsonl.gz`；JSONL 默认取 `text` 字段，可用 `--field` 指定，多个字段用逗号分隔（如 MNBVC 的 `--field 问,答`）。
- 745M 字约需 **20~40 分钟**、**数 GB 内存**（15GB 内存的机器够用）。
- 内存紧张时：`--max-n 3`（默认）只保留 2/3-gram 表，4 字词的熵用流式扫描，省内存。
- 想再省时间可加 `--skip-token-check`（跳过 jieba 分词校验，约省半小时；此时不会自动入库，只输出待审核表）。
- 先用 `--max-chars 5000000` 试跑，确认参数和输出符合预期再跑全量。

## 输出字段

| 字段 | 含义 |
| --- | --- |
| `word` | 候选词 |
| `freq` | 在语料中的出现次数 |
| `pmi` | 凝固度，越高越像一个整体 |
| `left_h` / `right_h` | 左右邻字熵，越高说明用法越自由 |
| `token_ratio` | jieba 把它当独立词切出的比例（跳过校验时为空） |
| `score` | 综合分数，用于排序和自动入库 |
| `pinyin` | 自动注音（Rime 风格，`nv`/`lv`） |
| `flags` | 风险标记，见下 |

### flags 说明

| 标记 | 含义 | 处理建议 |
| --- | --- | --- |
| `polyphone?X` | 含多音字 X，注音可能不准 | 人工确认读音 |
| `name?` | 像人名 | 一般不入库 |
| `place?` | 像地名 | 一般不入库 |
| `pos=x/u/p/c/r` | 词性像虚词/代词等 | 一般不入库 |
| `fragment?` | 可切成「已知词 + 单字虚词」，像跨词碎片 | 一般不入库 |
| `truncated?` | 几乎总是出现在更长的固定字串里，像被截断 | 一般不入库 |
| `affix?` | 常作为更长词库词的前缀/后缀，像黏着片段 | 一般不入库 |
| `oov?` | jieba 不把它当独立词 | 新词常见，需人工判断 |

## 审核与入库

候选表按 `score` 从高到低排序。建议：

1. 先看 `flags` 为空或只有 `oov?` 的词，这些最可能是真新词。
2. 含 `name?` / `place?` / `fragment?` / `truncated?` 的基本可以跳过。
3. 含 `polyphone?` 的确认读音后再入库。
4. 确认后的词按 `词 拼音 频率` 追加到 `cn_dicts/others.dict.yaml`，频率一般填 `0`。

也可以让脚本自动追加**极少数高置信度词**（默认阈值很保守，通常只会加入个位数）：

```bash
python3 scripts/discover_new_words.py \
  --corpus yuliao/ \
  --min-freq 20 \
  --apply-to cn_dicts/others.dict.yaml
```

## 局限

- 新词发现是**高召回、低精度**：它会把大量碎片、人名、地名一起找出来，最终仍需人工判断。
- 小语料（几百万字）噪声很大，只适合验证流程；真正有效需要千万字以上的语料。
- 自动注音对多音字、专有名词可能不准，入库前应抽查。
- 它只能发现「语料里出现过」的词；语料里没有的词，任何统计方法都找不到。
