from pypinyin import pinyin, lazy_pinyin, Style
# pip install pypinyin

print(pinyin('中心'))
print(pinyin(['中心']))
print(lazy_pinyin('中心'))

print(pinyin(['下雨天']))
print(lazy_pinyin('下雨天'))

print(lazy_pinyin('禁着点'))
print(pinyin('禁着点',heteronym=True))


print(pinyin('鸂鶒',heteronym=True))
print(pinyin('寻思',heteronym=True))
print(lazy_pinyin('寻思'))
print(pinyin('寻'))