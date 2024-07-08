import os
import re
import math
import re

import jieba

def match_chinese(text):
    # 定义正则表达式模式匹配中文字符
    pattern = re.compile("[\u4e00-\u9fa5]{1}")  # 匹配连续两个中文字符
    return re.findall(pattern, text)

jieba.load_userdict('cn_dicts_dazhu/custom_fenci_dict.txt')
# 精确模式分词
seg_list = jieba.cut("耙耙柑", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))


seg_list = jieba.cut("廉而不刿，汉语成语，拼音是：lián ér bù guì，意思是有棱边而不至于割伤别人。比喻为人廉正宽厚。出自《道德经·第五十八章》。", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))


for i in range(0,78):
    if os.path.exists(f"cn_dicts_dazhu/wiki_deal_sort{i}.txt"):
        print(f"已有cn_dicts_dazhu/wiki_deal_sort{i}.txt")
        continue

    print(f"cn_dicts_dazhu/wiki_deal{i}.txt")
    read_file = open(f"cn_dicts_dazhu/wiki_deal{i}.txt", 'r', encoding='utf-8')
    word_map = {}
    deal_count = 0
    for line in read_file:
        line = line.strip()
        seg_list = jieba.cut(line, cut_all=False)
        for seg in seg_list:
            if seg in word_map:
                word_map[seg] += 1
            else:
                word_map[seg] = 1
        deal_count += 1
        if deal_count % 10000 == 0:
            print(f"当前处理数量{deal_count}")
            #break

    print("词频统计完成")
    print(len(word_map))
    # 对word_map按值进行排序
    sorted_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)

    # 遍历排序后的结果
    write_file = open(f"cn_dicts_dazhu/wiki_deal_sort{i}.txt", 'w', encoding='utf-8')
    for item in sorted_word_map:
        if match_chinese(item[0]):
            write_file.write(f"{item[0]}\t{item[1]}\n")