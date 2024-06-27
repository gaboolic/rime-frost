import os
import re


# read_file = open("others/zhihu.json", 'r', encoding='utf-8')
# write_file = open("others/zhihu.txt", 'w', encoding='utf-8')
# file_content = read_file.read()
# print(len(file_content))

# # 使用正则表达式提取所有 "q_title" 字段的内容
# q_titles = re.findall(r'"q_title" : "(.*?)",', file_content)
# q_contents = re.findall(r'"q_content" : "(.*?)",', file_content)
# a_content = re.findall(r'"a_content" : "(.*?)",', file_content)

# for title in q_titles:
#     title = title.strip()
#     write_file.write(title+"\n")

# for title in q_contents:
#     title = title.strip()
#     write_file.write(title+"\n")

# for title in a_content:
#     title = title.strip()
#     write_file.write(title+"\n")

import string

def has_punctuation(text):
    for char in text:
        if char in string.punctuation:
            return True
    return False

def match_chinese(text):
    # 定义正则表达式模式匹配中文字符
    pattern = re.compile("[\u4e00-\u9fa5]{1}")  # 匹配连续两个中文字符
    return re.findall(pattern, text)


read_file = open("others/zhihu_sort.txt", 'r', encoding='utf-8')
write_file = open("others/zhihu_sort_deal3.txt", 'w', encoding='utf-8')
for line in read_file:
    line = line.strip()
    if match_chinese(line) and len(line.split("\t")[0]) == 3:
        write_file.write(line+"\n")
