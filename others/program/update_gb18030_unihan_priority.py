# -*- coding: utf-8 -*-
"""
用 Unihan 优先更新 GB18030-2022，替换虚拟读音
"""
import urllib.request
import zipfile
import os
import tempfile

# 下载 Unihan.zip
unihan_url = 'https://www.unicode.org/Public/UNIDATA/Unihan.zip'
temp_dir = tempfile.mkdtemp()
zip_path = os.path.join(temp_dir, 'Unihan.zip')

print('下载 Unihan.zip...')
urllib.request.urlretrieve(unihan_url, zip_path)

# 解压
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

# 读取 kMandarin 数据
readings_file = os.path.join(temp_dir, 'Unihan_Readings.txt')
mandarin_data = {}

print('读取 kMandarin...')
with open(readings_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 3 and parts[1] == 'kMandarin':
            code_point = parts[0]
            pinyin = parts[2]
            if code_point.startswith('U+'):
                try:
                    char = chr(int(code_point[2:], 16))
                    mandarin_data[char] = pinyin.lower()
                except:
                    pass

print(f'Unihan kMandarin: {len(mandarin_data)} 个字')

# 读取 GB18030-2022 字典
dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'

with open(dict_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_end = 0
for i, line in enumerate(lines):
    if line.strip() == '...':
        header_end = i + 1
        break

header = lines[:header_end]
data_lines = lines[header_end:]

# 处理数据行
updated_lines = []
unihan_count = 0
ziang_to_unihan = 0

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
    
    # 如果已有真实拼音，保留
    if pinyin_val not in ('x', 'ziang'):
        updated_lines.append(line)
        continue
    
    # 检查 Unihan 是否有读音
    if len(char) == 1 and char in mandarin_data:
        py = mandarin_data[char]
        if pinyin_val == 'ziang':
            ziang_to_unihan += 1
        new_line = f"{char}\t{py}\t0\t# Unihan"
        updated_lines.append(new_line)
        unihan_count += 1
    else:
        updated_lines.append(line)

# 写入文件
with open(dict_file, 'w', encoding='utf-8') as f:
    for line in header:
        f.write(line)
    for line in updated_lines:
        f.write(line + '\n')

# 清理
import shutil
shutil.rmtree(temp_dir)

print(f'\\n用 Unihan 更新: {unihan_count} 个字')
print(f'其中从 ziang 替换为 Unihan: {ziang_to_unihan} 个')
print('完成!')
