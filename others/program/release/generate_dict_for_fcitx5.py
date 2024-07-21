import os
import string

top_freq = 15184272
word_map = {}
file_list = ['base.dict.yaml','ext.dict.yaml']
for file in file_list:
    file_name = os.path.join('cn_dicts', file)
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                continue
            params = line.split("\t")
            word = params[0]
            pinyin = params[1]
            pinyin = pinyin.replace(" ","'")
            if len(params) == 3:
                freq = int(params[2])
            else:
                continue

            key = word +" " + pinyin
            if key in word_map:
                continue

            word_map[key] = freq/top_freq

# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
file_list = os.listdir("cn_dicts_cell")
for file in file_list:
    file_name = os.path.join('cn_dicts_cell', file)
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                continue
            params = line.split("\t")
            word = params[0]
            pinyin = params[1]
            pinyin = pinyin.replace(" ","'")
            if len(params) == 3:
                freq = int(params[2])
            else:
                continue

            key = word +" " + pinyin
            if key in word_map:
                continue

            word_map[key] = freq/top_freq

write_file_name = os.path.join('', "frost_dict_for_fcitx5.txt")
write_file = open(write_file_name, 'w')
for word in word_map:
    write_file.write(f"{word} {word_map[word]}\n")

    # write_file.write(word+" "+word_map[word]+"\n")
