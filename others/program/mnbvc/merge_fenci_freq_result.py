import os
import re

def match_chinese(text):
    # 定义正则表达式模式匹配中文字符
    pattern = re.compile("[\u4e00-\u9fa5]{1}")  # 匹配连续两个中文字符
    return re.findall(pattern, text)

word_map = {}
for i in range(0,5):
    read_file = open(f"cn_dicts_dazhu/zhihu_deal_sort{i}.txt", 'r', encoding='utf-8')
    for line in read_file:
        line = line.strip()
        params = line.split("\t")
        word = params[0]
        freq = int(params[1])

        if word in word_map:
            word_map[word] += freq
        else:
            word_map[word] = freq

with open(os.path.join('others', '错字词.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            continue
        wrong_word, correct_word = line.split('\t', 1)
        wrong_freq = word_map.pop(wrong_word, 0)
        if wrong_freq:
            word_map[correct_word] = word_map.get(correct_word, 0) + wrong_freq

# 对word_map按值进行排序
sorted_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)

# 遍历排序后的结果
write_file = open(f"cn_dicts_dazhu/zhihu_deal_sort_merge.txt", 'w', encoding='utf-8')
for item in sorted_word_map:
    if match_chinese(item[0]):
        write_file.write(f"{item[0]}\t{item[1]}\n")