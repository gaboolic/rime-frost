import os
import string
from collections import OrderedDict


base_word_map = {}
file_list = ['8105.dict.yaml','41448.dict.yaml','base.dict.yaml','ext.dict.yaml']
for file_name in file_list:
    file_name = os.path.join('cn_dicts', file_name)
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                continue
            params = line.split("\t")
            word = params[0]
            encode = params[1]


            key = word + encode
            if key not in base_word_map:
                base_word_map[key] = '1'

print(len(base_word_map))

# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
file_names = os.listdir("cn_dicts_cell")


# 打印出所有找到的文件名
for file_name in file_names:
    print("- cn_dicts_cell/"+file_name)
    read_file_name = os.path.join('cn_dicts_cell', file_name)

    word_map = OrderedDict()
    with open(read_file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                word_map[line]=''
                continue
            params = line.split("\t")
            word = params[0]
            encode = params[1]
            
            key = word + encode
            if key not in base_word_map:
                word_map[line]=''
    
    write_file_name = os.path.join('cn_dicts_cell', file_name)
    write_file = open(write_file_name, 'w')

    for word in word_map:
        write_file.write(word+"\n")

