import os
import re
import string
import json

read_file = open(os.path.join('cn_dicts_dazhu', "zhihu_deal_sort_merge.txt"), 'r')
write_file = open(os.path.join('cn_dicts_dazhu', "知频.txt"), 'w')

read_file = open(os.path.join('cn_dicts_dazhu', "wiki_deal_sort_merge.txt"), 'r')
write_file = open(os.path.join('cn_dicts_dazhu', "维基频-dazhu.txt"), 'w')
# 逐行读取文件内容
for line in read_file:
    line = line.strip()
    params = line.split("\t")

    write_file.write(f"{params[1]}\t{params[0]}\n")
