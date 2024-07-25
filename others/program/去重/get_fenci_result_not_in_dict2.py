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
print("为什么" in dict_word_map)

fenci_file = ('others/2字词频表.txt')
fenci_word_map = {}
# with open(fenci_file, 'r', encoding='utf-8') as fenci_file:
#     for line in fenci_file:
#         line = line.strip()
#         if line.startswith("#"):
#             continue
#         params = line.split("	")
#         word = params[0]
#         freq = params[1]
#         if ' ' in freq:
#             freqs = freq.split(" ")
#             freq = freqs[0]
#         fenci_word_map[word] = int(freq)
fenci_file = ('others/3字统计结果.txt')
with open(fenci_file, 'r', encoding='utf-8') as fenci_file:
    for line in fenci_file:
        line = line.strip()
        if line.startswith("#"):
            continue
        params = line.split("	")
        word = params[0]
        freq = params[1]
        fenci_word_map[word] = int(freq)
print(len(fenci_word_map))
print("为什么" in fenci_word_map)

not_in_dict = []
for word in fenci_word_map:
    if word not in dict_word_map:
        not_in_dict.append(word)
#print(not_in_dict)

# Write the list to a file
output_file = 'cn_dicts_dazhu/not_in_dict2.txt'
with open(output_file, 'w', encoding='utf-8') as file:
    for word in not_in_dict:
        freq = int(fenci_word_map[word])
        if freq < 100:
            continue
        if len(word) == 1:
            continue
        if '的' in word or '是' in word or '了' in word or '有' in word:
            continue
        file.write(f"{word}\t{freq}\n")

print(f"The words not in dict_word_map have been written to {output_file}.")