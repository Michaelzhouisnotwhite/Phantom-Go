#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
import sys
from board import *
import gtp
import learn
import search

if __name__ == "__main__":
    args = sys.argv

    launch_mode = 0  # 0: gtp, 1: self, 2: learn
    byoyomi = 5.0  # 读秒
    main_time = 0.0  # 总时间
    quick = False  # 快速走子设置
    random = False  # 随机落子设置
    clean = False  # GTP通信相关设置
    use_gpu = True  # 使用GPU设置

    # 只有额外加参数才会进行修改
    for arg in args:
        if arg.find("self") >= 0:
            launch_mode = 1
        elif arg.find("learn") >= 0:
            launch_mode = 2
        elif arg.find("quick") >= 0:
            quick = True
        elif arg.find("random") >= 0:
            random = True
        elif arg.find("clean") >= 0:
            clean = True
        elif arg.find("main_time") >= 0:
            main_time = float(arg[arg.find("=") + 1:])
        elif arg.find("byoyomi") >= 0:
            byoyomi = float(arg[arg.find("=") + 1:])
        elif arg.find("cpu") >= 0:
            use_gpu = False

    if launch_mode == 0:
        gtp.call_gtp(main_time, byoyomi, quick, clean, use_gpu)

    elif launch_mode == 1:
        b = Board()
        if not random:
            # 读取训练模型，声明tree对象
            tree = search.Tree("model.ckpt", use_gpu)
            tree.main_time = main_time

        # 下棋主循环
        while b.move_cnt < BVCNT * 2:
            # 记录上一步走的棋，来判断游戏是否结束
            prev_move = b.prev_move
            if random:
                # 随机下一步
                move = b.random_play()
            elif quick:
                # 得到棋盘评价最高的点，选取该点
                # 返回两行，一行策略，一行价值
                move = rv2ev(np.argmax(tree.evaluate(b)[0][0]))
                print(move)
                b.play(move, False)
            else:
                # 通过搜索得到策略
                move, _ = tree.search(b, 10, clean=clean, ponder=True)
                b.play(move, False)

            # 每步下完以后进行展示
            b.showboard()
            if prev_move == PASS and move == PASS:
                # 当双方都PASS时，游戏结束，此时跳出while循环
                break

        # 复制当前局势,然后随机下棋256次,输出其中最多能赢多少子-->实质就是MCTS中算某结点胜利的次数
        score_list = []
        b_cpy = Board()

        # 模拟256次
        for i in range(256):
            b.copy(b_cpy)
            b_cpy.rollout(show_board=False)
            score_list.append(b_cpy.score())

        # 选出得分表中出现最多次的得分
        # [(74.0, 25), (-88.0, 15), (10.0, 13), (16.0, 11), (-2.0, 11), (4.0, 9), (-18.0, 9), (-16.0, 8), (6.0, 7),
        #  (8.0, 7), (14.0, 6), (22.0, 6), (-28.0, 6), (-26.0, 6), (-24.0, 6), (-6.0, 6), (2.0, 5), (-48.0, 5),
        #  (-22.0, 5), (-12.0, 5),(0.0, 4), (24.0, 4), (26.0, 4), (-20.0, 4), (-8.0, 4), (-4.0, 4), (20.0, 3),
        #  (-56.0, 3), (-46.0, 3), (-44.0, 3), (-40.0, 3), (-38.0, 3), (-36.0, 3), (-34.0, 3), (-32.0, 3), (-30.0, 3),
        #  (28.0, 2), (30.0, 2), (32.0, 2), (36.0, 2), (44.0, 2), (48.0, 2), (-54.0, 2), (-42.0, 2), (-10.0, 2),
        # (34.0, 1), (38.0, 1), (42.0, 1), (46.0, 1), (50.0, 1), (-72.0, 1), (-62.0, 1), (-60.0, 1), (-58.0, 1),
        #  (-52.0, 1), (-50.0, 1), (56.0, 1), (-14.0, 1)]
        score = Counter(score_list).most_common(1)[0][0]
        if score == 0:
            result_str = "Draw"
        else:
            winner = "B" if score > 0 else "W"
            result_str = "%s+%.1f" % (winner, abs(score))
        sys.stderr.write("result: %s\n" % result_str)

    else:  # launch_mode == 2、Learn:
        path = input('input the path of learned sgfs')
        learn.learn(3e-4, 0.5, sgf_dir="{}".format(path), use_gpu=use_gpu, gpu_cnt=1)
