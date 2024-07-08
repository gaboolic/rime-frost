import os
import re
import string
import json

# mnbvc liwu_253874_com.jsonl
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'undl_01.jsonl') # 通用平行
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'liwu_253874_com.jsonl') # 里屋论坛
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'46.jsonl') #维基
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'oscar_202201.part_0075.jsonl') # 通用文本

total_count = 0
for i in range(0,78):
    file_name = os.path.join(os.path.expanduser("~/mnbvc_wiki"),f'{i}.jsonl') # wiki
    write_file_name = os.path.join('cn_dicts_dazhu', f"wiki_deal{i}.txt")
    write_file = open(write_file_name, 'w')
    line_count = 0
    if not os.path.exists(file_name):
        continue
    with open(file_name, 'r') as file:
        # 逐行读取文件内容
        for line in file:
            line_count += 1
            line = line.strip()
            if len(line) == 0:
                continue

            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError:
                print("JSONDecodeError")
                print(line)
                continue
            for d in data['段落']:
                content = d['内容']
                write_file.write(content)
                write_file.write("\n")
                total_count += len(content)
        print(f"line_count {line_count}")

print(total_count)
        
