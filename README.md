# 白霜拼音

原始配置和词库由[雾凇拼音](https://github.com/iDvel/rime-ice)的 [af2480b](https://github.com/iDvel/rime-ice/commit/af2480ba1b147a6a54c0c21e2997ef451c34e036) commit 修改而来。

雾凇词库里的词比较全但也不是非常全，主要的问题是字频和词频不太对，废词有点多，于是重新制作。

主要维护词库、词频。在雾凇词库的基础上删除了不健康词汇，删除了大量冷僻词（频率==1 且分词器分不出的词），删除/调整了诸如“的吧”、“的了”这种不是词的词。手动大量修改了字频 词频。第一步是做了减法。

然后使用745396750字的高质量语料，进行分词，重新统计字频、词频，归一化，以达到更好的输入效果。全拼和双拼都可以使用。

使用方法同雾凇拼音。

无智能模型时的输入效果
![alt text](others/img/gegegojx.png)

![alt text](others/img/mggjdgg.png)

![alt text](others/img/ddmdd.png)

![alt text](others/img/tushuguancangshu.png)

![alt text](others/img/znjldkd.png)

![alt text](others/img/kudsvqw.png)

![alt text](others/img/cqlbtdmdfu.png)

![alt text](others/img/djbwv.png)

![alt text](others/img/刚交的朋友.png)

![alt text](others/img/刚交的好朋友.png)

![alt text](others/img/刚交的好朋友2.png)

![alt text](others/img/衍射.png)

后续todo：

拆分细胞词库，加上长尾词，重新分词

训练一个智能语言模型

### 鸣谢

雾凇词库 <https://github.com/iDvel/rime-ice> 白霜词库的初始词库、绝大部分配置来自雾凇词库

结巴中文分词 <https://github.com/fxsjy/jieba>

汉字转拼音(pypinyin) <https://github.com/mozillazg/python-pinyin>

MNBVC超大规模中文语料集 <https://github.com/esbatmop/MNBVC> 目前已有33TB数据量

kenlm <https://github.com/kpu/kenlm> 官网<https://kheafield.com/code/kenlm/>

kenlm教程、python调用 <https://github.com/mattzheng/py-kenlm-model>

### 友情链接

墨奇音形 <https://github.com/gaboolic/rime-shuangpin-fuzhuma>
墨奇五笔整句 <https://github.com/gaboolic/rime-wubi-sentence>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gaboolic/rime-frost&type=Date)](https://star-history.com/#gaboolic/rime-frost&Date)
