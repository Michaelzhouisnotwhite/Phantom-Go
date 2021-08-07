# -*- coding: utf-8 -*-


from sys import stderr
import numpy as np

BSIZE = 9  # board size
EBSIZE = BSIZE + 2  # extended board size
BVCNT = BSIZE ** 2  # vertex count
EBVCNT = EBSIZE ** 2  # extended vertex count

# 两个越界的位置规定为PASS-81和unvaild-82
# pass
PASS = EBVCNT
# invalid position
VNULL = EBVCNT + 1
# 贴目
KOMI = 7.0
# v的(右下左上)四个位置
dir4 = [1, EBSIZE, -1, -EBSIZE]
# v的(四个角)位置
diag4 = [1 + EBSIZE, EBSIZE - 1, -EBSIZE - 1, 1 - EBSIZE]

KEEP_PREV_CNT = 2
# 12当前黑白棋
# 3456前两次黑白棋
# 7当前棋色
FEATURE_CNT = KEEP_PREV_CNT * 2 + 3  # 7

x_labels = "ABCDEFGHJKLMNOPQRST"


def ev2xy(ev):
    """
    e.g.ev=12==>（1,1）;
    ev=13==>(2,1)
    从行到列→↓
    :param ev:
    :return:
    """
    return ev % EBSIZE, ev // EBSIZE


def xy2ev(x, y):
    """
    将坐标转换成向量
    :param x:
    :param y:
    :return:
    """
    return y * EBSIZE + x


def rv2ev(rv):
    """
    更新坐标索引起点=>0-8向量转化为1-9向量
    12 - 108
    :param rv:
    :return:
    """
    if rv == BVCNT:
        return PASS
    return rv % BSIZE + 1 + (rv // BSIZE + 1) * EBSIZE


def ev2rv(ev):
    """
    将棋盘1-9向量==>0-8向量
    :param ev:
    :return:
    """
    if ev == PASS:
        return BVCNT
    return ev % EBSIZE - 1 + (ev // EBSIZE - 1) * BSIZE


def ev2str(ev):
    """
    将下棋位置转化为str
    :param ev:
    :return:
    """
    if ev >= PASS:
        return "pass"
    x, y = ev2xy(ev)
    return x_labels[x - 1] + str(y)


def str2ev(v_str):
    """
    字符形式信息转换为ev
    :param v_str:
    :return:
    """
    v_str = v_str.upper()
    if v_str == "PASS" or v_str == "RESIGN":  # 放弃
        return PASS
    else:
        x = x_labels.find(v_str[0]) + 1
        y = int(v_str[1:])
        return xy2ev(x, y)


rv_list = [rv2ev(i) for i in range(BVCNT)]


# 并查集？
class StoneGroup(object):

    def __init__(self):
        self.lib_cnt = VNULL  # liberty count(气的数目)
        self.size = VNULL  # stone size(该气的大小_包含棋子数)
        self.v_atr = VNULL  # liberty position if in Atari(在叫吃情况下的气-->劫)
        self.libs = set()  # set of liberty positions(气集合)

    def clear(self, stone=True):
        # clear as placed stone or empty
        self.lib_cnt = 0 if stone else VNULL  # 0或者121
        self.size = 1 if stone else VNULL
        self.v_atr = VNULL
        self.libs.clear()

    def add(self, v):
        # add liberty at v
        if v not in self.libs:
            self.libs.add(v)
            self.lib_cnt += 1
            self.v_atr = v

    def sub(self, v):
        # remove liberty at v
        if v in self.libs:
            self.libs.remove(v)
            self.lib_cnt -= 1

    def merge(self, other):
        """
        合并两个气
        :param other: StoneGroup对象
        :return:
        """
        # merge with aother stone group
        self.libs |= other.libs
        self.lib_cnt = len(self.libs)
        self.size += other.size
        if self.lib_cnt == 1:
            for lib in self.libs:
                self.v_atr = lib
                # 集合是升序的,所以会是最后一个


# 棋盘
class Board(object):
    """
    记录比赛信息的量
    注意: 没有全局变量记录当前局自己的颜色
    """
    def __init__(self):
        # 1-d array ([EBVCNT]) of stones or empty or exterior
        # 一维阵列([EBVCNT])的棋色、空、边界
        # 0: white 1: black
        # 2: empty 3: exterior(越界、边界)

        # color保存的是对战棋盘上可以直接观测到的信息
        self.color = np.full(EBVCNT, 3)
        # 对棋盘上气的统计
        self.sg = [StoneGroup() for _ in range(EBVCNT)]  # stone groups

        # 除了这两个量以外, 其他的量(clear函数中定义的)都是一些算法中需要记录、使用到的值
        self.id = None
        self.next = None
        self.prev_color = None
        self.ko = None
        self.turn = None
        self.move_cnt = None
        self.prev_move = None
        self.remove_cnt = None
        self.history = None
        self.clear()

    def clear(self):
        """
        实现初始化、重置
        :return: None
        """
        self.color[rv_list] = 2  # 将能下子的地方标记为空
        self.id = np.arange(EBVCNT)  # id of stone group(属于哪团气的)
        self.next = np.arange(EBVCNT)  # next position in the same group
        for i in range(EBVCNT):
            self.sg[i].clear(stone=False)
        self.prev_color = [np.copy(self.color) for _ in range(KEEP_PREV_CNT)]

        self.ko = VNULL  # illegal position due to Ko(劫)
        self.turn = 1  # black first
        self.move_cnt = 0  # move count
        self.prev_move = VNULL  # previous move
        self.remove_cnt = 0  # removed stones count(移掉子的数目)
        self.history = []  # 该局历史

    def copy(self, b_cpy):
        """
        实现对象的拷贝功能
        :param b_cpy: Board对象
        :return:
        """
        b_cpy.color = np.copy(self.color)
        b_cpy.id = np.copy(self.id)
        b_cpy.next = np.copy(self.next)
        for i in range(EBVCNT):
            b_cpy.sg[i].lib_cnt = self.sg[i].lib_cnt
            b_cpy.sg[i].size = self.sg[i].size
            b_cpy.sg[i].v_atr = self.sg[i].v_atr
            b_cpy.sg[i].libs |= self.sg[i].libs
        for i in range(KEEP_PREV_CNT):
            b_cpy.prev_color[i] = np.copy(self.prev_color[i])

        b_cpy.ko = self.ko
        b_cpy.turn = self.turn
        b_cpy.move_cnt = self.move_cnt
        b_cpy.prev_move = self.prev_move
        b_cpy.remove_cnt = self.remove_cnt

        for h in self.history:
            b_cpy.history.append(h)

    def remove(self, v):
        # remove stone group including stone at v
        """
        提子操作
        :param v:
        :return:
        """
        v_tmp = v
        while True:
            self.remove_cnt += 1
            self.color[v_tmp] = 2  # empty
            self.id[v_tmp] = v_tmp  # reset id
            for d in dir4:
                nv = v_tmp + d
                # add liberty to neighbor groups
                self.sg[self.id[nv]].add(v_tmp)
            v_next = self.next[v_tmp]
            self.next[v_tmp] = v_tmp
            v_tmp = v_next
            if v_tmp == v:
                break  # finish when all stones are removed

    def merge(self, v1, v2):
        # merge stone groups at v1 and v2
        """
        并查集，将两个group合并
        :param v1:
        :param v2:
        :return:
        """
        id_base = self.id[v1]
        id_add = self.id[v2]
        # 将add_group加到base_group
        if self.sg[id_base].size < self.sg[id_add].size:
            id_base, id_add = id_add, id_base  # swap
        self.sg[id_base].merge(self.sg[id_add])

        v_tmp = id_add
        while True:
            self.id[v_tmp] = id_base  # change id to id_base
            v_tmp = self.next[v_tmp]
            if v_tmp == id_add:
                break
        # swap next id for circulation
        self.next[v1], self.next[v2] = self.next[v2], self.next[v1]

    def place_stone(self, v):
        """
        落子,并更新board其他信息,判断是否连气、提子
        :param v: 位置0-120的一个点
        :return:
        """
        # 关键的还是self.color这个量,保存的是棋盘的信息
        self.color[v] = self.turn
        self.id[v] = v
        self.sg[self.id[v]].clear(stone=True)
        for d in dir4:
            nv = v + d
            if self.color[nv] == 2:
                self.sg[self.id[v]].add(nv)  # add liberty 增加该子的气数
            else:
                self.sg[self.id[nv]].sub(v)  # remove liberty 减少该子的气数

        # merge stone groups
        for d in dir4:
            nv = v + d
            if self.color[nv] == self.turn and self.id[nv] != self.id[v]:
                self.merge(v, nv)

        # remove opponent's stones
        self.remove_cnt = 0
        for d in dir4:
            nv = v + d
            # 是否为对方的棋子 且 对方该棋子没有气 了
            if self.color[nv] == int(self.turn == 0) and \
                    self.sg[self.id[nv]].lib_cnt == 0:
                self.remove(nv)

    def legal(self, v):
        """
        判断当前落子点是否合法
        :param v:
        :return:
        """
        # pass为合法
        if v == PASS:
            return True
        # 如果不为空、或者为劫(即劫争),则false
        elif v == self.ko or self.color[v] != 2:
            return False

        stone_cnt = [0, 0]
        atr_cnt = [0, 0]
        for d in dir4:  # [1, EBSIZE, -1, -EBSIZE]
            nv = v + d
            c = self.color[nv]
            # 如果有任意一个方向空.即不是眼,那么就可以下
            if c == 2:
                return True
            # 计算是否为眼
            elif c <= 1:
                stone_cnt[c] += 1
                if self.sg[self.id[nv]].lib_cnt == 1:
                    atr_cnt[c] += 1

        return (atr_cnt[int(self.turn == 0)] != 0 or
                atr_cnt[self.turn] < stone_cnt[self.turn])

    def eyeshape(self, v, pl):
        """
        当前v位置能否形成眼 or 是否会填眼?
        :param v: 位置
        :param pl: self.turn,当前player的颜色
        # int(pl == 0) 判断是否为pl相对颜色:如果传1黑,那么就是0白.
        :return: 是否能构成:bool
        """
        # 如果pass那么一定不能构成眼
        if v == PASS:
            return False
        for d in dir4:  # [1, EBSIZE, -1, -EBSIZE]
            c = self.color[v + d]
            # 一旦有位置是空的 or 对方的棋子? ,那么就不能形成眼==>也肯定填不了眼
            # ==> 如果一个子的四周有空的,那么这一步将不能构成眼==>也肯定填不了眼
            # --> 如果一个子的四周有对方的子的话,那么这步也肯定构成不了眼
            if c == 2 or c == int(pl == 0):
                return False

        # 在v位置大多都是己方子的时候，才可能形成眼
        # 记录四个角的情况，[白，黑，空，边界]
        diag_cnt = [0, 0, 0, 0]
        for d in diag4:  # [1 + EBSIZE, EBSIZE - 1, -EBSIZE - 1, 1 - EBSIZE]
            nv = v + d
            diag_cnt[self.color[nv]] += 1

        # 对方的子数 + 边界的个数
        wedge_cnt = diag_cnt[int(pl == 0)] + int(diag_cnt[3] > 0)
        if wedge_cnt == 2:
            for d in diag4:  # [1 + EBSIZE, EBSIZE - 1, -EBSIZE - 1, 1 - EBSIZE]
                nv = v + d
                # 1. 为对方的棋子
                # 2. 气数为1
                # 3. 顶点不为劫
                if self.color[nv] == int(pl == 0) and \
                        self.sg[self.id[nv]].lib_cnt == 1 and \
                        self.sg[self.id[nv]].v_atr != self.ko:
                    return True
        # 小于2为眼,如贴边、贴角
        return wedge_cnt < 2

    def play(self, v, not_fill_eye=True):
        """
        走子
        :param v: 位置
        :param not_fill_eye: 是否不填眼
        :return:
        """
        # 异常操作
        # 不合法返回1
        # 不想要填眼但是填了眼 返回2
        if not self.legal(v):
            return 1
        elif not_fill_eye and self.eyeshape(v, self.turn):
            return 2
        # 如果能走，且满足眼的要求
        else:
            for i in range(KEEP_PREV_CNT - 1)[::-1]:
                self.prev_color[i + 1] = np.copy(self.prev_color[i])
            self.prev_color[0] = np.copy(self.color)

            if v == PASS:
                self.ko = VNULL
            else:
                # 对棋盘的更新都在place_stone这个函数中
                self.place_stone(v)
                id = self.id[v]
                self.ko = VNULL
                # 如果提子了，那么这个位置将会被定义为劫,在下一步不能立马下在劫上
                # 1.移的子个数为1、
                # 2.该位置的sg气为1
                # 3.该位置的sg大小为1
                if self.remove_cnt == 1 and \
                        self.sg[id].lib_cnt == 1 and \
                        self.sg[id].size == 1:
                    # 劫的位置定义为，被叫吃的位置
                    self.ko = self.sg[id].v_atr

        # 一方下完后进行记录,并切换下子方
        self.prev_move = v
        self.history.append(v)
        self.turn = int(self.turn == 0)  # 实际是一个取反的作用
        self.move_cnt += 1

        return 0

    def random_play(self):
        """
        随机往空的位置下棋
        :return: v: int
        """
        empty_list = np.where(self.color == 2)[0]
        np.random.shuffle(empty_list)

        # 如果有子可以下
        for v in empty_list:
            if self.play(v, True) == 0:
                return v

        # 没子可下,那么PASS
        self.play(PASS)
        return PASS

    def score(self):
        """
        计算得分
        :return: int
        """
        # 记录黑白上方的目数
        stone_cnt = [0, 0]
        # 遍历所有棋盘位置(没有边界)
        for rv in range(BVCNT):
            # 程序主要的都是购过ev坐标来进行的
            v = rv2ev(rv)
            c = self.color[v]
            # 所占位置计分
            if c <= 1:
                stone_cnt[c] += 1
            # 争论位置
            else:
                # 统计v位置"十"周围信息
                nbr_cnt = [0, 0, 0, 0]
                for d in dir4:
                    nbr_cnt[self.color[v + d]] += 1
                # 如果白子数目>0 且 黑子数目为0, 那么这个位置算是白子的目
                if nbr_cnt[0] > 0 and nbr_cnt[1] == 0:
                    stone_cnt[0] += 1
                # 如果黑子数目>0 且 白子数目为0, 那么这个位置算是黑子的目
                elif nbr_cnt[1] > 0 and nbr_cnt[0] == 0:
                    stone_cnt[1] += 1
        print(stone_cnt)
        # 黑目-白目-黑贴白目
        return stone_cnt[1] - stone_cnt[0] - KOMI

    def rollout(self, show_board=False):
        """
        模拟随机下棋进行一句游戏
        :param show_board: 是否显示棋盘
        :return:
        """
        while self.move_cnt < EBVCNT * 2:
            prev_move = self.prev_move
            move = self.random_play()
            if show_board and move != PASS:
                stderr.write("\nmove count=%d\n" % self.move_cnt)
                self.showboard()
            # 当局游戏结束的条件
            if prev_move == PASS and move == PASS:
                break

    def showboard(self):
        """
        输出当前的棋盘
        :return: None
        """

        def print_xlabel():
            """
            打印棋盘坐标 A ... J
            :return: None
            """
            line_str = "  "
            for x in range(BSIZE):
                line_str += " " + x_labels[x] + " "
            stderr.write(line_str + "\n")

        print_xlabel()

        # 9, 8, ..., 1行:[ 9 .  .  .  .  .  .  .  .  .  9]
        for y in range(1, BSIZE + 1)[::-1]:
            line_str = str(y) if y >= 10 else " " + str(y)
            for x in range(1, BSIZE + 1):
                v = xy2ev(x, y)
                # 如果该v位置没有棋子,x_str == .
                x_str = " . "
                color = self.color[v]
                # 如果该v位置有棋子,x_str == O/X
                if color <= 1:
                    stone_str = "O" if color == 0 else "X"
                    # 特殊处理上一步的显示
                    if v == self.prev_move:
                        x_str = "[" + stone_str + "]"
                    else:
                        x_str = " " + stone_str + " "
                # 每行输出一次
                line_str += x_str
            line_str += str(y) if y >= 10 else " " + str(y)
            stderr.write(line_str + "\n")

        print_xlabel()
        stderr.write("\n")

    @property
    def feature(self):
        """
        提取棋盘特征，记忆上一次，上上次的棋路
        :return: feature_[rv_list, :]: 记录除去边界的所有棋子坐标
        """
        feature_ = np.zeros((EBVCNT, FEATURE_CNT), dtype=np.float)
        # shape:(121, 7)

        # 记录当前棋子的颜色 w:0 b:1
        my = self.turn

        # my棋子颜色的反向
        opp = int(self.turn == 0)

        # 第0列 棋盘中是否有和当前颜色相同的，将该位置记为True
        feature_[:, 0] = (self.color == my)
        # 第1列 棋盘中是否有和当前颜色相同的，将该位置记为True
        feature_[:, 1] = (self.color == opp)

        # (0+1)*2==3列、4开始--->(1+1)*2 + 1==5列、6结束
        # feature_将 2， 3， 4， 5列，分别找到黑棋和白棋位置，并记录为True
        for i in range(KEEP_PREV_CNT):
            feature_[:, (i + 1) * 2] = (self.prev_color[i] == my)  # self.prev_color: 两个(121, )的列表，记录棋盘
            feature_[:, (i + 1) * 2 + 1] = (self.prev_color[i] == opp)
        # 第6列 标记为当前棋子颜色
        feature_[:, FEATURE_CNT - 1] = my

        # 返回81行 rv_list:记录除去边界的棋盘棋盘索引
        return feature_[rv_list, :]

    def hash(self):
        """
        哈希算状态
        :return: hash_code
        """
        return (hash(self.color.tostring()) ^
                hash(self.prev_color[0].tostring()) ^ self.turn)

    def info(self):
        """
        返回一些MCTS中需要的信息
        :return: 当前状态，走子数，输出决策
        """
        # 空的位置 np.where返回是一个两个元素的元组，所以取第一个，第二个为空
        empty_list = np.where(self.color == 2)[0]
        # 可以下的策略
        cand_list = []
        # 找到合法且不是眼的坐标（所有可行点）
        for v in empty_list:
            if self.legal(v) and not self.eyeshape(v, self.turn):
                cand_list.append(ev2rv(v))
        cand_list.append(ev2rv(PASS))
        # 当前状态，走子数，输出决策
        return self.hash(), self.move_cnt, cand_list


if __name__ == '__main__':
    # [rv2ev(i) for i in range(BVCNT)]
    '''
    [[100 101 102 103 104 105 106 107 108]
     [ 89  90  91  92  93  94  95  96  97]
     [ 78  79  80  81  82  83  84  85  86]
     [ 67  68  69  70  71  72  73  74  75]
     [ 56  57  58  59  60  61  62  63  64]
     [ 45  46  47  48  49  50  51  52  53]
     [ 34  35  36  37  38  39  40  41  42]
     [ 23  24  25  26  27  28  29  30  31]
     [ 12  13  14  15  16  17  18  19  20]]
    '''
    '''
    '''
    b = Board()
    b.play(34)  # 黑
    b.play(100)  # 白

    b.play(35)  # 黑
    b.play(108)  # 白

    b.play(25)  # 黑
    b.play(20)  # 白

    b.play(14)  # 黑
    b.play(12)  # 白
    b.showboard()
    print(b.score())

    # b.rollout(True)
