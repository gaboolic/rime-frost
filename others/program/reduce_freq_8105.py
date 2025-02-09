import os
import re
import math

def read_file(file_path):
    list = []
    with open(file_path, 'r', encoding='utf-8') as dict_file:
        for line in dict_file:
            line = line.strip()
            if not '\t' in line or line.startswith("#"):
                list.append(line)
                continue
            line = line.strip()
            print(line)
            params = line.split('\t');
            
            character = params[0]
            encoding = params[1]
            freq = params[2]

            freq = math.ceil((int(freq)/100.0))
            # list.append(f"{character}\t{encoding}")
            list.append(f"{character}\t{encoding}\t{freq}")
                
    return list


final_list = []

cn_dicts_common_list = [ '8105.dict.yaml']


for file_name in cn_dicts_common_list:
    # File paths
    yaml_file_path = os.path.join('cn_dicts', file_name)

    for line in read_file(yaml_file_path):
        final_list.append(line)




# 写入多行数据到文件
with open('cn_dicts_dazhu/8105.dict.yaml', 'w') as file:
    file.writelines('\n'.join(final_list))