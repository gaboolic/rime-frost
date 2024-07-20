# 白霜拼音

原始配置和词库由[雾凇拼音](https://github.com/iDvel/rime-ice)的 [af2480b](https://github.com/iDvel/rime-ice/commit/af2480ba1b147a6a54c0c21e2997ef451c34e036) commit 修改而来。

雾凇词库里的词比较全但也不是非常全，主要的问题是字频和词频不太对，废词有点多，于是重新制作。

主要维护词库、词频。在雾凇词库的基础上删除了不健康词汇，删除了大量冷僻词（频率==1 且分词器分不出的词），删除/调整了诸如“的吧”、“的了”这种不是词的词。手动大量修改了字频 词频。第一步是做了减法。

然后使用745396750字的高质量语料，进行分词，重新统计字频、词频，归一化，以达到更好的输入效果。全拼和双拼都可以使用。

使用方法同雾凇拼音。

### 如何安装&配置文件路径

下载本仓库的压缩包Code - Download ZIP（或者下载[releases](https://github.com/gaboolic/rime-frost/releases)最新的source-code.zip），解压到如下路径即可

- windows：%APPDATA%\Rime
- mac
  - [鼠须管](https://github.com/rime/squirrel)路径为~/Library/Rime
  - [fcitx5-mac版](https://github.com/fcitx-contrib/fcitx5-macos)路径为~/.local/share/fcitx5/rime
- linux
  - [fcitx5-rime](https://github.com/fcitx/fcitx5-rime)路径为~/.local/share/fcitx5/rime
  - fcitx5 flatpak版的路径~/.var/app/org.fcitx.Fcitx5/data/fcitx5/rime
  - [ibus-rime](https://github.com/rime/ibus-rime)路径为~/.config/ibus/rime
- android
  - [fcitx5-安卓版](https://github.com/fcitx5-android/fcitx5-android)路径为 /Android/data/org.fcitx.fcitx5.android/files/data/rime
  - [同文](https://github.com/osfans/trime)路径为 /rime
- ios [仓输入法](https://github.com/imfuxiao/Hamster) 目前已内置，也可以通过【输入方案设置 - 右上角加号 - 方案下载 - 覆盖并部署】来更新墨奇音形。

如果会使用git基本操作，可以直接用git管理配置，首次：例如mac可以打开~/Library文件夹，然后`git clone --depth 1 https://github.com/gaboolic/rime-frost Rime`  后面在Rime文件夹执行`git pull`即可

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
整理分词后词频比较高但词库没有的词加进去

统计中文语料中的英文词频

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
