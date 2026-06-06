# -*- coding: utf-8 -*-
"""
统计 GB18030-2022 字表中有读音的字，并更新字典
"""
from pypinyin import pinyin, Style
from pathlib import Path

dict_file = Path(r"D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml")

# 读取现有字典
entries = []
with open(dict_file, 'r', encoding='utf-8') as f:
    header = []
    in_data = False
    for line in f:
        if line.strip() == '...':
            in_data = True
            header.append(line)
            continue
        if not in_data:
            header.append(line)
            continue
        line = line.strip()
        if not line:
            continue
        c = line.split('\t')[0]
        if len(c) == 1:
            entries.append(c)

print(f"总字数: {len(entries)}")

# 获取拼音
has_pinyin = []
no_pinyin = []

for i, c in enumerate(entries):
    if i % 10000 == 0:
        print(f"处理中: {i}/{len(entries)}")
    py = pinyin(c, style=Style.NORMAL, heteronym=False)
    if py and py[0] and py[0][0] and py[0][0] != c.lower():
        has_pinyin.append((c, py[0][0]))
    else:
        no_pinyin.append(c)

print(f"\n有读音: {len(has_pinyin)} 字")
print(f"无读音: {len(no_pinyin)} 字")

# 重写文件
with open(dict_file, 'w', encoding='utf-8') as f:
    for line in header:
        f.write(line)
    
    # 先写有读音的，按拼音排序
    for c, py in sorted(has_pinyin, key=lambda x: (x[1], x[0])):
        f.write(f"{c}\t{py}\t0\n")
    
    # 再写无读音的
    for c in no_pinyin:
        f.write(f"{c}\tx\t0\n")

print(f"\n已更新 {dict_file}")
print(f"有读音的字: {len(has_pinyin)} 个")
print(f"无读音的字: {len(no_pinyin)} 个")
