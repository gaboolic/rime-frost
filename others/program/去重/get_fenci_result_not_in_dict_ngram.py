import opencc
import re
# pip install opencc

converter = opencc.OpenCC('t2s.json')

def is_all_chinese(input_str):
    pattern = re.compile(r'[\u4e00-\u9fa5]+')  # 匹配所有的中文字符
    return True if pattern.fullmatch(input_str) else False

# 找出在fenci_word_map并且不在dict_word_map中的词
dict_file = ('cn_dicts_dazhu/custom_fenci_dict.txt')
dict_word_map = {}
with open(dict_file, 'r', encoding='utf-8') as dict_file:
    for line in dict_file:
        line = line.strip()
        if line.startswith("#"):
            continue
        params = line.split(" ")
        word = params[0]
        freq = params[1]
        dict_word_map[word] = int(freq)
print(len(dict_word_map))


fenci_file = ('cn_dicts_dazhu/ngram_1_frequencies.txt')
fenci_word_map = {}
with open(fenci_file, 'r', encoding='utf-8') as fenci_file:
    for line in fenci_file:
        line = line.strip()
        if line.startswith("#"):
            continue
        params = line.split("\t")
        word = params[0]
        
        word = converter.convert(word)
        freq = params[1]
        fenci_word_map[word] = int(freq)
print(len(fenci_word_map))

not_in_dict = []
for word in fenci_word_map:
    if word not in dict_word_map:
        not_in_dict.append(word)
#print(not_in_dict)

# Write the list to a file
output_file = 'cn_dicts_dazhu/not_in_dict_ngram1.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    for word in not_in_dict:
        freq = int(fenci_word_map[word])
        if freq < 100:
            continue
        if len(word) == 1:
            continue
        if not is_all_chinese(word):
            continue
        # file.write(f"{word}\t{freq}\n")
        file.write(f"{word}\n")

print(f"The words not in dict_word_map have been written to {output_file}.")