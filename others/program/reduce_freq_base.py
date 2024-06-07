import os
import re
import math

def read_file(file_path):
    list = []
    with open(file_path, 'r', encoding='utf-8') as dict_file:
        for line in dict_file:
            line = line.strip()
            if not '\t' in line or line.startswith("#"):
                #list.append(line)
                continue
            line = line.strip()
            params = line.split('\t');
            
            character = params[0]
            encoding = params[1]
            freq = params[2]

            if int(freq) <= 1 and len(character) == 2:
                print(line)
                list.append(line)
 
            # list.append(f"{character}\t{encoding}")
            #list.append(f"{character}\t{encoding}\t{freq}")
                
    return list


final_list = []

cn_dicts_common_list = [ 'base.dict.yaml']


for file_name in cn_dicts_common_list:
    # File paths
    yaml_file_path = os.path.join('cn_dicts', file_name)

    for line in read_file(yaml_file_path):
        final_list.append(line)




# 写入多行数据到文件
with open('cn_dicts_dazhu/base.dict.yaml', 'w') as file:
    file.writelines('\n'.join(final_list))