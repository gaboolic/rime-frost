import os
import re
import math
import re

import jieba


# 遍历排序后的结果
write_file = open(f"cn_dicts_dazhu/zhihu_deal_fenci_merge.txt", 'w', encoding='utf-8')
word_map = {}
for i in range(0,5):
    read_file = open(f"cn_dicts_dazhu/zhihu_deal_fenci{i}.txt", 'r', encoding='utf-8')
    for line in read_file:
        line = line.strip()
        write_file.write(line)
        write_file.write("\n")