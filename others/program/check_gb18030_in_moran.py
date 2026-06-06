# -*- coding: utf-8 -*-
"""
对比 GB18030-2022 字表与 rime-moran 的 chars.txt
"""

# 读取 rime-moran 的 chars.txt
moran_chars = {}
with open(r'D:\vscode\rime_projs\rime-moran\tools\data\chars.txt', 'r', encoding='utf-8') as f:
    next(f)  # 跳过标题行
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            char = parts[0]
            pinyin = parts[1]
            if char not in moran_chars:
                moran_chars[char] = []
            moran_chars[char].append(pinyin)

print(f"rime-moran chars.txt: {len(moran_chars)} 个字")

# 读取 GB18030-2022 字表
gb_chars = []
with open(r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml', 'r', encoding='utf-8') as f:
    in_data = False
    for line in f:
        if line.strip() == '...':
            in_data = True
            continue
        if not in_data:
            continue
        line = line.strip()
        if not line:
            continue
        c = line.split('\t')[0]
        if len(c) == 1:
            gb_chars.append(c)

print(f"GB18030-2022 字表: {len(gb_chars)} 个字")

# 对比
has_pinyin = []
no_pinyin = []

for c in gb_chars:
    if c in moran_chars:
        has_pinyin.append((c, moran_chars[c]))
    else:
        no_pinyin.append(c)

print(f"\n在 rime-moran 中有拼音: {len(has_pinyin)} 个")
print(f"在 rime-moran 中无拼音: {len(no_pinyin)} 个")
print(f"覆盖率: {len(has_pinyin)/len(gb_chars)*100:.1f}%")

print(f"\n有拼音的示例 (前20):")
for c, pys in has_pinyin[:20]:
    print(f"  {c} - {', '.join(pys)}")

print(f"\n无拼音的示例 (前20):")
print(f"  {' '.join(no_pinyin[:20])}")
