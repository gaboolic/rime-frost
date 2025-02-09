import os
import re
import string
import json
import string
import string

# 生成字母表
alphabet = list(string.ascii_lowercase)

result = []

# 生成单个字母的字符串
for letter in alphabet:
    result.append(letter)

# 生成两个字母的字符串
for i in range(len(alphabet)):
    for j in range(len(alphabet)):
        result.append(alphabet[i] + alphabet[j])

# 生成三个字母的字符串
for i in range(len(alphabet)):
    for j in range(len(alphabet)):
        for k in range(len(alphabet)):
            result.append(alphabet[i] + alphabet[j] + alphabet[k])

# 生成四个字母的字符串
for i in range(len(alphabet)):
    for j in range(len(alphabet)):
        for k in range(len(alphabet)):
            for l in range(len(alphabet)):
                result.append(alphabet[i] + alphabet[j] + alphabet[k] + alphabet[l])

print(len(result))
print(result[0])
print(result[-1])

read_file = open(os.path.join('cn_dicts_dazhu', "zhihu_deal_sort_merge.txt"), 'r')
write_file = open(os.path.join('cn_dicts_dazhu', "知码.txt"), 'w')


index = 0
# 逐行读取文件内容
for line in read_file:
    line = line.strip()
    params = line.split("\t")

    if index >= len(result):
        break
    code = result[index]


    write_file.write(f"{code}\t{params[0]}\n")
    index += 1
