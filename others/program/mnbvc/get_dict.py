import os
import re
import json
import time

# mnbvc liwu_253874_com.jsonl
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'undl_01.jsonl') # 通用平行
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'liwu_253874_com.jsonl') # 里屋论坛
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'46.jsonl') #维基
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'oscar_202201.part_0075.jsonl') # 通用文本

# mnbvc 0.jsonl父级文件路径
# 知乎 https://huggingface.co/datasets/liwu/MNBVC/tree/main/qa/20230196/zhihu
MNBVC_PATH = "~/mnbvc"


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


def check_dir_exist(file_name):
    """
    检查文件夹是否存在，不存在则创建
    :param file_name:
    :return:
    """
    if not os.path.exists(file_name):
        os.mkdir(file_name)


def print_log(msg):
    """
    打印日志
    :param msg:
    :return:
    """
    print("Time:{time}\nMessage:{msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                              msg=msg))


def mnbvc_zhihu(file_name):
    """
    处理mnbvc知乎数据，用于后续拆词和统计词频
    :param total_count:
    :return:
    """
    total_count_mark = 0
    check_dir_exist('cn_dicts_dazhu')
    match = re.search(r'(\d+)', file_name)  # 查找所有的数字序列
    if not match:
        return
    number = int(match.group(1))  # 获取第一个匹配组，并转换为整数            print_log("Read File: {}".format(file_name))
    write_file_name = os.path.join('cn_dicts_dazhu', "zhihu_deal{}.txt".format(number))
    with open(file_name, 'r') as file, open(write_file_name, 'w') as write_file:
        # 读取整个文件内容，减少IO读写
        lines = file.readlines()
        line_count = len(lines)

        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue

            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError:
                print_log("JSONDecodeError")
                print_log(line)
                continue

            q_content = data['问']
            a_content = data['答']
            q_length = len(q_content)
            a_length = len(a_content)
            write_file.write(q_content + "\n" + a_content + "\n")
            total_count_mark += q_length + a_length

        print_log(f"line_count {line_count}")
    return total_count_mark


if __name__ == '__main__':
    for file_name in scan_file(os.path.expanduser(MNBVC_PATH)):
        if file_name.endswith('.jsonl'):
            total_count = mnbvc_zhihu(file_name)
            print_log(f"total_count {total_count}\n")