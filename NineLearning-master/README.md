# NjuptGo

> folk from [**NineLearning**](https://github.com/blont714/NineLearning)
>
> 实现9路幻影围棋的基础AI


## Pyaq

Pyaq是仅用Python实现的Go程序。
该程序是旨在学习和玩Go神经网络模型的深度学习教程。  

![top](https://user-images.githubusercontent.com/32036527/36086412-90005ab6-100f-11e8-912b-fdf30c61b2ef.png)  

更具体地讲，做了以下内容。

- 使用[TensorFlow](https://www.tensorflow.org/)学习9条记录
- 玩学习的模型

它是Go游戏和深度学习的最低必需实现，它具有约1000行的所有学习和执行代码。如果您想学习更高级的内容，请阅读源代码。当然也欢迎拉取请求。

### 1.准备

以下面的环境为例进行说明。

- Ubuntu 16.04
- Python 2.7
- TensorFlow

引进TensorFlow是[在Ubuntu安装TensorFlow](https://qiita.com/yudsuzuk/items/092c38fee18e4484ece9)请参考。
将GPU与TensorFlow一起使用时

- [CUDA工具包9.0](https://developer.nvidia.com/cuda-90-download-archive)
- [cuDNN v7.0](https://developer.nvidia.com/cudnn)

必须安装。此外，还需要nVidia生产的[CUDA Capability](https://developer.nvidia.com/cuda-gpus) 3.5或更高版本的图形板。
有关CUDA的[安装](https://qiita.com/JeJeNeNo/items/05e148a325192004e2cd)，请参考[在Ubuntu 16.04LTS上安装的CUDA 8.0和cuDNN 6](https://qiita.com/JeJeNeNo/items/05e148a325192004e2cd)（注意：版本与链接不同）。

接下来，下载源代码。

```shell
$ git clone https://github.com/ymgaq/Pyaq
```
您也可以从右上角的“克隆或下载”手动下载它。
准备完成。

如果要立即运行，请将学习到的数据文件复制`Pyaq/pre_train/model.ckpt`到`Pyaq/`“，并使用[ GoGui。](#4.在GoGui上玩)

让我们检查一下测试匹配是否有效。

```shell
$ ./pyaq.py --self --random
```

如果获得以下输出，则说明成功。转到“ [2.学习](#2.学习)”。

```
   A  B  C  D  E  F  G  H  J 
 9 .  X  X  X  X  X  X  .  X  9
 8 X  X  X  .  X  X  X  X  X  8
 7 O  O  X  X  X  O  O  X  O  7
 6 O  O  O  O  O  .  O  O  O  6
 5 O  O  X  O  O  O  O  .  O  5
 4 X  X  X  O  .  O  .  O  O  4
 3 .  X  O  O  O  O  O  O  .  3
 2 X  X  X  X  X  O  O  O  O  2
 1 X  .  X  O  O  O  O  O  .  1
   A  B  C  D  E  F  G  H  J 

   A  B  C  D  E  F  G  H  J 
 9 .  X  X  X  X  X  X  .  X  9
 8 X  X  X  .  X  X  X  X  X  8
 7 O  O  X  X  X  O  O  X  O  7
 6 O  O  O  O  O  .  O  O  O  6
 5 O  O  X  O  O  O  O  .  O  5
 4 X  X  X  O  .  O  .  O  O  4
 3 .  X  O  O  O  O  O  O  .  3
 2 X  X  X  X  X  O  O  O  O  2
 1 X  .  X  O  O  O  O  O  .  1
   A  B  C  D  E  F  G  H  J 

result: W+16.0
```

### 2.学习

首先，扩展学习文件。

```shell
$ cd Pyaq
$ unzip sgf.zip
```

使用9个跟踪记录文件（* .sgf）进行学习。当您运行以下命令时，学习开始：

```shell
$ ./pyaq.py --learn
```

如果要在没有GPU的情况下进行训练，请`--cpu`添加一个选项。
（但是，纯CPU学习尚未经过全面测试。）

```shell
$ ./pyaq.py --learn --cpu
```

学习日志扩展如下：相同的内容也记录在log.txt中。
根据GPU的性能，学习将在大约3-4小时内完成。仅对于CPU，大约需要3天。

```
imported 34572 sgf files.
converting ...
learning rate=0.0003
progress: 0.10[%] 14.3[sec]
progress: 0.20[%] 13.3[sec]
progress: 0.30[%] 13.3[sec]
progress: 0.40[%] 13.4[sec]
progress: 0.50[%] 13.3[sec]
progress: 0.60[%] 13.4[sec]
progress: 0.70[%] 13.3[sec]
progress: 0.80[%] 13.3[sec]
progress: 0.90[%] 13.2[sec]
progress: 1.00[%] 13.2[sec]
progress: 1.10[%] 13.3[sec]
progress: 1.20[%] 13.3[sec]
progress: 1.30[%] 13.3[sec]
progress: 1.40[%] 13.2[sec]
progress: 1.50[%] 13.2[sec]
progress: 1.60[%] 13.2[sec]
progress: 1.70[%] 13.3[sec]
progress: 1.80[%] 13.3[sec]
progress: 1.90[%] 13.2[sec]
progress: 2.00[%] 13.2[sec]
progress: 2.10[%] 13.2[sec]
progress: 2.20[%] 13.4[sec]
progress: 2.30[%] 13.4[sec]
progress: 2.40[%] 13.2[sec]
progress: 2.50[%] 13.3[sec]
train: policy=46.95[%]  value=0.469
test : policy=47.13[%]  value=0.469

progress: 2.60[%] 15.5[sec]
progress: 2.70[%] 13.4[sec]
```

每2.5％对测试数据进行评估。`policy`是游戏分数的下一手和神经网络输出的一手之间的匹配率，并且`value`是分数分数与网络输出的评估值（-1至+1）之间的误差（均方误差）。最后，在测试数据中似乎策略为57％，值约为0.36。
学习完成后，将`model.ckpt`保存参数文件。

网络模型的`BLOCK_CNT`和`FILTER_CNT`或板，`KEEP_PREV_CNT`或改变，如改变该模型的形状，通过使用原始游戏记录数据，则可以产生更有力的参数。如果您有兴趣，请尝试为您创建最强大的网络。

### 3.让我们玩自我比赛（控制台）

使用在控制台上学习的模型，让我们首先进行不搜索的自我匹配。

```shell
$ ./pyaq.py --self --quick --cpu
```

无需搜索即可获得战斗结果。

```
   A  B  C  D  E  F  G  H  J 
 9 .  .  .  .  .  O  O  X  .  9
 8 .  .  O  O  .  O  X  X  X  8
 7 .  O  X  X  O  O  O  X  .  7
 6 .  .  .  O  X  O  X  X  .  6
 5 O  O  .  O  X  X  O  .  .  5
 4[X] X  O  O  O  X  O  .  .  4
 3 X  X  X  O  X  X  X  .  .  3
 2 X  .  X  O  X  .  .  .  .  2
 1 .  X  O  O  O  X  .  .  .  1
   A  B  C  D  E  F  G  H  J 

   A  B  C  D  E  F  G  H  J 
 9 .  .  .  .  .  O  O  X  .  9
 8 .  .  O  O  .  O  X  X  X  8
 7 .  O  X  X  O  O  O  X  .  7
 6 .  .  .  O  X  O  X  X  .  6
 5 O  O  .  O  X  X  O  .  .  5
 4 X  X  O  O  O  X  O  .  .  4
 3 X  X  X  O  X  X  X  .  .  3
 2 X  .  X  O  X  .  .  .  .  2
 1 .  X  O  O  O  X  .  .  .  1
   A  B  C  D  E  F  G  H  J 

   A  B  C  D  E  F  G  H  J 
 9 .  .  .  .  .  O  O  X  .  9
 8 .  .  O  O  .  O  X  X  X  8
 7 .  O  X  X  O  O  O  X  .  7
 6 .  .  .  O  X  O  X  X  .  6
 5 O  O  .  O  X  X  O  .  .  5
 4 X  X  O  O  O  X  O  .  .  4
 3 X  X  X  O  X  X  X  .  .  3
 2 X  .  X  O  X  .  .  .  .  2
 1 .  X  O  O  O  X  .  .  .  1
   A  B  C  D  E  F  G  H  J 


result: Draw
```

接下来，让我们与搜索进行自我匹配。

```shell
$ ./pyaq.py --self --byoyomi=3
```

如果没有GPU，则`--cpu`添加一个选项。

```shell
$ ./pyaq.py --self --byoyomi=3 --cpu
```

游戏每步进行3秒。

```
move count=3: left time=0.0[sec] evaluated=104
|move|count  |rate |value|prob | best sequence
|D5  |   1114| 54.7| 56.3| 90.4| D5 ->C5 ->C4 ->E5 ->D6 ->E6 ->E7 ->E4 
|E4  |    150| 51.3| 55.2|  0.8| E4 ->E3 ->D5 ->C5 ->E5 ->F3 ->C4 ->D3 
|F4  |     20| 51.2| 54.3|  0.8| F4 ->D6 ->D7 
|D6  |      1| 48.1| 48.1|  3.0| D6 
|C6  |      1| 46.0| 46.0|  2.3| C6 
|C3  |      1| 44.4| 44.4|  1.8| C3 
   A  B  C  D  E  F  G  H  J 
 9 .  .  .  .  .  .  .  .  .  9
 8 .  .  .  .  .  .  .  .  .  8
 7 .  .  .  .  .  .  .  .  .  7
 6 .  .  .  .  .  X  .  .  .  6
 5 .  .  . [X] .  .  .  .  .  5
 4 .  .  .  O  .  .  .  .  .  4
 3 .  .  .  .  .  .  .  .  .  3
 2 .  .  .  .  .  .  .  .  .  2
 1 .  .  .  .  .  .  .  .  .  1
   A  B  C  D  E  F  G  H  J 
```

思想记录的内容如下。

- `move count` 移动计数
- `left time` 剩余时间
- `evaluated` 以此想法评估的board数量
- `move` 选手步数
- `count` 搜索数
- `rate` 选手的胜率
- `value` 选手开始时的评估值
- `prob` 选手走棋的概率
- `best sequence` 最佳顺序

pyaq.py的命令行选项如下。

- `--cpu` 仅使用CPU
- `--learn` 从游戏记录中学习
- `--self` 在控制台上进行自我比试
- `--random` 随机play
- `--quick` 选择可能性最高的（不搜索）
- `--clean` 中止（仅在搜索时）
- `--main_time=600` 设定总时间10分钟
- `--byoyomi=10` 将读数时间设为10秒

### 4.在GoGui上玩

人谁不学习，学到的数据文件`Pyaq/pre_train`中`model.ckpt`的`Pyaq/`被复制到请。

使用[GoGui](https://sourceforge.net/projects/gogui/files/gogui/1.4.9/)与AI一起[玩](https://sourceforge.net/projects/gogui/files/gogui/1.4.9/)。
将菜单>游戏>面板尺寸设置为“ 9”后，从菜单>程序>新程序中注册“命令”和“工作目录”。

![resister](https://user-images.githubusercontent.com/32036527/36086431-acdf1168-100f-11e8-9127-adc138b3fa3d.png)  

启动后，您可以使用GUI。可以从菜单>工具> GTP Shell中查看思想日志。

![top](https://user-images.githubusercontent.com/32036527/36086412-90005ab6-100f-11e8-912b-fdf30c61b2ef.png)   

https://twitter.com/ymg_aq)

## 附录:
### 围棋英文术语:

- 贴目 (komi)
- 气 (*liberty*) 
- 叫吃 (*atari*) 
- 劫(Ko)

### 规则说明:

**让子**:是围棋的一种对弈制度，指持黑子的一方先在棋盘上摆上一定数目的子之後，再由执白子的一方开始下

**贴目**:指黑方由于先手，在布局上占有一定的优势，为了公平起见，在最后计算双方所占地的多少时，黑棋必须扣减一定的[目数](https://baike.baidu.com/item/目数)或子数。

**劫**:如图，轮[白下](https://www.baidu.com/s?wd=白下&tn=SE_PcZhidaonwhc_ngpagmjz&rsv_dl=gh_pc_zhidao)子时，白在A位提黑一子；此时，黑不能立即回提A位的白子，必须寻找劫材，即在别处下一着，待白方应后，再回提A位的白子。但是，并非所有的劫材都会导致对方应一手，在价值判断取舍的情况下，对方也可能不应劫而解消劫争，“劫胜”也叫“消劫”。

![](https://gss0.baidu.com/94o3dSag_xI4khGko9WTAnF6hhy/zhidao/pic/item/35a85edf8db1cb1301064346d054564e92584b73.jpg)





### License

[MIT License](https://github.com/ymgaq/Pyaq/blob/master/LICENSE)

Author:

<a href="https://github.com/Freedomisgood">
    <img src="https://avatars3.githubusercontent.com/u/31088082?s=40&v=4" width="50px">
</a><a href="https://github.com/HotPotAndMe">
    <img src="https://avatars3.githubusercontent.com/u/44315782?s=400&v=4" width="50px">
</a>

Thanks to origin Author: [Yu Yamaguchi](