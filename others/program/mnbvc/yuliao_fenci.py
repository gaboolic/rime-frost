import heapq
import os
import re
from collections import Counter

import jieba

# 定义文件路径
MNBVC_SOURCE_TXT_PATH = "cn_dicts_dazhu"

# 加载自定义词典
jieba.load_userdict('cn_dicts_dazhu/custom_fenci_dict.txt')
# 精确模式分词
seg_list = jieba.cut("耙耙柑", cut_all=False)
print("精确模式: " + "/ ".join(seg_list))

seg_list = jieba.cut(
    "廉而不刿，汉语成语，拼音是：lián ér bù guì，意思是有棱边而不至于割伤别人。比喻为人廉正宽厚。出自《道德经·第五十八章》。",
    cut_all=False)
print("精确模式: " + "/ ".join(seg_list))


def scan_file(path):
    """
    遍历文件夹下所有文件
    :param path:
    :return:
    """
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def match_chinese(text):
    """
    匹配中文字符
    :param text:
    :return:
    """
    # 定义正则表达式模式匹配中文字符
    pattern = re.compile("[\u4e00-\u9fa5]{1}")  # 匹配连续两个中文字符
    return re.findall(pattern, text)


if __name__ == '__main__':
    for file_name in scan_file(os.path.expanduser(MNBVC_SOURCE_TXT_PATH)):
        # 定义匹配的正则表达式模式
        pattern = r'zhihu_deal(\d+).txt'
        # 使用正则表达式模式匹配文件名
        match = re.search(pattern, os.path.basename(file_name))
        if not match:
            continue
        number = match.group(1)
        print(file_name)
        read_file = open(file_name, 'r', encoding='utf-8')
        word_map = {}
        word_counter = Counter()
        deal_count = 0
        for line in read_file:
            line = line.strip()
            # 使用精确模式分词
            seg_list = jieba.lcut(line, cut_all=False)
            for seg in seg_list:
                if seg == '的了':
                    print(line)
                if match_chinese(seg):
                    word_counter[seg] += 1
            deal_count += 1
            if deal_count % 10000 == 0:
                print(f"当前处理数量{deal_count}")

        # 遍历排序后的结果
        sorted_words = heapq.nlargest(len(word_counter), word_counter, key=word_counter.get)
        with open("{save_path}/zhihu_deal_sort{i}.txt".format(save_path=MNBVC_SOURCE_TXT_PATH, i=number), 'w',
                  encoding='utf-8') as write_file:
            for word in sorted_words:
                write_file.write(f"{word}\t{word_counter[word]}\n")