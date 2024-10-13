# 白霜拼音

原始配置和词库由[雾凇拼音](https://github.com/iDvel/rime-ice)的 [af2480b](https://github.com/iDvel/rime-ice/commit/af2480ba1b147a6a54c0c21e2997ef451c34e036) commit 修改而来。

雾凇词库里的词比较全但也不是非常全，主要的问题是字频和词频不太对，废词有点多，于是重新制作。

主要维护词库、词频。在雾凇词库的基础上删除了不健康词汇，删除了大量冷僻词（频率==1 且分词器分不出的词），删除/调整了诸如“的吧”、“的了”这种不是词的词。手动大量修改了字频 词频。第一步是做了减法。

然后使用 745396750 字的高质量语料，进行分词，重新统计字频、词频，归一化，以达到更好的输入效果。全拼和双拼都可以使用。

### 使用方法

使用方法基本同雾凇拼音，微调了一些触发指令，加入了lua辅助码的支持。辅助码是可选项，按下`开启，不影响正常打字。

- 符号 /fh 更多符号详见`https://github.com/gaboolic/rime-frost/blob/master/symbols_v.yaml`
- 带调韵母 /a /e /u 等
- 日期与时间 rq sj xq dt ts
- 开启辅助码 ` [墨奇辅助码拆分说明](https://moqiyinxing.chunqiujinjing.com/index/mo-qi-yin-xing-shuo-ming/fu-zhu-ma-shuo-ming/mo-qi-ma-chai-fen-shuo-ming)
- 部件拆字反查 uU
- unicode字符 U
- 数字金额大写 R
- 农历 N
- 计算器 V

### 如何安装&配置文件路径

#### 手动下载安装

下载本仓库的压缩包 Code - Download ZIP（或者下载[releases](https://github.com/gaboolic/rime-frost/releases)最新的 source-code.zip），解压到如下路径即可

- Windows: `%APPDATA%\Rime` （可以在右下角小狼毫输入法右键打开菜单选用户文件夹）复制完之后，去输入法设定里选择白霜拼音，然后重新部署
- Mac
  - [鼠须管](https://github.com/rime/squirrel)路径为 `~/Library/Rime`
  - [fcitx5-Mac 版](https://github.com/fcitx-contrib/fcitx5-macos)路径为 `~/.local/share/fcitx5/rime`
- Linux
  - [fcitx5-rime](https://github.com/fcitx/fcitx5-rime)路径为 `~/.local/share/fcitx5/rime`
  - fcitx5 flatpak 版的路径 `~/.var/app/org.fcitx.Fcitx5/data/fcitx5/rime`
  - [ibus-rime](https://github.com/rime/ibus-rime)路径为 `~/.config/ibus/rime`
- Android
  - [fcitx5-安卓版](https://github.com/fcitx5-android/fcitx5-android)路径为 `/Android/data/org.fcitx.fcitx5.android/files/data/rime`
  - [同文](https://github.com/osfans/trime)路径为 `/rime`
  - [雨燕](https://github.com/gurecn/YuyanIme) 已内置白霜词库词频，直接安装使用即可
- iOS [仓输入法](https://github.com/imfuxiao/Hamster) 目前已内置，也可以通过【输入方案设置 - 右上角加号 - 方案下载 - 覆盖并部署】来更新白霜拼音。


#### 通过 Git 安装

**首次安装：**

根据用户使用的系统、安装的软件不同，先cd到对应的配置文件的父级目录(例如Windows为`%APPDATA%`、mac鼠须管为`~/Library/`)，然后执行以下命令：

`git clone --depth 1 https://github.com/gaboolic/rime-frost Rime`

**后续更新：**

在 Rime 文件夹执行 `git pull` 即可。

- Mac: `cd ~/Library/Rime && git pull`
- Windows: `cd "$env:APPDATA\Rime" && git pull`
- 其他系统以此类推

#### 通过 东风破 安装

选择配方（others/recipes/*.recipe.yaml）来进行安装或更新：

- ℞ 安装或更新全部文件 执行bash rime-install gaboolic/rime-frost:others/recipes/full

### 无智能模型时的输入效果

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

### To-Do

- [x] 整理分词后词频比较高但词库没有的词加进去
- [ ] 错字错音提醒lua
- [ ] 写自动化脚本，把句子转成拼音，再用拼音调用 rime_api 生成句子，比对正确率，迭代
- [ ] 加上墨奇码首末字形反查，例如 amq 引导符再打 mu cun 可以打出“村 櫉 梼 树”等字
- [x] 加上 lua 引导辅助码的功能
- [ ] 2 字词，动词+名词结构，中间加入“了” “完”，结尾加入“没”自动派生词汇。
  - 例如：
    - 拔牙： 拔了牙，拔完牙，拔牙没，没拔牙，拔没拔牙
  - 形容词中间加“不”：
    - 例如：厉害→厉不厉害
- [ ] 类似“第四 四列 = 第四列”这种词加上去
- [ ] 统计中文语料中的英文词频
- [ ] 训练一个智能语言模型

### 鸣谢

雾凇词库 <https://github.com/iDvel/rime-ice> 白霜词库的初始词库、绝大部分配置来自雾凇词库

结巴中文分词 <https://github.com/fxsjy/jieba>

汉字转拼音(pypinyin) <https://github.com/mozillazg/python-pinyin>

MNBVC 超大规模中文语料集 <https://github.com/esbatmop/MNBVC> 目前已有 33TB 数据量

kenlm <https://github.com/kpu/kenlm> 官网<https://kheafield.com/code/kenlm/>

kenlm 教程、python 调用 <https://github.com/mattzheng/py-kenlm-model>

吉祥物(于2024-10-12捡来)：

<img src="others/img/white-cat.jpg" width=30%>

### 友情链接

使用白霜词库的方案

墨奇音形 <https://github.com/gaboolic/rime-shuangpin-fuzhuma>

墨奇五笔整句 <https://github.com/gaboolic/rime-wubi-sentence>

薄荷拼音 <https://github.com/Mintimate/oh-my-rime>

雨燕输入法 <https://github.com/gurecn/YuyanIme> 一个开箱即用的安卓输入法 内置白霜词库

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gaboolic/rime-frost&type=Date)](https://star-history.com/#gaboolic/rime-frost&Date)
