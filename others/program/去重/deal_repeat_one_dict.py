import os
import string
from collections import OrderedDict 

jianpin_word_map = {}

# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
file_names = os.listdir("cn_dicts_cell")

# 打印出所有找到的文件名
for file_name in file_names:
    print(file_name)
    read_file_name = os.path.join('cn_dicts_cell', file_name)

    
    word_map = OrderedDict()
    with open(read_file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            
            
            if line in word_map:
                continue
            word_map[line]=''
    
    write_file_name = os.path.join('cn_dicts_cell', file_name)
    write_file = open(write_file_name, 'w')

    for word in word_map:
        write_file.write(word+"\n")


