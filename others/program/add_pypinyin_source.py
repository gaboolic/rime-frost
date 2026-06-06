# -*- coding: utf-8 -*-
"""
为 GB18030-2022 中无拼音的字添加 pypinyin 读音
"""
from pypinyin import pinyin, Style

dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'

# 读取文件
with open(dict_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找出数据行
header_end = 0
for i, line in enumerate(lines):
    if line.strip() == '...':
        header_end = i + 1
        break

header = lines[:header_end]
data_lines = lines[header_end:]

# 处理数据行
updated_lines = []
pypinyin_count = 0

for line in data_lines:
    line = line.strip()
    if not line:
        continue
    
    parts = line.split('\t')
    if len(parts) < 2:
        updated_lines.append(line)
        continue
    
    char = parts[0]
    pinyin_val = parts[1]
    
    # 如果已经有拼音(不是x)，保留原样
    if pinyin_val != 'x':
        updated_lines.append(line)
        continue
    
    # 检查 pypinyin 是否有读音
    if len(char) == 1:
        py = pinyin(char, style=Style.NORMAL, heteronym=False)
        if py and py[0] and py[0][0] and py[0][0] != char.lower():
            new_line = f"{char}\t{py[0][0]}\t0\t# pypinyin"
            updated_lines.append(new_line)
            pypinyin_count += 1
        else:
            updated_lines.append(line)
    else:
        updated_lines.append(line)

# 写入文件
with open(dict_file, 'w', encoding='utf-8') as f:
    for line in header:
        f.write(line)
    for line in updated_lines:
        f.write(line + '\n')

print(f"添加 pypinyin 读音: {pypinyin_count} 个字")
print(f"完成!")
