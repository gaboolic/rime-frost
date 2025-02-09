import os
import re
import string
import json

# mnbvc liwu_253874_com.jsonl
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'undl_01.jsonl') # 通用平行
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'liwu_253874_com.jsonl') # 里屋论坛
file_name = os.path.join(os.path.expanduser("~/Downloads"),'46.jsonl') #维基
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'oscar_202201.part_0075.jsonl') # 通用文本
# file_name = os.path.join(os.path.expanduser("~/mnbvc"),'pkuholefromarchive_0.jsonl') # chatgpt zhidao

count = 0
with open(file_name, 'r') as file:


    # 逐行读取文件内容
    for line in file:
        line = line.strip()
        if len(line) == 0:
            continue

        print(line)
        count+=1

        
