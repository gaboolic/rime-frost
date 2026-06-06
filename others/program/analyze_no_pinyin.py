# -*- coding: utf-8 -*-
"""
分析 GB18030-2022 中无拼音字的 Unicode 区块分布
"""

dict_file = r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml'

# 读取无拼音的字
no_pinyin_chars = []
with open(dict_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line == '...':
            continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[1] == 'x' and len(parts[0]) == 1:
            no_pinyin_chars.append(parts[0])

print(f"无拼音字总数: {len(no_pinyin_chars)}")

# 按 Unicode 区块分类
ranges = {
    'CJK 基本区 (U+4E00-9FFF)': (0x4E00, 0x9FFF),
    'CJK 扩展A (U+3400-4DBF)': (0x3400, 0x4DBF),
    'CJK 扩展B (U+20000-2A6DF)': (0x20000, 0x2A6DF),
    'CJK 扩展C (U+2A700-2B734)': (0x2A700, 0x2B734),
    'CJK 扩展D (U+2B740-2B81D)': (0x2B740, 0x2B81D),
    'CJK 扩展E (U+2B820-2CEA1)': (0x2B820, 0x2CEA1),
    'CJK 扩展F (U+2CEB0-2EBE0)': (0x2CEB0, 0x2EBE0),
    'CJK 扩展G (U+30000-3134A)': (0x30000, 0x3134A),
    'CJK 扩展H (U+31350-323AF)': (0x31350, 0x323AF),
}

for name, (start, end) in ranges.items():
    count = sum(1 for c in no_pinyin_chars if start <= ord(c) <= end)
    if count > 0:
        print(f"{name}: {count} 个")

# 检查基本区的字
basic_chars = [c for c in no_pinyin_chars if 0x4E00 <= ord(c) <= 0x9FFF]
if basic_chars:
    print(f"\nCJK 基本区无拼音字示例 (前20):")
    print(' '.join(basic_chars[:20]))
