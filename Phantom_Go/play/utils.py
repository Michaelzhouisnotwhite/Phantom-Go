

class ChessGrand:
    PASS = 122
    BLACK = 1
    WHITE = 0
    EMPTY = 2
    BOARDER = 3 # 边界
    BSIZE = 9  # 能下的棋盘大小
    EBSIZE = BSIZE + 2  # 棋盘加上边界
    BVCNT = BSIZE ** 2 # 能够下棋的坐标个数
    EBVCNT = EBSIZE ** 2 # 总共坐标个数
    INVALID = -1
    VNULL = 123
