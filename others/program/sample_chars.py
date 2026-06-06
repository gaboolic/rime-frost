# -*- coding: utf-8 -*-
"""
随机选10个无拼音字，查询汉典
"""
import random

# 读取无拼音的字
no_pinyin_chars = []
with open(r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line == '...':
            continue
        parts = line.split('\t')
        if len(parts) >= 2 and parts[1] == 'x' and len(parts[0]) == 1:
            no_pinyin_chars.append(parts[0])

# 随机选10个
sample = random.sample(no_pinyin_chars, 10)

print("随机选取的10个无拼音字:")
for c in sample:
    code = f'U+{ord(c):04X}'
    print(f"  {c} ({code})")
    print(f"    汉典链接: https://www.zdic.net/hans/{c}")
