import os
import string

def is_all_chinese(text):
    for char in text:
        if not '\u4e00' <= char <= '\u9fff':
            return False
    return True

word_map = {}
# file_list = ['ngram_1_frequencies.txt','ngram_2_frequencies.txt','ngram_3_frequencies.txt']
file_list = ['ngram_2_frequencies.txt','ngram_3_frequencies.txt']

for file in file_list:
    file_name = os.path.join('cn_dicts_dazhu', file)
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                continue
            params = line.split("\t")

            word = params[0]
            word = word.replace(" ", "")
            word = word.replace("<s>", "")

            # 句末符号
            word = word.replace("</s>", "$") 
        
            
            if len(params) == 3:
                freq = params[2]
            else:
                freq = params[1]
            
            if len(word) <= 1 or len(word) > 8:
                continue
            word_map[word] = freq

write_file_name = os.path.join('cn_dicts_dazhu', "merge_2_3.txt")
write_file = open(write_file_name, 'w')
for word in word_map:
    write_file.write(word+"\t"+word_map[word]+"\n")
