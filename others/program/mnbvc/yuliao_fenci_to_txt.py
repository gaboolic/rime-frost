import os
import re
import math
import re

import jieba

# 此脚本是把txt格式的文件进行分词，词和词之间加空格，逗号和句号替换成换行
def is_all_punctuation(text):
    # 定义一个正则表达式模式，匹配所有标点符号
    pattern = r'^[^\w\s]+$'
    # 使用 re.match() 函数判断字符串是否完全由标点符号组成
    return bool(re.match(pattern, text))

def replace_punctuation_with_newline(text):
    # 定义需要替换的标点符号的正则表达式模式
    punctuation_pattern = r'[.,!?;:。，！？；：]'
    #print("pre:"+text)
    # 使用 re.sub() 函数将符合正则表达式的字符替换为换行符
    replaced_text = re.sub(punctuation_pattern, '\n', text).strip()
    #print("after "+replaced_text)
    return replaced_text

def match_chinese(text):
    # 定义正则表达式模式匹配中文字符
    pattern = re.compile("[\u4e00-\u9fa5]{1}")  # 匹配连续两个中文字符
    return re.findall(pattern, text)

jieba.load_userdict('cn_dicts_dazhu/custom_fenci_dict.txt')
# 精确模式分词
seg_list = jieba.cut("耙耙柑", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

seg_list = jieba.cut("廉而不刿，汉语成语，拼音是：lián ér bù guì，意思是有棱边而不至于割伤别人。比喻为人廉正宽厚。出自《道德经·第五十八章》。", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

for i in range(0,5):
    print(i)
    read_file = open(f"cn_dicts_dazhu/zhihu_deal{i}.txt", 'r', encoding='utf-8')

    # 分词后的结果
    write_file = open(f"cn_dicts_dazhu/zhihu_deal_fenci{i}.txt", 'w', encoding='utf-8')

    word_map = {}
    deal_count = 0
    for line in read_file:
        line = line.strip()
        if line == '':
            continue
        new_lines = replace_punctuation_with_newline(line).split("\n")
        for new_line in new_lines:
            new_line = new_line.strip()
            if new_line == '':
                continue
            seg_list = jieba.cut(new_line, cut_all=False)
            
            text = ""
            for seg in seg_list:
                seg = seg.strip()
                if seg in '，。？：！“”、；,.;:\'…[]【】《》<>{}-?!' or is_all_punctuation(seg):
                    continue
                text += seg+" "
                
            text = text[0:-1]
            # print(text)
            if text == '':
                continue
            write_file.write(text)
            write_file.write("\n")

        deal_count += 1
        if deal_count % 10000 == 0:
            print(f"当前处理数量{deal_count}")
            #break
        
        # if deal_count >=200:
        #     break

    print("词频统计完成")
    print(len(word_map))

# bin/lmplz -o 3 --text zhihu_deal_fenci0.txt --arpa MyModel/zhi0709.arpa --prune 0 50 100
