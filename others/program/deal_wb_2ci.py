import os
import re
import string


jianpin_word_map = {}
file_list = ['base.dict.yaml']
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
            freq = params[2]
            
            if len(word) != 2:
                continue
            pinyin = params[1]
            shengmus = pinyin.split(" ")
            jianpin = shengmus[0][0] + shengmus[1][0]

            word_freq = {}
            word_freq["word"] = word
            word_freq["freq"] = freq
            word_freq["jianpin"] = jianpin
            if word not in jianpin_word_map:
                jianpin_word_map[word] = word_freq

print(jianpin_word_map['什么'])

with open("others/2字词频表.txt", 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            #list.append(line)
            continue
        line = line.strip()
        params = line.split('\t');
        
        character = params[0]
        freq = params[1]
        freq = (''.join(re.findall(r'\d+', freq)))
        if int(freq) < 3000:
            break

        if character not in jianpin_word_map:
            continue
        jianpin = jianpin_word_map[character]
        print(character+"\t"+jianpin['jianpin'])
        

        #print(line)
        # list.append(f"{character}\t{encoding}")
        #list.append(f"{character}\t{encoding}\t{freq}")
            
