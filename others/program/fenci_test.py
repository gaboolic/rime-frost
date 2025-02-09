import os
import re
import math

import jieba

# 精确模式分词
seg_list = jieba.cut("尺八，中国传统乐器，唐宋时期传入日本。竹制，内涂朱砂拌大漆填充（地）外切口，今为五孔（前四后一），属边棱振动气鸣吹管乐器，以管长一尺八寸而得名，其音色苍凉辽阔，又能表现出空灵、恬静的意境。", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

seg_list = jieba.cut("吹管乐器", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

seg_list = jieba.cut("廉而不刿，汉语成语，拼音是：lián ér bù guì，意思是有棱边而不至于割伤别人。比喻为人廉正宽厚。出自《道德经·第五十八章》。", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

exit()
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