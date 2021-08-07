"""
@author: Michael
@Date: 2021-07-24
"""
from io import TextIOWrapper
import os
from tkinter.constants import NO
from typing import Optional, Union
workdir = os.path.abspath(os.path.dirname(__file__))


class __SoundEffectPath(object):
    __sound_dir = os.path.join(workdir, "sound")

    @property
    def move(self):
        """get sound effect: move

        Returns:
            str: path of "move.wav"
        """
        return os.path.join(self.__sound_dir, "move.wav")

    @property
    def defeat(self):
        """
        sound effect: defeat
        """
        pass

    @property
    def win(self):
        """
        sound effect: win
        """
        pass


class LogFile(object):
    file_path = os.path.join(workdir, "log.txt")
    log_file: TextIOWrapper

    def __init__(self, filename: Optional[str] = None) -> None:
        if filename is not None:
            self.file_path = os.path.join(workdir, filename)
            
        if os.path.exists(self.file_path):
            self.log_file = open(self.file_path, mode='a')
        else:
            self.log_file = open(self.file_path, mode='w')
        self.writelines("####  a new round  ######")

    def __del__(self):
        self.log_file.close()

    def writelines(self, log: str):
        self.log_file.write(log)
        self.log_file.write("\n")

    def write(self, log: str):
        self.log_file.write(log)


class __ImagePath(object):
    __img_dir = os.path.join(workdir, "img")

    @property
    def nine_road_chessboard(self):
        """chessboard

        Returns:
            str: path of chessboard 9x9
        """
        return os.path.join(self.__img_dir, "Goban_9x9_new.png")

    @property
    def white_piece(self):
        return os.path.join(self.__img_dir, "white.png")

    @property
    def black_piece(self):
        return os.path.join(self.__img_dir, "black.png")


ImagePath = __ImagePath()
SoundEffectPath = __SoundEffectPath()


class OperationMode:
    class Remove:
        """
        移除棋子模式
        """
        ILLEGAL_REMOVE = 1001
        TAKE_REMOVE = 1002
        SIMPLE_REMOVE = 1003

    class Draw:
        """
        绘制棋子模式
        """
        DRAW_WITE_PIECE = 3304
        DRAW_BLACK_PIECE = 3305
        TAKE_TURNS = 3
        ONE_SIDE = 4


class Pos:
    x: int
    y: int

    def __init__(self, x, y) -> None:
        self.set_pos(x, y)

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, o: object) -> bool:
        if o.x == self.x and o.y == self.y:
            return True
        else:
            return False

    def __sub__(self, o: object) -> int:
        return abs(self.x - o.x) + abs(self.y - o.y)

    def copy(self):
        tmp = Pos()
        tmp.x = self.x
        tmp.y = self.y
        return tmp

    def __copy__(self):
        tmp = Pos()
        tmp.x = self.x
        tmp.y = self.y
        return tmp


class ChessAttr:
    class Board:
        # --------Qwidget棋盘宽高-----------
        WIDTH = 430
        HEIGHT = 430
        # -------------------
        MARGIN = 24  # 窗口边缘宽度
        # 每格宽度
        GRID = (WIDTH - 2 * MARGIN) / 8
        BSIZE = 9  # board size

    EBSIZE = Board.BSIZE + 2  # extended board size
    BVCNT = Board.BSIZE**2  # vertex count
    EBVCNT = EBSIZE**2  # extended vertex count

    class Piece:
        # 棋子大小
        PIECE = 34
        EMPTY = 0
        BLACK = 1
        WHITE = 2

    # --------------------
    # 两个越界的位置规定为PASS-81和unvaild-82
    # pass
    PASS = EBVCNT
    # invalid position
    VNULL = EBVCNT + 1


class PieceAttr:
    piece_no: int
    pos: Pos
    color: int

    def __init__(self, piece_no: int, pos: Pos, color=None) -> None:
        self.piece_no = piece_no
        self.pos = pos
        self.color = color

    def __sub__(self, other):
        tmp = PieceAttr(other.piece_no, other.pos)
        if other.color == ChessAttr.Piece.BLACK:
            tmp.color = ChessAttr.Piece.WHITE
        elif other.color == ChessAttr.Piece.WHITE:
            tmp.color = ChessAttr.Piece.BLACK

        return tmp

    def copy(self):
        tmp = PieceAttr(self.piece_no, self.pos, self.color)
        return tmp

    def __copy__(self):
        tmp = PieceAttr(self.piece_no, self.pos, self.color)
        return tmp


if __name__ == "__main__":
    a = OperationMode.Draw.DRAW_BLACK_PIECE
    if a in (OperationMode.Draw.DRAW_BLACK_PIECE, OperationMode.Draw.DRAW_WITE_PIECE):
        print(a)
    pass
