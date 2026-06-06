# -*- coding: utf-8 -*-
"""
用 rime-moran 的拼音更新 GB18030-2022.dict.yaml
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
                moran_chars[char] = pinyin  # 取第一个读音

print(f"读取 rime-moran: {len(moran_chars)} 个字")

# 读取 GB18030-2022 字典
dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'
header = []
entries = []

with open(dict_file, 'r', encoding='utf-8') as f:
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
        parts = line.split('\t')
        if len(parts) >= 1:
            char = parts[0]
            if len(char) == 1:
                entries.append(char)

print(f"读取 GB18030-2022: {len(entries)} 个字")

# 更新并写入文件
updated = 0
with open(dict_file, 'w', encoding='utf-8') as f:
    for line in header:
        f.write(line)
    
    # 有拼音的字按拼音排序
    has_pinyin = []
    no_pinyin = []
    
    for c in entries:
        if c in moran_chars:
            has_pinyin.append((c, moran_chars[c]))
        else:
            no_pinyin.append(c)
    
    # 写入有拼音的
    for c, py in sorted(has_pinyin, key=lambda x: (x[1], x[0])):
        f.write(f"{c}\t{py}\t0\t# rime-moran\n")
        updated += 1
    
    # 写入无拼音的
    for c in no_pinyin:
        f.write(f"{c}\tx\t0\n")

print(f"\n已更新: {updated} 个字")
print(f"无拼音: {len(no_pinyin)} 个字")
print(f"完成!")
