# program 脚本说明

这个目录主要放词库处理、语料分词、词频写入、去重、排序和发布相关脚本。脚本通常需要在项目根目录执行，例如：

```powershell
python others/program/mnbvc/yuliao_fenci.py
```

## 制作白霜词库的过程

白霜词库最初基于雾凇拼音词库制作。使用一段时间后发现原词库存在一些问题，例如字频偏高，废词、黄词较多；输入“衍射与折射”、“打几把游戏”、“喝一杯蜜雪”等词句时，可能出现不符合预期甚至比较尴尬的上屏结果。因此后续重新制作并反复迭代词频。

整体思路是先在原词库基础上做减法，再使用语料分词统计得到新的词频，然后把新词频写回词库，测试效果后继续人工修正。

1. 在雾凇词库基础上做减法

   所有字的字频先整体 `/100`，再手工去掉“的吧”、“的了”这类不是词的条目，并大量手工调整字频、词频。

2. 生成 Jieba 自定义分词词典

   ```powershell
   python others/program/mnbvc/generate_custom_fenci_dict.py
   ```

   从修改后的词库生成：

   ```text
   cn_dicts_dazhu/custom_fenci_dict.txt
   ```

   后续分词脚本会加载这个文件，减少词库已有词被错误切碎的情况。

3. 下载 MNBVC 语料并清洗成纯文本

   ```powershell
   python others/program/mnbvc/get_dict.py
   ```

   默认读取 `yuliao` 目录下的 `.jsonl` / `.jsonl.gz` 文件，提取知乎回答内容，输出纯文本：

   ```text
   cn_dicts_dazhu/zhihu_deal*.txt
   ```

4. 对清洗后的语料分词并统计词频

   ```powershell
   python others/program/mnbvc/yuliao_fenci.py
   ```

   输入：

   ```text
   cn_dicts_dazhu/zhihu_deal*.txt
   ```

   输出：

   ```text
   cn_dicts_dazhu/zhihu_deal_sort*.txt
   ```

5. 合并多个分词统计结果

   ```powershell
   python others/program/mnbvc/merge_fenci_freq_result.py
   ```

   输入：

   ```text
   cn_dicts_dazhu/zhihu_deal_sort*.txt
   ```

   输出：

   ```text
   cn_dicts_dazhu/zhihu_deal_sort_merge.txt
   ```

6. 将统计词频写入白霜词库

   ```powershell
   python others/program/reduce_freq_base_to_zhifreq.py
   python others/program/reduce_freq_celldict_to_zhifreq.py
   ```

   读取：

   ```text
   cn_dicts_dazhu/zhihu_deal_sort_merge.txt
   ```

   并结合以下文件调整词频：

   ```text
   others/降频词.txt
   others/增频词.txt
   others/多音字.txt
   ```

   输出处理后的词库到：

   ```text
   cn_dicts_dazhu/*.dict.yaml
   ```

   

   如果发现 `cn_dicts/41448.dict.yaml` 里的繁体、生僻字频率整体仍然偏高，可以再把这个大字表的频率整体 `/10`：

   ```powershell
   python others/program/divide_freq_41448.py
   ```

7. 重新生成 Jieba 自定义分词词典并测试新词频效果

   ```powershell
   python others/program/mnbvc/generate_custom_fenci_dict.py
   python others/program/mnbvc/fenci_test.py
   ```

8. 手工打字评估新词频效果

   根据实际输入体验继续人工剔除一些影响分词效果的长词，例如“时间和”、“鱼的”等。

以上 1-8 步可以重复多次执行，通过“语料统计 + 手工修正 + 实际输入测试”的方式自我迭代，词库效果会逐步变好。

9. 添加细胞词库

   添加细胞词库时也会用到一些去重、注音和整理脚本，相关脚本都放在 `others/program` 目录下。

## 相关脚本

- `mnbvc/get_dict.py`：从 MNBVC JSONL 语料中提取知乎回答文本。
- `mnbvc/generate_custom_fenci_dict.py`：根据现有词库生成 Jieba 用户词典。
- `mnbvc/yuliao_fenci.py`：对清洗后的语料分词并统计词频。
- `mnbvc/merge_fenci_freq_result.py`：合并多个 `zhihu_deal_sort*.txt` 词频文件。
- `reduce_freq_base_to_zhifreq.py`：把合并后的语料词频写入主词库。
- `reduce_freq_celldict_to_zhifreq.py`：类似 `reduce_freq_base_to_zhifreq.py`，但处理 `cn_dicts_cell`，输出到 `cn_dicts_temp`。
- `divide_freq_41448.py`：把 `cn_dicts/41448.dict.yaml` 的频率整体除以 10。
- `multiply_freq.py`：批量放大词库频率。
- `dict_sort.py`：按音节和频率重新排序词库条目。

## 注意事项

- 多数脚本里的相对路径都按项目根目录计算，建议不要在 `others/program` 目录内直接执行。
- `mnbvc/merge_fenci_freq_result.py` 当前默认合并 `zhihu_deal_sort0.txt` 到 `zhihu_deal_sort4.txt`，如果实际文件编号不同，需要先改脚本里的范围。
- `reduce_freq_base_to_zhifreq.py` 会把结果写到 `cn_dicts_dazhu`，不会直接覆盖 `cn_dicts`。


## for AI
阅读program下所有脚本，阅读 @others/program/README.md 
把 E:\语料 下的 0 1 2 3 4.jsonl.gz 重新分词统计词频，更新本仓库的频率
注意要点：只获取回答的正文统计 统计词频时要把“错字词”的词频加到正确的词频上
统计完成要根据“降频词” “增频词” 最终处理
41448.dict.yaml也要最终频率/10