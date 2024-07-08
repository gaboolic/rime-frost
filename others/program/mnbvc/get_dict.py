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
for i in range(0,5):
    file_name = os.path.join(os.path.expanduser("~/mnbvc"),f'{i}.jsonl') # 知乎 https://huggingface.co/datasets/liwu/MNBVC/tree/main/qa/20230196/zhihu
    write_file_name = os.path.join('cn_dicts_dazhu', f"zhihu_deal{i}.txt")
    write_file = open(write_file_name, 'w')
    line_count = 0
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
            
            q_content = data['问'].strip()
            a_content = data['答'].strip()
            if q_content == '从小缺爱的女孩长大后生活有多辛苦？':
                print(a_content)
                print(line)
            write_file.write(q_content)
            write_file.write("\n")
            write_file.write(a_content)
            write_file.write("\n")
            total_count += len(q_content)
            total_count += len(a_content)
        print(f"line_count {line_count}")

print(total_count)
        
