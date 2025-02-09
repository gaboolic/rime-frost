import os
import re
import math

import jieba

# 精确模式分词
seg_list = jieba.cut("耙耙柑", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

# 全模式分词
seg_list = jieba.cut("耙耙柑", cut_all=True)
print("全模式: " + "/ ".join(seg_list))

# 搜索引擎模式分词
seg_list = jieba.cut_for_search("耙耙柑")
print("搜索引擎模式: " + "/ ".join(seg_list))

read_file = open("others/zhihu.txt", 'r', encoding='utf-8')
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
    if deal_count % 1000 == 0:
        print(f"当前处理数量{deal_count}")

print("词频统计完成")
print(len(word_map))
# 对word_map按值进行排序
sorted_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)

# 遍历排序后的结果
write_file = open("others/zhihu_sort.txt", 'w', encoding='utf-8')
for item in sorted_word_map:
    write_file.write(f"{item[0]}\t{item[1]}\n")