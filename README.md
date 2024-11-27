# c2json-editor-qt

用`Pyqt5`编写的一款 | 《二战前线合集》(*Commando Collections*)(Steam新版)下的《二战前线2》(*Commando 2*)创意工坊(*Workshop*)自定mod导出的json数据的 | **非官方**修改工具。

是面向别出心裁的、具有探索精神的、想要在mod中尝试给一些对象设定非常规数据的(例如小数、负数)mod制作者的一款编辑工具。

本程序仓库地址在[这里](https://github.com/wyz-2015/c2json-editor-qt/)。如果君出于各种原因，只获得了本程序的一个副本(人话：不知道从哪下载到了这样一份程序源码)，它毕竟不会自行更新，建议使用`git clone`的方式克隆本仓库并使用。这样方便接收更新。

## 使用警告

1. 本程序是以为探索者提供工具为目的编写的，实验与探索必然伴随着一定的失败。<span style="color: red">本程序并不确保*利用本程序修改的mod*，能在游戏中正确运行；同时对由上述行为引发的不良后果概不负责。</span>

2. 本程序遵循[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)协议开放源代码。

## 安装方法

1. 需要`Python >= 3.10`。Windows用户请最好前往[官网](https://www.python.org/)下载安装，在安装过程中，请务必勾选关于 将Python添加到`Path`环境变量 的选项。

2. 需要安装python库`pyqt5`，方法见下：

### Windows

Windows下默认的python解释器名为`python.exe`，打开`cmd`，键入`python --version`并执行，如果能输出类似`Python 3.12.3`的信息，说明Python安装正确。

接下来执行指令：

```
python -m ensurepip --upgrade
python -m pip install pyqt5 -i https://mirrors.aliyun.com/pypi/simple/
```

### Unix-Like

这不需要我提示了吧？默认软件源里很可能已经带了，从源里安装即可。

## 使用方法

1. 从游戏内创意工坊界面中导出自己创立的mod的json数据到本地。

2. 执行本目录下的`main.py`以启动程序。

2. 用本程序打开json文件并编辑，保存或另存。

3. 将修改过的json文件导入并覆盖需要目标mod。
