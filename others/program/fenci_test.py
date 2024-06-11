import os
import re
import math

import jieba

# 精确模式分词
seg_list = jieba.cut("耙耙柑", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

# 全模式分词
seg_list = jieba.cut("耙耙柑", cut_all=True)
print("全模式: " + "/ ".join(seg_list))

# 搜索引擎模式分词
seg_list = jieba.cut_for_search("耙耙柑")
print("搜索引擎模式: " + "/ ".join(seg_list))


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

            if len(character) >= 2 and len(character) <= 4:
                # print(line)
                seg_list = list(jieba.cut(character, cut_all=False))

                # 分词>1
                if len(seg_list) != 1:
                    line_list.append(line)
                    # print("精确模式: " + "/ ".join(seg_list))
                    pass
                else:
                    # print("精确模式: " + "/ ".join(seg_list))
                    pass

            #print(line)
            # list.append(f"{character}\t{encoding}")
            #list.append(f"{character}\t{encoding}\t{freq}")
                
    return line_list



final_list = []

cn_dicts_common_list = [ 'tencent.dict.yaml']


for file_name in cn_dicts_common_list:
    # File paths
    yaml_file_path = os.path.join('cn_dicts', file_name)

    for line in read_file(yaml_file_path):
        final_list.append(line)



# 写入多行数据到文件
with open('cn_dicts_dazhu/to_add_tencent_分词无.dict.yaml', 'w') as file:
    for line in final_list:
        print(line)
        file.write(line + '\n')