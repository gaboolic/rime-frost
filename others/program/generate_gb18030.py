# -*- coding: utf-8 -*-
"""
生成 GB18030-2022 汉字字表，去掉 8105 和 41448 中已有的字
GB18030-2022 包含 CJK 统一汉字及其扩展区 (A-H)
"""
from pathlib import Path

def extract_chars(file_path):
    """从字典文件中提取所有字"""
    chars = set()
    in_data = False
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == '...':
                in_data = True
                continue
            if not in_data or line.startswith('#') or not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 1 and len(parts[0]) == 1:
                chars.add(parts[0])
    return chars

def get_gb18030_2022_chars():
    """获取 GB18030-2022 所有汉字 (CJK 统一汉字及扩展区 A-H)"""
    ranges = [
        (0x4E00, 0x9FFF),      # CJK Unified Ideographs
        (0x3400, 0x4DBF),      # CJK Extension A
        (0x20000, 0x2A6DF),    # CJK Extension B
        (0x2A700, 0x2B734),    # CJK Extension C
        (0x2B740, 0x2B81D),    # CJK Extension D
        (0x2B820, 0x2CEA1),    # CJK Extension E
        (0x2CEB0, 0x2EBE0),    # CJK Extension F
        (0x30000, 0x3134A),    # CJK Extension G
        (0x31350, 0x323AF),    # CJK Extension H
    ]
    
    chars = set()
    for start, end in ranges:
        for code in range(start, end + 1):
            try:
                char = chr(code)
                # 验证是否是有效字符
                if char.isprintable():
                    chars.add(char)
            except (ValueError, OverflowError):
                continue
    
    return chars

# 路径
dict_dir = Path(r"D:\vscode\rime-frost\cn_dicts")
output_file = dict_dir / "GB18030-2022.dict.yaml"

# 读取现有字表
print("读取 8105 字表...")
chars_8105 = extract_chars(dict_dir / "8105.dict.yaml")
print(f"  8105: {len(chars_8105)} 字")

print("读取 41448 字表...")
chars_41448 = extract_chars(dict_dir / "41448.dict.yaml")
print(f"  41448: {len(chars_41448)} 字")

existing_chars = chars_8105 | chars_41448
print(f"  合计已有: {len(existing_chars)} 字")

# 获取 GB18030-2022 汉字
print("\n生成 GB18030-2022 汉字列表...")
gb18030_chars = get_gb18030_2022_chars()
print(f"  GB18030-2022 总汉字: {len(gb18030_chars)} 字")

# 去掉已有字
new_chars = gb18030_chars - existing_chars
print(f"  去掉已有后: {len(new_chars)} 字")

# 写入文件
print(f"\n写入 {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Rime dictionary\n")
    f.write("# encoding: utf-8\n")
    f.write("#\n")
    f.write("# GB18030-2022 汉字字表 (去掉 8105 和 41448 中已有的字)\n")
    f.write("#\n")
    f.write("---\n")
    f.write("name: GB18030-2022\n")
    f.write("version: \"2026-06-05\"\n")
    f.write("sort: by_weight\n")
    f.write("...\n")
    
    # 按 Unicode 排序
    sorted_chars = sorted(new_chars, key=lambda c: ord(c))
    for char in sorted_chars:
        f.write(f"{char}\tx\t0\n")

print(f"完成! 共写入 {len(new_chars)} 字")
