# -*- coding: utf-8 -*-
"""
从 Unicode Unihan 数据库获取读音，更新 GB18030-2022.dict.yaml
"""
import urllib.request
import zipfile
import os
import tempfile

# 下载 Unihan.zip
unihan_url = "https://www.unicode.org/Public/UNIDATA/Unihan.zip"
temp_dir = tempfile.mkdtemp()
zip_path = os.path.join(temp_dir, "Unihan.zip")

print("下载 Unihan.zip...")
urllib.request.urlretrieve(unihan_url, zip_path)
print("下载完成")

# 解压
print("解压...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

# 读取 Unihan_Readings.txt 中的 kMandarin 数据
readings_file = os.path.join(temp_dir, "Unihan_Readings.txt")
mandarin_readings = {}

print("读取 kMandarin 数据...")
with open(readings_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 3 and parts[1] == 'kMandarin':
            # 格式: U+4E00	kMandarin	yī
            code_point = parts[0]
            pinyin = parts[2]
            
            # 转换 Unicode 编码为字符
            if code_point.startswith('U+'):
                try:
                    char = chr(int(code_point[2:], 16))
                    mandarin_readings[char] = pinyin.lower()
                except (ValueError, OverflowError):
                    continue

print(f"读取到 {len(mandarin_readings)} 个字的 kMandarin 读音")

# 读取 GB18030-2022 字典
dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'

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
unihan_count = 0

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
    
    # 检查 Unihan 是否有读音
    if len(char) == 1 and char in mandarin_readings:
        py = mandarin_readings[char]
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

# 清理临时文件
import shutil
shutil.rmtree(temp_dir)

print(f"\n添加 Unihan 读音: {unihan_count} 个字")
print("完成!")
