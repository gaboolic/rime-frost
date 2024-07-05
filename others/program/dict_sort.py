import os
import re
import math

# todo 按音节、按频率排序

# 解析每一行并存储在一个字典中
data = {}
cn_dicts_common_list = [ '8105.dict.yaml']
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
            encode = params[1]
            freq = int(params[2])

            key = character +"\t"+ encode
            data[key] = freq

    # 对频率进行排序
    # 按照频率从高到低排序
    # sorted_data = {k: sorted(v, reverse=True) for k, v in data.items()}
    sorted_word_map = sorted(data.items(), key=lambda x: x[1], reverse=True)
    print(sorted_word_map)
    # 将排序后的结果输出到新文件中
    with open('output.txt', 'w', encoding='utf-8') as file:
        for item in sorted_word_map:
            key = item[0]
            value = item[1]
            
            file.write(f'{key}\t{value}\n')