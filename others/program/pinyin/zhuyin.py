import os
import string
from collections import OrderedDict 
from pypinyin import pinyin, lazy_pinyin, Style
# pip install pypinyin

jianpin_word_map = {}

# file_names = ['literature.dict.yaml','computer.dict.yaml']
# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
file_names = os.listdir("cn_dicts_cell")

# 打印出所有找到的文件名
for file_name in file_names:
    print(file_name)
    read_file_name = os.path.join('cn_dicts_cell', file_name)

    
    word_map = OrderedDict()
    with open(read_file_name, 'r') as file:

        start = False
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line == '...':
                start = True
                word_map[line]=''
                continue
            if not start:
                word_map[line]=''
                continue

            # if line.startswith("#") or '\t' in line:
            #     word_map[line]=''
            #     continue

            if line.startswith("#"):
                word_map[line]=''
                continue

            params = line.split("\t")
            if len(params) == 3:
                word_map[line]=''
                continue
            word = params[0]
            #freq = params[1]
            print(word)
            pinyin_list = lazy_pinyin(word)
            pinyin = ' '.join(pinyin_list)
            #print(pinyin)
            new_line = word +"\t" + pinyin + "\t0"
            print(new_line)
            word_map[new_line]=''
    
    write_file_name = os.path.join('cn_dicts_cell', file_name)
    write_file = open(write_file_name, 'w')

    for word in word_map:
        write_file.write(word+"\n")


