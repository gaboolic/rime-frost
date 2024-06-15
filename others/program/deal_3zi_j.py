import os
import string

code_3_word_list = {}
with open("others/program/jdh.dict.yaml", 'r') as file:
    # 逐行读取文件内容
    for line in file:
        # 去除行尾的换行符
        line = line.rstrip()
        if line.startswith('#') or '\t' not in line:
            continue
        params = line.split("\t")
        word = params[0]
        if len(word) != 3:
            continue
        code_3_word_list[word] = 1

need_up_freq_word = []
jianpin_word_map = {}
file_list = ['base.dict.yaml','ext.dict.yaml']
for file in file_list:
    file_name  = os.path.join('cn_dicts', file)
    write_file_name  = os.path.join('cn_dicts_dazhu', file)
    write_file = open(write_file_name, "w")
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                write_file.write(line+"\n")
                continue
            params = line.split("\t")
            word = params[0]
            pinyin = params[1]
            freq = params[2]
            
            if word not in code_3_word_list:
                write_file.write(line+"\n")
                continue

            if int(freq) < 50000:
                need_up_freq_word.append(word)
                write_file.write(word+"\t"+pinyin+"\t49999\n")
            else:
                write_file.write(line+"\n")
