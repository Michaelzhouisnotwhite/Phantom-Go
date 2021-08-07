import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import numpy as np
from play.utils import ChessGrand  # NOQA: E402
from collections import deque


class SideBoard(object):
    chess_board: np.ndarray
    prev_history: list
    move_cnt: int
    around_pos: list
    ko: int
    PLAY_ILLEGAL = -11

    def __init__(self) -> None:
        self.chess_board = np.full(ChessGrand.EBVCNT, ChessGrand.BOARDER)
        self.rv_list = [self.rv2ev(i) for i in range(ChessGrand.BVCNT)]
        self.side = ChessGrand.BLACK

        self.init_chessboard()
        pass

    def init_chessboard(self):
        self.chess_board[self.rv_list] = 2
        self.prev_history = deque(maxlen=2)
        self.move_cnt = 0
        self.around_pos = [-1, -ChessGrand.EBSIZE, 1, ChessGrand.EBSIZE]
        self.ko = ChessGrand.VNULL

    def switch_side(self):
        self.side = int(self.side == 0)

    @property
    def opposite_side_color(self):
        return int(self.side == 0)
    
    def play_side(self, vector: int = ChessGrand.INVALID, x: int = ChessGrand.INVALID, y: int = ChessGrand.INVALID, guess=False):
        if not self.is_legal(vector=vector):
            return SideBoard.PLAY_ILLEGAL
        if vector == ChessGrand.PASS:
            pass
        else:
            self.prev_history.appendleft(np.copy(self.chess_board))
            self.chess_board[vector] = self.side
        pass

    def is_legal(self, vector: int = ChessGrand.INVALID, x: int = ChessGrand.INVALID, y: int = ChessGrand.INVALID) -> bool:
        """判断生成的棋子有无重复

        Args:
            vector (int, optional): 向量坐标. Defaults to ChessGrand.INVALID.
            x (int, optional): x坐标. Defaults to ChessGrand.INVALID.
            y (int, optional): y坐标. Defaults to ChessGrand.INVALID.
        Return:
            bool
        """
        if self.chess_board[vector] != ChessGrand.EMPTY:
            return False
        return True

    def illegal_remove(self, vector: int):
        self.chess_board[vector] = self.opposite_side_color
        pass

    def take_remove(self, vector: int):
        for pos in self.around_pos:
            if (pos + vector) in self.rv_list:
                if (pos + vector) == self.ko:
                    continue
                self.chess_board[pos + vector] = self.opposite_side_color
        
        self.chess_board[vector] = ChessGrand.EMPTY
        self.ko = vector
        pass
    
    @property
    def board_now(self):
        board = np.copy(self.chess_board).reshape((11, 11))
        return board

    @staticmethod
    def rv2ev(rv):
        """
        更新坐标索引起点=>0-8向量转化为1-9向量
        12 - 108
        :param rv:
        :return:
        """
        if rv == ChessGrand.BVCNT:
            return ChessGrand.PASS
        return rv % ChessGrand.BSIZE + 1 + (rv // ChessGrand.BSIZE + 1) * ChessGrand.EBSIZE


if __name__ == "__main__":
    b = SideBoard()
    print(b.board_now)
    
    b.play_side(46)
    b.play_side(47)
    b.play_side(48)
    b.play_side(49)
    
    print(b.board_now)
    
    b.take_remove(46)
    
    print(b.board_now)
    pass
