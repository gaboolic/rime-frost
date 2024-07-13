# 脚本来自RIME输入法交流小群-雨辰
import re
import math
import os
import string

def extract_ngram_counts(arpa_file):
    ngrams_counts = {}
    with open(arpa_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("ngram"):
                parts = line.split('=')
                if len(parts) == 2 and parts[0].startswith("ngram"):
                    order = int(parts[0].split()[1])
                    count = int(parts[1])
                    ngrams_counts[order] = count
            elif line.startswith("\\1-grams:"):  # Stop after reading counts
                break
    return ngrams_counts

def extract_ngrams(arpa_file):
    ngram_line_pattern = re.compile(r"^(-?\d+\.\d+)\t(.+?)(?:\t-?\d+\.\d+)?$")
    with open(arpa_file, 'r', encoding='utf-8') as file:
        current_order = 0
        for line in file:
            line = line.strip()
            if line.startswith("\\") and "-grams:" in line:
                current_order = int(line.split('-')[0][1:])
                continue
            
            ngram_line_match = ngram_line_pattern.match(line)
            if ngram_line_match:
                logprob, ngram = ngram_line_match.groups()
                prob = math.exp(float(logprob))
                #prob = math.pow(10,abs(float(logprob)))
                yield current_order, (ngram.strip(), prob)

def write_frequencies_to_file(ngrams_generator, ngrams_counts, filename_pattern):
    current_order = 0
    file = None
    for order, ngram_data in ngrams_generator:
        if order != current_order:
            if file:
                file.close()
            current_order = order
            filename = filename_pattern.format(order)
            filename = os.path.join('cn_dicts_dazhu', filename)
            file = open(filename, 'w', encoding='utf-8')
            print(f"Writing {current_order}-grams to {filename}")

        ngram, prob = ngram_data
        total_count = ngrams_counts.get(order, 1)
        freq = round(prob * total_count)
        file.write(f"{ngram}\t{freq}\n")

    if file:
        file.close()

# Update the path to your ARPA file
arpa_file_path = os.path.join('cn_dicts_dazhu', "zhi0713.arpa")
# arpa_file_path = os.path.join('cn_dicts_dazhu', "lm_sc.arpa")

# Extract n-grams counts
ngrams_counts = extract_ngram_counts(arpa_file_path)
print("extract_ngram_counts done")
# Extract n-grams and write frequencies to files
ngrams_generator = extract_ngrams(arpa_file_path)
write_frequencies_to_file(ngrams_generator, ngrams_counts, "ngram_{}_frequencies.txt")
print("write_frequencies_to_file done")