#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from sys import stderr
from board import *
import numpy as np


# sgf棋谱文件读取
class sgf_data(object):

    def __init__(self):
        self.size = BSIZE  # 棋盘大小
        self.komi = KOMI  # 贴目
        self.handicap = 0  # 让子
        self.result = 0  # 结局
        self.history = []  # 历史记录
        self.move_cnt = 0  # 步数统计

    def sgf2ev(self, v_sgf):
        """
        将sgf内容转换为ev格式
        :param v_sgf:
        :return:
        """
        if len(v_sgf) != 2:
            return (self.size + 2) ** 2
        labels = "abcdefghijklmnopqrs"
        x = labels.find(v_sgf[0]) + 1
        y = labels.find(v_sgf[1]) + 1
        return x + (self.size + 1 - y) * (self.size + 2)

    def import_file(self, file_path):
        """
        解析单个sgf文件内容
        :param file_path: 单个文件的文件名
        :return:
        """
        f = open(file_path, 'r', encoding='utf-8')
        lines = f.readlines()
        for line in lines:
            str = line.rstrip("\n")
            while len(str) > 3:
                open_br = str.find("[")
                close_br = str.find("]")
                if open_br < 0 or close_br < 0:
                    break
                elif close_br == 0:
                    str = str[close_br + 1:]
                    continue

                key = str[0:open_br].lstrip(";")
                val = str[open_br + 1:close_br]

                if key == "SZ":
                    self.size = int(val)
                elif key == "KM":
                    self.komi = float(val)
                elif key == "HA":
                    self.handicap = int(val)
                elif key == "RE":
                    if val.find("B") >= 0:
                        self.result = 1
                    elif val.find("W") >= 0:
                        self.result = -1
                    else:
                        self.result = 0
                elif key == "B" or key == "W":
                    self.history.append(self.sgf2ev(val))
                    self.move_cnt += 1

                str = str[close_br + 1:]
        if self.result == 0 and len(self.history) >= 2:
            pass_ = (self.size + 2) ** 2
            if self.history[-1] != pass_ or self.history[-2] != pass_:
                self.result = 1 if len(self.history) % 2 == 1 else -1


def import_sgf(dir_path):
    """
    读取目录下的所有sgf文件,训练learn.py中需要读取
    :param dir_path: sgf文件目录
    :return: list
    """
    dir_path += "/*.sgf"
    file_list = glob.glob(dir_path)
    sd_list = []
    # b = Board()
    for f in file_list:
        sd_list.append(sgf_data())
        sd_list[-1].import_file(f)

    #         b.clear()
    #         for v in sd_list[-1].history:
    #             err = b.play(v, not_fill_eye=False)
    #             if err:
    #                 stderr.write("file %d\n" % len(sd_list))
    #                 b.showboard()
    #                 stderr.write("move=(%d,%d)\n" % ev2xy(v))
    #                 raw_input()

    #         if len(sd_list) % 5000 == 0:
    #             stderr.write(".")

    return sd_list


def sgf2feed(sgf_list):
    """
    将读入的棋谱信息,进行对战
    :param sgf_list: 棋谱信息
    :return: feature, move, result
    """
    total_cnt = 0
    for s in sgf_list:
        total_cnt += s.move_cnt

    feature = np.zeros((total_cnt, BVCNT, 7), dtype=np.uint8)
    move = np.zeros((total_cnt, BVCNT + 1), dtype=np.uint8)
    result = np.zeros((total_cnt), dtype=np.int8)

    train_idx = 0
    # 声明一个对战棋盘
    b = Board()
    for s in sgf_list:
        if s.size != BSIZE or s.handicap != 0:
            continue
        b.clear()
        for v in s.history:
            feature[train_idx] = b.feature
            move[train_idx, ev2rv(v)] = 1
            result[train_idx] = s.result * (2 * b.turn - 1)

            b.play(v, False)
            train_idx += 1

    return feature, move, result
