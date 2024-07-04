import os
import string

word_map = {}
# file_list = ['base.dict.yaml','ext.dict.yaml']
file_list = ['8105.dict.yaml']
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

            if word in word_map:
                #print(line)
                word_map[word].append(pinyin+"-"+freq)
            else:
                word_map[word] = []
                word_map[word].append(pinyin+"-"+freq)
print(len(word_map))
# 遍历word_map 找到超过2个读音的词
# Iterate over word_map

write_file_name  = os.path.join('cn_dicts_dazhu', "多音字.txt")
write_file = open(write_file_name, "w")
for word, pronunciations in word_map.items():
    # print(pronunciations)
    if len(pronunciations) >= 2:
        write_file.write(f"{word}	{pronunciations}\n")

