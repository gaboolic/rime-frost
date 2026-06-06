# -*- coding: utf-8 -*-
from pypinyin import pinyin, Style

with open(r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml', 'r', encoding='utf-8') as f:
    chars = []
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line == '...':
            continue
        c = line.split('\t')[0]
        if len(c) == 1:
            chars.append(c)

# 检查有读音的字
has_pinyin = []
no_pinyin = []

for c in chars[:2000]:  # 检查前2000个
    py = pinyin(c, style=Style.NORMAL, heteronym=False)
    if py and py[0] and py[0][0] and py[0][0] != c.lower():
        has_pinyin.append((c, py[0][0]))
    else:
        no_pinyin.append(c)

print(f'检查前 {min(2000, len(chars))} 个字:')
print(f'有读音: {len(has_pinyin)} 个')
print(f'无读音或返回字本身: {len(no_pinyin)} 个')
print()
print('有读音的字示例 (前50):')
for c, py in has_pinyin[:50]:
    print(f'  {c} - {py}')
