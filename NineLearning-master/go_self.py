"""
@author: Michael
@version: 2021-07-20
"""

from collections import Counter
import sys
from board import *
import gtp
import learn
import search
# noinspection PyUnresolvedReferences
import tensorflow.compat.v1 as tf

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


def go_self():
    """
    1. 棋盘提子修改后输入
    2. 棋盘落子后不合法，需要重新生成新的落子位置
    3. 棋面只能有我方棋子
    *4.复盘后仍然能继续运行
    :return:
    """
    board = Board()
    tree = search.Tree("model.ckpt", use_gpu=False)
    # tree.main_time = 3

    while board.move_cnt < BVCNT * 2:
        prev_move = board.prev_move
        move, _ = tree.search(board, 0, clean=False, ponder=True)
        board.play(move, False)
        board.showboard()
        if prev_move == PASS and move == PASS:
            break

    score_list = []
    b_cpy = Board()

    # 模拟256次
    for i in range(256):
        board.copy(b_cpy)
        b_cpy.rollout(show_board=False)
        score_list.append(b_cpy.score())

    # 选出得分表中出现最多次的得分
    score = Counter(score_list).most_common(1)[0][0]
    if score == 0:
        result_str = "Draw"
    else:
        winner = "B" if score > 0 else "W"
        result_str = "%s+%.1f" % (winner, abs(score))
    sys.stderr.write("result: %s\n" % result_str)


if __name__ == '__main__':
    print(__doc__)
    go_self()
