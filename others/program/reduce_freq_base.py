import os
import re
import math

import jieba

# 移除频率<=1的词


def read_file(file_path):
    line_list = []
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
                # print(line)
                seg_list = list(jieba.cut(character, cut_all=False))
                if len(seg_list) > 1:
                    line_list.append(line)
                    # print("精确模式: " + "/ ".join(seg_list))
                    pass
                else:
                    # print("精确模式: " + "/ ".join(seg_list))
                    pass

 
            # list.append(f"{character}\t{encoding}")
            #list.append(f"{character}\t{encoding}\t{freq}")
                
    return line_list

def read_file_and_remove(file_path, remove_list):
    line_list = []
    with open(file_path, 'r', encoding='utf-8') as dict_file:
        for line in dict_file:
            line = line.strip()
            if not '\t' in line or line.startswith("#"):
                line_list.append(line)
                continue
            line = line.strip()
            params = line.split('\t');
            
            if line in remove_list:
                pass
            else:
                line_list.append(line)
 
            # list.append(f"{character}\t{encoding}")
            #list.append(f"{character}\t{encoding}\t{freq}")
                
    return line_list


final_list = []

cn_dicts_common_list = [ 'base.dict.yaml']


for file_name in cn_dicts_common_list:
    # File paths
    yaml_file_path = os.path.join('cn_dicts', file_name)

    for line in read_file(yaml_file_path):
        final_list.append(line)


to_add_list = read_file_and_remove(os.path.join('cn_dicts', file_name),final_list)

# 写入多行数据到文件
with open('cn_dicts_dazhu/to_add.dict.yaml', 'w') as file:
    file.writelines('\n'.join(to_add_list))