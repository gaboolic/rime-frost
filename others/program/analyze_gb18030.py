# -*- coding: utf-8 -*-
with open(r'D:\vscode\rime-frost\cn_dicts\GB18030-2022.dict.yaml', 'r', encoding='utf-8') as f:
    chars = []
    for line in f:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line == '...':
            continue
        c = line.split('\t')[0]
        if len(c) == 1:
            chars.append(c)

# 按 Unicode 区块分类
basic = [c for c in chars if 0x4E00 <= ord(c) <= 0x9FFF]
ext_a = [c for c in chars if 0x3400 <= ord(c) <= 0x4DBF]
ext_b = [c for c in chars if 0x20000 <= ord(c) <= 0x2A6DF]
ext_other = [c for c in chars if ord(c) > 0x2A6DF]

print(f'总字数: {len(chars)}')
print(f'基本区 (U+4E00-9FFF): {len(basic)} 字 - 这些通常有读音')
print(f'扩展A (U+3400-4DBF): {len(ext_a)} 字')
print(f'扩展B (U+20000-2A6DF): {len(ext_b)} 字')
print(f'其他扩展: {len(ext_other)} 字')
print()
print('基本区前50个示例:')
print(' '.join(basic[:50]))
