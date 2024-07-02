import os
import re
import math

word_freq_map = {}
with open(os.path.join('others', '知频.txt'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            continue
        params = line.split('\t');
        character = params[0]
        freq = params[1]
        word_freq_map[character] = freq

cn_dicts_common_list = [ '8105.dict.yaml','base.dict.yaml','ext.dict.yaml']
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
                freq = int(word_freq_map[character])
            
            if freq > 0:
                write_file.write(f"{character}\t{encoding}\t{freq}\n")

