# AGENTS.md

本文件是 rime-frost 词库的维护规则，供参与「语料挖词 → 人工审核 → 分流入库」的 Agent 和人阅读。新增词条、修改词频、整理错字词时，以本文件为准。

## 1. 目录职责

| 路径 | 用途 |
| --- | --- |
| `cn_dicts/others.dict.yaml` | 默认落点：独立新词、专业术语、热词、网络词 |
| `cn_dicts_cell/name.dict.yaml` | 人名、作者/学者/导演/运动员、动漫游戏角色名 |
| `cn_dicts_cell/composite.dict.yaml` | 跨词短语、动作搭配（如「注射血清」「摘了眼镜」） |
| `cn_dicts_cell/place.dict.yaml` | 地名、遗址、虚构地名、机构/校区名 |
| `cn_dicts_cell/game.dict.yaml`、`literature.dict.yaml` 等 | 游戏、动漫、文学等专用名词，按现有细胞词库归类 |
| `cn_dicts/corrections.dict.yaml` | Rime 输入纠错：错误拼音/错字也能打出正确词 |
| `others/错字词.txt` | 语料词频归并映射：错写 → 标准写法 |
| `scripts/discover_new_words.py` | 新词发现脚本 |
| `scripts/README_new_words.md` | 脚本参数、输出字段、审核流程的详细说明 |
| `data/corpus_mnbvc/zhihu_corpus.txt` | 知乎正文语料（gitignored，约 2.0GB / 5.97 亿字） |
| `data/candidates/*.tsv` | 候选表（gitignored） |
| `others/知频.txt`、`others/维基频.txt` | 候选佐证词频表 |

## 2. 分流口径（最重要）

一个候选词按下面顺序判定，**不要因为「不是独立词」就直接丢弃**：

```text
1. 跨词碎片（高下立判的「立判」、保护牙齿的「护牙」）→ 丢弃
2. 与词库标准写法冲突的变体（湿罗音 / 血粘度）→ others/错字词.txt
3. 人名 / 角色名（宫部美雪、雪代巴、冯诺伊曼）→ name.dict.yaml
4. 地名 / 机构名（柏林洪堡、珠峰南坡、郭店楚墓）→ place.dict.yaml
5. 跨词短语 / 动作搭配（注射血清、沪语报站、敢打包票）→ composite.dict.yaml
6. 游戏 / 动漫 / 文学专名 → game.dict.yaml、literature.dict.yaml（通用术语仍进 others）
7. 其余独立词 / 专业术语 → cn_dicts/others.dict.yaml
```

补充规则：

- `name?` / `place?` 只是脚本的粗标记，**不等于可以直接入库**；人名、地名要人工确认后分流到对应细胞词库。
- 纯人名、纯地名不要丢，进 `name` / `place`。
- 有意义的跨词短语不要丢，进 `composite`。
- 只在确认是跨词碎片（前后字固定、自由度低）时才丢弃。
- 虚词边界是**软信号**：`和 / 了 / 而 / 之` 等出现在词中不一定是碎片。`氘和氚`、`拽了拽`、`锂铍硼`、`慨而慷` 都是可收的固定搭配。
- 品牌、产品、网络词按既有惯例可入 `others`；纯公司名没有专用细胞词库时不强行新增文件。

## 3. 错字词规则（`others/错字词.txt`）

格式：每行两列，`错写<TAB>正确`，UTF-8，无表头。

```text
湿罗音	湿啰音
血粘度	血黏度
莲花清瘟	连花清瘟
欧陆词典	欧路词典
```

用途：

- `others/program/mnbvc/merge_fenci_freq_result.py` 和 `generate_custom_fenci_dict.py` 会读取该文件，把「错写」的词频归并到「正确」写法。
- 遇到与词库已有标准写法冲突的候选，**不把变体加进词库**，而是写进这里归并。
- 写映射前确认「正确」写法已在词库；不在就先把正确写法加进词库。
- 这里只处理**同词错写**；错误拼音 → 正确词的输入纠错放 `cn_dicts/corrections.dict.yaml`，两者不要混。

## 4. 新词发现脚本

依赖：

```bash
pip install jieba pypinyin
```

常用命令（在仓库根目录执行）：

```bash
# 2~3 字，低频高召回，约 1.2 小时 / 4GB
python3 scripts/discover_new_words.py \
  --corpus data/corpus_mnbvc/zhihu_corpus.txt \
  --max-n 3 --min-freq 20 \
  --out data/candidates/new_words_mnbvc_mf20.tsv

# 4 字词专项，约 1.5 小时 / 峰值 4.8GB
python3 scripts/discover_new_words.py \
  --corpus data/corpus_mnbvc/zhihu_corpus.txt \
  --max-n 4 --min-freq 60 \
  --out data/candidates/new_words_mnbvc_4gram.tsv
```

参数要点：

- `--min-freq`：2 字候选的下限；3 字、4 字按 `max(3, min-freq/2)` 取。
- `--max-n 4` 才会产出四字候选，内存和耗时明显增加。
- `--skip-token-check` 可省约半小时，但会失去 jieba 词比这一列。
- 大语料建议给进程设 `oom_score_adj=1000`，避免影响其他服务。
- 语料支持 `.txt`、`.jsonl`、`.jsonl.gz`；JSONL 默认取 `text` 字段，可用 `--field` 指定。

输出 TSV 列：

```text
word  freq  pmi  left_h  right_h  token_ratio  score  pinyin  flags
```

- `pmi`：凝固度；`left_h` / `right_h`：左右邻字熵；`token_ratio`：jieba 作为独立词切出的比例；`flags`：风险标记。
- 详细说明见 `scripts/README_new_words.md`。

## 5. 筛选口径

先排除硬伤标记：

```text
name?  place?  fragment?  truncated?  affix?  pos=
```

但注意：`name?` / `place?` 命中的候选要转到 `name` / `place` 复核，不是直接丢弃。

分长度筛选的参考阈值（结合语料人工确认）：

- **2 字**：按「知频/维基频佐证 ≥ 3」「jieba 词比 ≥ 0.5」「分数」分组浏览；重点看是否跨词。
- **3 字**：`词比 ≥ 0.8 且 PMI ≥ 7`，或知频/维基频证据 ≥ 10；OOV 术语可放宽到 `词比 ≥ 0.9 且 PMI ≥ 8`。
- **4 字**：`PMI ≥ 10`、`min(left_h, right_h) ≥ 2.0`、`freq ≥ 25`，再人工审核。

人工核对方法：

- 回语料看上下文，统计候选的**前字/后字分布**。前字高度集中说明是更长词的碎片（如「彩虹色」里的「虹色」、「保护牙」里的「护牙」）。
- 左右熵很低（< 1）通常是碎片。
- 纯人名、地名、品牌、作品名按第 2 节分流。
- 宁缺毋滥；不确定的候选先不入库。

## 6. 分支与提交流程

日常词库批次统一走「从最新 master 切分支 → PR → 合并 → 同步 develop」：

```bash
git fetch origin master

# 建议用 worktree，保持主 checkout 干净
git worktree add /tmp/opencode/wt-YYYYMMDD -b dict-YYYY-MM-DD[-后缀] origin/master
cd /tmp/opencode/wt-YYYYMMDD

# 只改词库/字典文件，追加即可，不要重排已有内容
# cn_dicts/others.dict.yaml
# cn_dicts_cell/*.dict.yaml
# others/错字词.txt

git add <改动文件>
git commit -m "dict(others): YYYY-MM-DD 新增 ..."
git push -u origin dict-YYYY-MM-DD[-后缀]

gh pr create --repo gaboolic/rime-frost --base master \
  --head dict-YYYY-MM-DD[-后缀] \
  --title "..." --body "..."

gh pr merge <PR号> --repo gaboolic/rime-frost --merge

# 回到主仓库同步 develop
cd /vol1/gbl/sourcecode/rime-proj/rime-frost
git fetch origin master
git merge origin/master --no-edit

# 清理
git worktree remove /tmp/opencode/wt-YYYYMMDD
git branch -D dict-YYYY-MM-DD[-后缀]
```

约定：

- 分支名：`dict-YYYY-MM-DD`，同一天多批加后缀，如 `dict-2026-11-25-mnbvc-4char`。
- 提交信息：`dict(others): ...`、`dict(cell): ...`，说明日期、范围、数量。
- 合并方式用 `--merge`（保留 merge commit），不用 squash。
- 新词词频统一写 `0`。
- 追加批次时加一行注释说明日期和来源，例如：
  `# 2026-11-25 新增：MNBVC 知乎语料四字词（219 词）`。
- 冲突处理：词库是追加式文件，通常两边都保留，再按日期排序整理。
- 不要推送 `develop`；`develop` 可能领先 `origin/develop` 很多提交。

## 7. 校验清单

提交前逐项检查：

1. 新词不在 `cn_dicts/*.dict.yaml` 和 `cn_dicts_cell/*.dict.yaml` 中（注意同词不同拼音的已有条目）。
2. 新增条目在本批次内无重复。
3. 拼音音节数等于字数：`len(pinyin.split()) == len(word)`。
4. 每行三列，Tab 分隔：`词<TAB>拼音<TAB>0`。
5. `others/错字词.txt` 每行恰好两列：`错写<TAB>正确`。
6. `git diff --stat` 只包含本次要改的文件。
7. 抽查 10~20 个词的拼音，特别是多音字（铝 `lv`、熵 `shang`、氘 `dao`、氚 `chuan`、塞族 `sai zu`、西什库 `xi shi ku`）。

## 8. 定时任务：知乎热词缺词补录

固定流程，按顺序执行，不要跳步。

### 8.1 同步 develop

```bash
git checkout develop
git fetch origin master
git merge origin/master --no-edit
```

`develop` 可能领先 `origin/develop`，**不要 push develop**。

### 8.2 生成缺词表

```bash
python3 scripts/generate_missing_words.py --limit 30
```

脚本依次执行：下载当日知乎热榜 → jieba 分词 → 与 `cn_dicts_dazhu/custom_fenci_dict.txt` 比对 → 写出缺词表。

产物：

- `data/corpus/zhihu_hotlist_{YYYY-MM-DD}.txt`：热榜原文
- `/tmp/zhihu_hotlist_fenci.txt`：分词结果
- `data/corpus/zhihu_missing_{YYYY-MM-DD}.txt`：缺词表，**前两行是 `#` 注释，其余为 `词<TAB>频次`**

说明：

- 缺词表同时包含**需要加的热词**和**分词碎片**，必须逐条判断。
- 热榜下载依赖 Playwright；已有热榜时可加 `--skip-hot` 复用。
- 自定义分词词库不存在时，脚本会自动调用 `others/program/mnbvc/generate_custom_fenci_dict.py` 生成。
- `data/` 已 gitignore，热榜和缺词表不用提交。

### 8.3 逐条分析缺词表

读取 `data/corpus/zhihu_missing_{YYYY-MM-DD}.txt`，**按行逐条**处理：

1. 跳过 `#` 开头行。
2. 丢弃分词碎片：单字、跨词组合、虚词拼接、明显不是词的榜单短语。
3. 需要加的热词/术语/专名，按第 2 节分流：
   - 独立热词、术语 → `cn_dicts/others.dict.yaml`
   - 人名 → `cn_dicts_cell/name.dict.yaml`
   - 地名/机构 → `cn_dicts_cell/place.dict.yaml`
   - 跨词短语 → `cn_dicts_cell/composite.dict.yaml`
   - 错写变体 → `others/错字词.txt`
4. 写入格式：`词<TAB>拼音<TAB>0`，频率固定写 `0`。
5. 入库前查重（`cn_dicts` 和 `cn_dicts_cell` 都要查），拼音音节数必须等于字数。

### 8.4 提交到当日词库分支

词库分支必须**基于最新 master**，且**只包含词库变更**：

```bash
git fetch origin master
git checkout -b dict-{YYYY-MM-DD} origin/master

# 只暂存本次改动的词库文件，禁止 git add -A
git add cn_dicts/others.dict.yaml
# 以及本次改到的 cn_dicts_cell/*.dict.yaml、others/错字词.txt

git commit -m "dict(others): {YYYY-MM-DD} 新增知乎热词（N 词）"
git push -u origin dict-{YYYY-MM-DD}
```

注意：

- 工作区里 develop 的其他未提交改动（例如 `scripts/download_zhihu_hotlist.py`）不要带进词库分支。
- 如果切分支会把非词库改动一起带过去，先 `git stash push <非词库文件>`，切分支后再恢复。
- 分支基点是 `origin/master`，不能基于 `develop`；如果远端已有同名 `dict-{YYYY-MM-DD}`，改用 `dict-{YYYY-MM-DD}-b` 并说明。

### 8.5 提 PR 并合并

```bash
gh pr create --repo gaboolic/rime-frost --base master \
  --head dict-{YYYY-MM-DD} \
  --title "dict(others): {YYYY-MM-DD} 新增知乎热词（N 词）" \
  --body "..."

gh pr merge <PR号> --repo gaboolic/rime-frost --merge
```

### 8.6 收尾

```bash
git checkout develop
git merge origin/master --no-edit
```

如果 develop 工作区还保留着本次词库改动，先丢弃或 stash，避免与合并冲突；改动已经通过 PR 进入 master，不会丢失。

## 9. 数据与注意事项

- MNBVC 原始 `.jsonl.gz` 保留在 `data/corpus_mnbvc/zhihu/`，不要删除。
- `data/`、`data/candidates/` 已 gitignore，候选表不用提交。
- 语料只用知乎正文（`问` / `答`），不含 `来源` / `元数据` / `扩展字段`。
- 本仓库主 checkout 可能有未提交的 `scripts/download_zhihu_hotlist.py` 修改；除非任务明确要求，不要顺手提交。
- 跑大语料前先确认内存；峰值 4~5GB 属正常，超过可用内存时提高 `--min-freq` 重跑。
- 词频统计时，`others/错字词.txt` 的错写词频要归并到正确写法，再参与入库判断。
