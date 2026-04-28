import argparse
import gzip
import json
import os
import re
import time
from pathlib import Path

# mnbvc liwu_253874_com.jsonl
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'undl_01.jsonl') # 通用平行
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'liwu_253874_com.jsonl') # 里屋论坛
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'46.jsonl') #维基
# file_name = os.path.join(os.path.expanduser("~/Downloads"),'oscar_202201.part_0075.jsonl') # 通用文本

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MNBVC_PATH = PROJECT_ROOT / "yuliao"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[3] / "cn_dicts_dazhu"


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
    deduped_files = {}
    for file_name in sorted(file_list):
        if file_name.endswith(".jsonl.gz"):
            key = file_name[:-3]
            deduped_files[key] = file_name
        elif file_name.endswith(".jsonl"):
            deduped_files.setdefault(file_name, file_name)
    return sorted(deduped_files.values())


def check_dir_exist(file_name):
    """
    检查文件夹是否存在，不存在则创建
    :param file_name:
    :return:
    """
    if not os.path.exists(file_name):
        os.mkdir(file_name)


def open_corpus_file(file_name):
    if file_name.endswith(".gz"):
        return gzip.open(file_name, "rt", encoding="utf-8")
    return open(file_name, "r", encoding="utf-8")


def print_log(msg):
    """
    打印日志
    :param msg:
    :return:
    """
    print("Time:{time}\nMessage:{msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                              msg=msg))


def mnbvc_zhihu(file_name, output_dir):
    """
    处理mnbvc知乎数据，用于后续拆词和统计词频
    :param total_count:
    :return:
    """
    total_count_mark = 0
    check_dir_exist(output_dir)
    match = re.search(r'(\d+)', file_name)  # 查找所有的数字序列
    if not match:
        return
    number = int(match.group(1))  # 获取第一个匹配组，并转换为整数            print_log("Read File: {}".format(file_name))
    write_file_name = os.path.join(output_dir, "zhihu_deal{}.txt".format(number))
    with open_corpus_file(file_name) as file, open(write_file_name, 'w', encoding='utf-8') as write_file:
        line_count = 0
        print_log("Read File: {}".format(file_name))
        for line in file:
            line = line.strip()
            if len(line) == 0:
                continue
            line_count += 1

            try:
                data = json.loads(line)
            except json.decoder.JSONDecodeError:
                print_log("JSONDecodeError")
                print_log(line)
                continue

            a_content = data.get('答', '').strip()
            if not a_content:
                continue
            write_file.write(a_content + "\n")
            total_count_mark += len(a_content)

        print_log(f"line_count {line_count}")
    return total_count_mark


def parse_args():
    parser = argparse.ArgumentParser(description="Extract answer-only Zhihu corpus text from MNBVC JSONL files.")
    parser.add_argument(
        "--input-dir",
        default=str(DEFAULT_MNBVC_PATH),
        help="Directory containing .jsonl or .jsonl.gz files. Defaults to the repository yuliao folder.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for zhihu_deal*.txt outputs. Defaults to rime-frost/cn_dicts_dazhu.",
    )
    parser.add_argument(
        "--input-files",
        nargs="*",
        help="Specific .jsonl or .jsonl.gz files to process. When set, --input-dir is ignored.",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    input_dir = os.path.expanduser(args.input_dir)
    output_dir = os.path.expanduser(args.output_dir)
    file_names = args.input_files if args.input_files else scan_file(input_dir)
    for file_name in file_names:
        file_name = os.path.expanduser(file_name)
        if file_name.endswith(('.jsonl', '.jsonl.gz')):
            total_count = mnbvc_zhihu(file_name, output_dir)
            print_log(f"total_count {total_count}\n")