import os
import string


jianpin_word_map = {}
file_list = ['base.dict.yaml','ext.dict.yaml']

# 使用 os 模块中的 listdir 函数列出指定文件夹中的所有文件和子目录
file_names = os.listdir("cn_dicts_cell")

# 打印出所有找到的文件名
for file_name in file_names:
    print(file_name)
    file_name = os.path.join('cn_dicts_cell', file_name)
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            # 去除行尾的换行符
            line = line.rstrip()
            if line.startswith('#') or '\t' not in line:
                continue
            params = line.split("\t")
            word = params[0]
            encode = params[1]
            
            pinyin = params[1]
            shengmus = pinyin.split(" ")

            word_freq = {}
            word_freq["word"] = word
            # word_freq["freq"] = freq

            key = word + encode
            if key not in jianpin_word_map:
                jianpin_word_map[key] = word_freq
            else:

                print("重复"+word)
                print(jianpin_word_map[key])

print(jianpin_word_map['什么shen me'])

