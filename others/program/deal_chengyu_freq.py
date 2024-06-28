import os
import string

code_3_word_list = {}
with open("others/program/THUOCL_chengyu.txt", 'r') as file:
    # 逐行读取文件内容
    chengyu_count = 1
    for line in file:
        # 去除行尾的换行符
        line = line.rstrip()
        if line.startswith('#') or '\t' not in line:
            continue
        params = line.split(" 	 ")
        word = params[0]
        # if len(word) != 3:
        #     continue
        code_3_word_list[word] = chengyu_count
        chengyu_count += 1

record_show_map = {}

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


            chengyu_count = code_3_word_list[word]
            code_4 = ''.join(x[0] for x in pinyin.split(" "))
            new_freq = 90000 - chengyu_count

            if int(freq) < 90000:
                need_up_freq_word.append(word)
                write_file.write(f"{word}\t{pinyin}\t{new_freq}\n")
            else:
                write_file.write(line+"\n")

# print(need_up_freq_word)