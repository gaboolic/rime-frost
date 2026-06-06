# -*- coding: utf-8 -*-
"""
将无拼音字的读音改为虚拟读音 ziang
"""

dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'

# 读取文件
with open(dict_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到数据开始位置
header_end = 0
for i, line in enumerate(lines):
    if line.strip() == '...':
        header_end = i + 1
        break

header = lines[:header_end]
data_lines = lines[header_end:]

# 处理数据行
updated_lines = []
ziang_count = 0

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
    
    # 改为虚拟读音 ziang
    new_line = f"{char}\tziang\t0\t# 虚拟读音"
    updated_lines.append(new_line)
    ziang_count += 1

# 写入文件
with open(dict_file, 'w', encoding='utf-8') as f:
    for line in header:
        f.write(line)
    for line in updated_lines:
        f.write(line + '\n')

print(f"设置虚拟读音 ziang: {ziang_count} 个字")
print("完成!")
