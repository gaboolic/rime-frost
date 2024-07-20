import os
import re
import math



def find_english_words(string):
    pattern = r'[A-Za-z]+'  # 匹配由字母组成的单词
    english_words = re.findall(pattern, string)
    return english_words[0]

need_to_reduce_freq_word_map = {}
with open(os.path.join('others', '降频词.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if line.startswith("#"):
            continue
        need_to_reduce_freq_word_map[line] = ''

baijiaxing_word_map = {}
with open(os.path.join('others/program', '百家姓.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if line.startswith("#"):
            continue
        baijiaxing_word_map[line] = ''


char_yin_freq_map = {}
with open(os.path.join('others', '多音字.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            continue
        params = line.split('\t')
        if len(params) != 2:
            continue
        character = params[0]
        encode_freq = params[1]

        encode_freq_params = encode_freq.split(";")
        for encode_freq_param in encode_freq_params:
            if encode_freq_param == "":
                continue
            encode = find_english_words(encode_freq_param)
            freq = encode_freq_param[len(encode):]
            char_yin_freq_map[character+encode] = float(freq)
            

word_freq_map = {}
with open(os.path.join('cn_dicts_dazhu', 'zhihu_deal_sort_merge.txt'), 'r', encoding='utf-8') as dict_file:
# with open(os.path.join('others', '知频.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            continue
        params = line.split('\t');
        character = params[0]
        freq = params[1]
        word_freq_map[character] = freq

cn_dicts_common_list = [ '8105.dict.yaml','41448.dict.yaml','base.dict.yaml','ext.dict.yaml','tencent.dict.yaml']
for file_name in cn_dicts_common_list:
    # File paths
    yaml_file_path = os.path.join('cn_dicts', file_name)

    write_file = open(os.path.join('cn_dicts_dazhu', file_name), 'w')
    with open(yaml_file_path, 'r', encoding='utf-8') as dict_file:
        for line in dict_file:
            line = line.strip()
            if not '\t' in line or line.startswith("#"):
                write_file.write(line+"\n")
                continue

            params = line.split('\t');
            character = params[0]
            encoding = params[1]
            freq = 0
            if character in word_freq_map:
                if character == '薰':
                    print(int(word_freq_map[character]))
                freq = int(word_freq_map[character])
                if character in need_to_reduce_freq_word_map or character +'\t' + encoding in need_to_reduce_freq_word_map:
                    freq = freq//10
                if character == '薰':
                    print(freq)
                    print(character in need_to_reduce_freq_word_map)

            if character+encoding in char_yin_freq_map:
                if character == '她':
                    print("她她她")
                freq = freq * char_yin_freq_map[character+encoding]
                if '41448' in file_name:
                    freq = math.sqrt(freq)
                freq = math.ceil(freq)
            if character == '合':
                print(word_freq_map[character])
                print(line)
                print(f"{character}\t{encoding}\t{freq}\n")
            
            if freq > 0:
                write_file.write(f"{character}\t{encoding}\t{freq}\n")
            elif '8105' in file_name or '41448' in file_name or 'tencent' in file_name:
                write_file.write(f"{character}\t{encoding}\t0\n")

           

