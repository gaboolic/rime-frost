import os
import re
import math

tgz_8105_map = {}
with open(os.path.join('cn_dicts', '8105.dict.yaml'), 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if not '\t' in line or line.startswith("#"):
            continue
        params = line.split('\t');
        character = params[0]
        encode = params[1]
        freq = int(params[2])

        key = character+encode
        tgz_8105_map[key] = 1




# 按音节、按频率排序
# 解析每一行并存储在一个字典中
yinjie_map = {}
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
            key = character+encode
            # if key in tgz_8105_map:
            #     continue

            obj = {}
            obj['character'] = character
            obj['freq'] = freq

            if encode in yinjie_map:
                yinjie_map[encode].append(obj)
            else:
                yinjie_map[encode] = []
                yinjie_map[encode].append(obj)

    print(yinjie_map['a'])
    
    # Step 1: Sort keys alphabetically
    sorted_keys = sorted(yinjie_map.keys())

    # Step 2: Sort values (lists of dictionaries) for each key based on 'freq'
    for key in sorted_keys:
        yinjie_map[key] = sorted(yinjie_map[key], key=lambda x: x['freq'], reverse=True)

    write_file = open('output.txt', 'w', encoding='utf-8')
    # Display the sorted yinjie_map
    for key in sorted_keys:
        # print(f"Key: {key}")
        for item in yinjie_map[key]:
            character = item['character']
            freq = item['freq']
            # print(f"  Character: {item['character']}, Frequency: {item['freq']}")
            line = f'{character}\t{key}\t{freq}\n'
            # print(line)
            write_file.write(line)
    