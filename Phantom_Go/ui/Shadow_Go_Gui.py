"""
@author: Michael
@version: 2021-07-18
"""
# -*- coding: utf-8 -*-
from copy import deepcopy
import sys
from collections import deque
import time
from typing import Deque, Union, Tuple, Optional, List

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp, QThread
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMessageBox

sys.path.append("..")
sys.path.append(".")
sys.path.append("../play")
sys.path.append("../ui")

from play.board import *  # NOQA: E402
import play.search as search  # NOQA: E402
from ui.ChessAttributeDlg_GUi import *  # NOQA: E402
from ui.ReplayDlg_Gui import *  # NOQA: E402
from ui.utils import *  # NOQA: E402
from ui.QtThread import Timer  # NOQA: E402


class ReplayDict(object):
    mode: int
    pos: Pos
    color: int

    def __init__(self, mode: int, pos: Pos) -> None:
        self.mode = mode
        self.pos = pos


class ReplayList:
    index: int
    board_history_list: list
    OUT_OF_INDEX = -101
    pieces_used_history_list: List[Deque[PieceAttr]]
    pieces_unused_history_list: list

    def __init__(self) -> None:
        self.index = 0
        self.board_history_list = []
        self.pieces_unused_history_list: List[Deque[PieceAttr]] = []
        self.pieces_used_history_list = []

    def add(self, b: Board, pu: deque, puu: deque):
        """添加棋盘信息

        Args:
            b (Board): 算法输入棋盘
            pu (deque): 绘制棋盘Qlabel已用索引队列
            puu (deque): 绘制棋盘Qlabel未用索引队列
        """
        self.board_history_list.append(b.copy())
        self.pieces_used_history_list.append(deepcopy(pu))
        self.pieces_unused_history_list.append(deepcopy(puu))

        self.index = len(self.board_history_list) - 1

    def back(self) -> Union[Tuple[int, int, int], Tuple[Board, Deque[PieceAttr], deque]]:
        """撤销

        Returns:
            tuple: board, pieces, used pieces, unused pieces
            exeptions: ReplayList.OUT_OF_INDEX
        """
        if self.index <= 0:
            return ReplayList.OUT_OF_INDEX, \
                   ReplayList.OUT_OF_INDEX, \
                   ReplayList.OUT_OF_INDEX

        self.index -= 1
        return self.board_history_list[self.index], \
               deepcopy(self.pieces_used_history_list[self.index]), \
               deepcopy(self.pieces_unused_history_list[self.index])

    def undo(self) -> Union[Tuple[int, int, int], Tuple[Board, Deque[PieceAttr], deque]]:
        """重做

        Returns:
            tuple: board, pieces, used pieces, unused pieces
            exeptions: ReplayList.OUT_OF_INDEX
        """
        if self.index >= len(self.board_history_list) - 1:
            return ReplayList.OUT_OF_INDEX, \
                   ReplayList.OUT_OF_INDEX, \
                   ReplayList.OUT_OF_INDEX
        self.index += 1
        return self.board_history_list[self.index], \
               deepcopy(self.pieces_used_history_list[self.index]), \
               deepcopy(self.pieces_unused_history_list[self.index])


class MainWindowGui(QMainWindow):
    class TimerBtnState:
        ZERO: int = 0
        START: int = 1
        STOP: int = 2

    def __init__(self):
        super().__init__()
        # -------------------界面初始化----------------------------------
        self.replay_dlg = ReplayDlg(self)
        self.cadlg = ChessAttributeDlg(self)
        MainWindow = self
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.widget_chessboard = QtWidgets.QWidget(self.centralwidget)

        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.checkBox_gpu = QtWidgets.QCheckBox(self.groupBox)
        self.p_btn_set = QtWidgets.QPushButton(self.groupBox)
        self.lineEdit_1 = QtWidgets.QLineEdit(self.groupBox)
        self.label = QtWidgets.QLabel(self.groupBox)

        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.p_btn_ok = QtWidgets.QPushButton(self.groupBox_2)
        self.p_btn_cancel = QtWidgets.QPushButton(self.groupBox_2)

        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.textEdit = QtWidgets.QTextEdit(self.groupBox_3)
        self.textEdit_2 = QtWidgets.QTextEdit(self.groupBox_3)

        self.p_btn_rar = QtWidgets.QPushButton(self.centralwidget)
        self.p_btn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)

        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_4)
        self.p_btn_ok_2 = QtWidgets.QPushButton(self.groupBox_4)
        self.p_btn_cancel_2 = QtWidgets.QPushButton(self.groupBox_4)
        self.p_btn_cancel_3 = QtWidgets.QPushButton(self.groupBox_4)

        self.p_btn_time_1 = QtWidgets.QPushButton(self.centralwidget)
        self.p_btn_time_2 = QtWidgets.QPushButton(self.centralwidget)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)

        # ------------------------------------------------------------------
        # 棋子图片加载
        self.black = QPixmap(ImagePath.black_piece)
        self.white = QPixmap(ImagePath.white_piece)
        # 音效加载
        self.sound_piece = QSound(SoundEffectPath.move)

        self.piece_now = ChessAttr.Piece.BLACK
        self.step = 0  # 步数
        # 添加Qlabel作为棋子
        self.pieces = [QLabel(self) for i in range(81)]

        self.setupUi()

        # 已下棋子和未下棋子用队列装起来记录，方便删除和添加
        self.pieces_used: Deque[PieceAttr] = deque()
        self.pieces_unused: Deque[int] = deque()

        # 界面初始化操作

        self.history_s = None

        # 下棋模式
        self.mode = ONE_SIDE
        self.color = ChessAttr.Piece.BLACK

        self.board = None
        self.tree = None
        self.move: int = -1
        self.edit_board_record: deque[Board] = deque()

        self.history_board_record = ReplayList()

        self.take_pieces_list = deque()

        self.log_file = LogFile()
        # self.chess_record_log = LogFile("chess_record.sgf")
        self.back_history = deque()

        self.timer_1 = Timer()
        self.timer_2 = Timer()

        self.p_btn_time_1_push_state = MainWindowGui.TimerBtnState.ZERO
        self.p_btn_time_2_push_state = MainWindowGui.TimerBtnState.ZERO

        self.total_time_1 = 0.0
        self.total_time_2 = 0.0
        self.init_mainWindow()
        self.connect_all_controls()

    def init_mainWindow(self):
        self.init_pieces_deque()
        self.disable_btn(self.p_btn_rar)
        self.disable_btn(self.p_btn_ok)
        self.disable_btn(self.p_btn_stop)
        self.disable_btn(self.p_btn_ok_2)

        self.set_edit_digits_only(self.lineEdit_1)
        self.set_edit_digits_and_letter_only(self.lineEdit_3)
        self.set_edit_digits_and_letter_only(self.lineEdit_2)

        self.disable_btn(self.actionEditChessboard)
        self.board = Board()
        self.p_btn_time_1.setText("0.0")
        self.p_btn_time_2.setText("0.0")
        self.show_in_history(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def init_pieces_deque(self):
        for i in range(0, 81):
            self.pieces_unused.append(i)

    def allocate_piece(self, i, j) -> int:
        used_p = self.pieces_unused.popleft()
        for _, pd in enumerate(self.pieces_used):
            if pd.pos == Pos(i, j):
                print("Error, 棋子重叠！！")
                return -1
        self.pieces_used.append(PieceAttr(piece_no=used_p, pos=Pos(i, j)))
        return used_p

    def eat_piece(self, i: int, j: int, mode=OperationMode.Remove.SIMPLE_REMOVE) -> int:
        """吃掉指定逻辑坐标的棋子"""
        for _, pd in enumerate(self.pieces_used):
            if pd.pos == Pos(i, j):
                return_flag = 1
                if self.color != pd.color:
                    return_flag = 2
                self.pieces_unused.append(pd.piece_no)
                self.pieces_used.remove(pd)
                self.pieces[pd.piece_no].clear()
                if mode == OperationMode.Remove.ILLEGAL_REMOVE:
                    self.show_in_history("<illegal remove>")
                elif mode == OperationMode.Remove.TAKE_REMOVE:
                    self.show_in_history("<take remove>")
                elif mode == OperationMode.Remove.SIMPLE_REMOVE:
                    self.show_in_history("<simple remove>")
                self.show_in_history(self.pretty_print_coordinate(self.map2chessboard_coordinates(i, j)))
                self.show_in_history("--------------")

                return return_flag
        return -1

    def draw_piece(self, i, j, color=None):
        """下指定坐标的棋子"""
        index = self.allocate_piece(i, j)
        if index == -1:
            return

        x, y = self.map2pixel(i, j)
        if color is None:
            if self.mode == OperationMode.Draw.TAKE_TURNS:
                # 一次黑棋一次白棋
                if self.piece_now == ChessAttr.Piece.BLACK:
                    self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
                    self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.BLACK
                    self.piece_now = ChessAttr.Piece.WHITE
                else:
                    self.pieces[index].setPixmap(self.white)  # 放置白色棋子
                    self.piece_now = ChessAttr.Piece.BLACK
                    self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.WHITE
            elif self.mode == OperationMode.Draw.ONE_SIDE:
                if self.color == ChessAttr.Piece.BLACK:
                    self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
                    self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.BLACK
                elif self.color == ChessAttr.Piece.WHITE:
                    self.pieces[index].setPixmap(self.white)  # 放置白色棋子
                    self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.WHITE
        else:
            if color == ChessAttr.Piece.BLACK:
                self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
                self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.BLACK
            elif color == ChessAttr.Piece.WHITE:
                self.pieces[index].setPixmap(self.white)  # 放置白色棋子
                self.pieces_used[len(self.pieces_used) - 1].color = ChessAttr.Piece.WHITE

        self.pieces[index].setGeometry(x, y, ChessAttr.Piece.PIECE, ChessAttr.Piece.PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效
        # self.step += 1  # 步数+1

        chessboard_coordinate = self.map2chessboard_coordinates(i, j)
        self.show_in_history("placed:" + self.pretty_print_coordinate(chessboard_coordinate))
        self.show_in_history("-------------------------")
        winner = ChessAttr.Piece.EMPTY  # 判断输赢
        if winner != ChessAttr.Piece.EMPTY:
            # self.mouse_point.clear()
            self.game_over(winner)

    def pretty_print_coordinate(self, map_cdt: str):
        if self.color == ChessAttr.Piece.BLACK:
            color_flag = "B"
        elif self.color == ChessAttr.Piece.WHITE:
            color_flag = "W"
        map_cdt = "(" + map_cdt[0] + ", " + map_cdt[1] + ")" + "   " + color_flag + "[{}{}]".format(map_cdt[1].lower(), chr(int(map_cdt[0]) - 1 + ord('a')))
        return map_cdt

    def remove_all_piece(self):
        pass

    def map2pixel(self, i, j) -> Tuple[int, int]:
        """从逻辑坐标到 UI 上的绘制坐标的转换"""
        mh = self.menuBar.height()
        x = self.widget_chessboard.geometry().x()
        y = self.widget_chessboard.geometry().y()
        return ChessAttr.Board.MARGIN + j * ChessAttr.Board.GRID - ChessAttr.Piece.PIECE / 2 + x, ChessAttr.Board.MARGIN + i * ChessAttr.Board.GRID - ChessAttr.Piece.PIECE / 2 + mh + y  # 加上菜单栏的高度

    def ve2map(self, v) -> Tuple[int, int]:
        """从棋盘算法中的向量转换成棋盘逻辑坐标

        Args:
            v (int): 棋盘坐标向量
        return:
            (i, j)
        """
        def ev2xy(ev) -> Tuple[int, int]:
            """
            e.g.ev=12==>（1,1）;
            ev=13==>(2,1)
            从行到列→↓
            :param ev:
            :return:
            """
            return ev % 11, ev // 11

        tmp = ev2xy(v)
        return 9 - tmp[1], tmp[0] - 1

    def map2ve(self, i, j) -> int:
        """
        逻辑坐标转换成向量
        Args:
            i (int)
            j (int)

        Returns:
            int
        """
        x = j + 1
        y = 9 - i
        return y * EBSIZE + x

    def setupUi(self):
        """界面初始化"""
        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(971, 496)
        MainWindow.setMinimumSize(QtCore.QSize(971, 496))
        MainWindow.setMaximumSize(QtCore.QSize(971, 496))

        font = QtGui.QFont()
        font.setPointSize(12)
        MainWindow.setFont(font)

        self.centralwidget.setObjectName("centralwidget")
        self.widget_chessboard.setGeometry(QtCore.QRect(10, 10, 430, 430))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_chessboard.sizePolicy().hasHeightForWidth())

        self.widget_chessboard.setSizePolicy(sizePolicy)
        self.widget_chessboard.setMinimumSize(QtCore.QSize(430, 430))
        self.widget_chessboard.setMaximumSize(QtCore.QSize(430, 430))
        self.widget_chessboard.setStyleSheet("border-image: url(:/img/img/Goban_9x9_new.png);")
        self.widget_chessboard.setObjectName("widget_chessboard")
        self.groupBox.setGeometry(QtCore.QRect(460, 30, 221, 171))

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.checkBox_gpu.setGeometry(QtCore.QRect(30, 140, 61, 21))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.checkBox_gpu.setFont(font)
        self.checkBox_gpu.setObjectName("checkBox_gpu")
        self.p_btn_set.setGeometry(QtCore.QRect(130, 140, 51, 23))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_set.setFont(font)
        self.p_btn_set.setObjectName("p_btn_set")
        self.lineEdit_1.setGeometry(QtCore.QRect(130, 30, 71, 21))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(12)
        self.lineEdit_1.setFont(font)
        # self.lineEdit_1.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.label.setGeometry(QtCore.QRect(20, 30, 101, 20))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.groupBox_2.setGeometry(QtCore.QRect(460, 220, 221, 71))

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.lineEdit_2.setGeometry(QtCore.QRect(20, 30, 113, 20))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.p_btn_ok.setGeometry(QtCore.QRect(140, 30, 31, 21))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_ok.setFont(font)
        self.p_btn_ok.setObjectName("p_btn_ok")
        self.p_btn_cancel.setGeometry(QtCore.QRect(180, 30, 31, 21))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel.setFont(font)
        self.p_btn_cancel.setObjectName("p_btn_cancel")
        self.groupBox_3.setGeometry(QtCore.QRect(750, 20, 201, 351))

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(9)
        self.textEdit.setGeometry(QtCore.QRect(10, 20, 181, 171))
        self.textEdit.setFont(font)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        self.textEdit_2.setGeometry(QtCore.QRect(10, 200, 181, 141))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(9)
        self.textEdit_2.setFont(font)
        self.textEdit_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit_2.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setObjectName("textEdit_2")

        self.p_btn_rar.setGeometry(QtCore.QRect(460, 400, 131, 31))

        self.groupBox_4.setGeometry(QtCore.QRect(460, 310, 261, 71))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")

        self.lineEdit_3.setGeometry(QtCore.QRect(20, 30, 113, 20))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setObjectName("lineEdit_3")

        self.p_btn_ok_2.setGeometry(QtCore.QRect(140, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_ok_2.setFont(font)
        self.p_btn_ok_2.setObjectName("p_btn_ok_2")

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_rar.setFont(font)
        self.p_btn_rar.setObjectName("p_btn_rar")
        self.p_btn_stop.setGeometry(QtCore.QRect(610, 400, 61, 31))

        self.p_btn_cancel_2.setGeometry(QtCore.QRect(180, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel_2.setFont(font)
        self.p_btn_cancel_2.setObjectName("p_btn_cancel_2")

        self.p_btn_cancel_3.setGeometry(QtCore.QRect(220, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel_3.setFont(font)
        self.p_btn_cancel_3.setObjectName("p_btn_cancel_3")

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_stop.setFont(font)
        self.p_btn_stop.setObjectName("p_btn_stop")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        # noinspection PyAttributeOutsideInit
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 856, 23))
        self.menuBar.setObjectName("menuBar")
        # noinspection PyAttributeOutsideInit
        self.menu_operate = QtWidgets.QMenu(self.menuBar)
        self.menu_operate.setObjectName("menu_operate")
        # noinspection PyAttributeOutsideInit
        self.actionEditChessboard = QtWidgets.QAction(MainWindow)
        self.actionEditChessboard.setObjectName("actionEditChessboard")

        self.actionBack = QtWidgets.QAction(MainWindow)
        self.actionBack.setObjectName("actionBack")

        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")

        self.p_btn_time_1.setGeometry(QtCore.QRect(704, 410, 121, 31))
        self.p_btn_time_1.setObjectName("p_btn_time_1")

        self.p_btn_time_2.setGeometry(QtCore.QRect(834, 410, 121, 31))
        self.p_btn_time_2.setObjectName("p_btn_time_2")

        self.label_2.setGeometry(QtCore.QRect(700, 390, 81, 21))
        self.label_2.setObjectName("label_2")

        self.label_3.setGeometry(QtCore.QRect(830, 390, 81, 21))
        self.label_3.setObjectName("label_3")

        MainWindow.setMenuBar(self.menuBar)

        # self.actionReplay.setObjectName("actionReplay")
        # self.actionRerun.setObjectName("actionRerun")
        # self.actionCompleteReplay.setObjectName("actionCompleteReplay")
        # self.actionCancelReplay.setObjectName("actionCancelReplay")
        self.menu_operate.addAction(self.actionEditChessboard)
        self.menu_operate.addAction(self.actionBack)
        self.menu_operate.addAction(self.actionUndo)
        self.menuBar.addAction(self.menu_operate.menuAction())

        # self.menu_operate.addAction(self.actionReplay)
        # self.menu_operate.addAction(self.actionCompleteReplay)
        # self.menu_operate.addAction(self.actionCancelReplay)

        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

        MainWindow.setTabOrder(self.lineEdit_1, self.checkBox_gpu)
        MainWindow.setTabOrder(self.checkBox_gpu, self.p_btn_set)
        MainWindow.setTabOrder(self.p_btn_set, self.lineEdit_2)
        MainWindow.setTabOrder(self.lineEdit_2, self.p_btn_ok)
        MainWindow.setTabOrder(self.p_btn_ok, self.p_btn_cancel)
        MainWindow.setTabOrder(self.p_btn_cancel, self.p_btn_rar)
        MainWindow.setTabOrder(self.p_btn_rar, self.p_btn_stop)
        MainWindow.setTabOrder(self.p_btn_stop, self.textEdit)

        for piece in self.pieces:
            piece.setVisible(True)  # 图片可视
            piece.setScaledContents(True)  # 图片大小根据标签大小可变

    @staticmethod
    def set_edit_digits_only(edit):
        """设置编辑框只能输入数字"""
        reg = QRegExp("^\d+(\.\d+)?$")
        validator = QRegExpValidator(reg)
        edit.setValidator(validator)

    def game_over(self, winner):
        """判断游戏赢家（未完成）"""
        # 胜利
        if winner == ChessAttr.Piece.BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Continue?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 失败
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, 'You Lost!', 'Continue?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 若选择Yes，重置棋盘
        if reply == QMessageBox.Yes:
            self.piece_now = ChessAttr.Piece.BLACK
            self.mouse_point.setPixmap(self.black)
            self.step = 0
            self.close()
            for piece in self.pieces:
                piece.clear()
            self.chessboard.reset()
            self.update()
        # 若选择No时关闭窗口
        else:
            pass

    @staticmethod
    def set_edit_digits_and_letter_only(edit: QtWidgets.QLineEdit):
        reg = QRegExp("^[0-9]{1}[A-I]{1}$")
        validator = QRegExpValidator(reg)
        edit.setValidator(validator)

    def retranslate_ui(self):
        MainWindow = self
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "幻影围棋比赛界面"))
        self.groupBox.setTitle(_translate("MainWindow", "属性设置"))
        self.checkBox_gpu.setText(_translate("MainWindow", "GPU"))
        self.p_btn_set.setText(_translate("MainWindow", "Set"))
        self.label.setText(_translate("MainWindow", "Main Time:"))
        self.groupBox_2.setTitle(_translate("MainWindow", "提子"))
        self.p_btn_ok.setText(_translate("MainWindow", "√"))
        self.p_btn_cancel.setText(_translate("MainWindow", "×"))
        self.groupBox_3.setTitle(_translate("MainWindow", "操作历史"))
        self.p_btn_rar.setText(_translate("MainWindow", "Run a Round"))
        self.p_btn_stop.setText(_translate("MainWindow", "Stop"))
        self.menu_operate.setTitle(_translate("MainWindow", "操作"))
        self.groupBox_4.setTitle(_translate("MainWindow", "落子违规"))
        self.p_btn_ok_2.setText(_translate("MainWindow", "√"))
        self.p_btn_cancel_2.setText(_translate("MainWindow", "×"))
        self.p_btn_cancel_3.setText(_translate("MainWindow", "o"))
        self.actionEditChessboard.setText(_translate("MainWindow", "编辑棋盘"))
        self.actionBack.setText(_translate("MainWindow", "撤销"))
        self.actionUndo.setText(_translate("MainWindow", "重做"))
        self.label_2.setText(_translate("MainWindow", "计时器1"))
        self.label_3.setText(_translate("MainWindow", "计时器2"))

    def do_model(self):
        self.show()

    def connect_all_controls(self):
        self.p_btn_rar.clicked.connect(self.click_btn_rar) # run a round按钮
        self.p_btn_set.clicked.connect(self.click_btn_set) # set
        self.p_btn_ok.clicked.connect(self.click_btn_ok)
        self.p_btn_stop.clicked.connect(self.click_btn_stop)
        self.p_btn_cancel.clicked.connect(self.click_btn_cancel)
        self.actionEditChessboard.triggered.connect(self.clicked_action_edit_chessboard)
        self.p_btn_ok_2.clicked.connect(self.click_btn_ok_2)
        self.p_btn_cancel_2.clicked.connect(self.click_btn_cancel_2)
        self.p_btn_cancel_3.clicked.connect(self.click_btn_cancel_3)

        self.actionBack.triggered.connect(self.clicked_action_back)
        self.actionUndo.triggered.connect(self.clicked_action_undo)

        self.p_btn_time_1.clicked.connect(self.clicked_btn_timer_1)
        self.p_btn_time_2.clicked.connect(self.clicked_btn_timer_2)

        self.timer_1.sinOut.connect(self.set_btn_time_1_text)
        self.timer_2.sinOut.connect(self.set_btn_time_2_text)

    def clicked_action_back(self):
        board, pieces_used, pieces_unused = self.history_board_record.back()
        if board == ReplayList.OUT_OF_INDEX:
            self.disable_btn(self.actionBack)
            return
        self.enable_btn(self.actionUndo)
        self.board = board
        self.pieces_used = pieces_used
        self.pieces_unused = pieces_unused

        for p in self.pieces:
            p.clear()

        for _, pd in enumerate(self.pieces_used):
            if pd.color == ChessAttr.Piece.BLACK:
                self.pieces[pd.piece_no].setPixmap(self.black)  # 放置白色棋子
                self.piece_now = ChessAttr.Piece.BLACK
            if pd.color == ChessAttr.Piece.WHITE:
                self.pieces[pd.piece_no].setPixmap(self.white)  # 放置白色棋子
                self.piece_now = ChessAttr.Piece.WHITE

            x, y = self.map2pixel(pd.pos.x, pd.pos.y)
            self.pieces[pd.piece_no].setGeometry(x, y, ChessAttr.Piece.PIECE, ChessAttr.Piece.PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效

        self.show_in_history("--back--")

    def clicked_action_undo(self):
        board, pieces_used, pieces_unused = self.history_board_record.undo()
        if board == ReplayList.OUT_OF_INDEX:
            self.disable_btn(self.actionUndo)
            return
        self.enable_btn(self.actionBack)
        self.board = board
        self.pieces_used = pieces_used
        self.pieces_unused = pieces_unused
        for _, pd in enumerate(self.pieces_used):
            if pd.color == ChessAttr.Piece.BLACK:
                self.pieces[pd.piece_no].setPixmap(self.black)  # 放置白色棋子
                self.piece_now = ChessAttr.Piece.BLACK
            if pd.color == ChessAttr.Piece.WHITE:
                self.pieces[pd.piece_no].setPixmap(self.white)  # 放置白色棋子
                self.piece_now = ChessAttr.Piece.WHITE

            x, y = self.map2pixel(pd.pos.x, pd.pos.y)
            self.pieces[pd.piece_no].setGeometry(x, y, ChessAttr.Piece.PIECE, ChessAttr.Piece.PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效

        self.show_in_history("--undo--")

    def click_btn_cancel_3(self):
        text = self.lineEdit_3.text()
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        flag = self.eat_piece(i, j)
        self.enable_btn(self.p_btn_rar)
        if flag == -1:
            print("该位置没有棋子")
            return

        self.board.illegal_play(self.map2ve(i, j))
        self.history_board_record.add(self.board, self.pieces_used, self.pieces_unused)

    def clicked_action_edit_chessboard(self):
        self.show_in_history("<Edit mode on>")

        redlg = ReplayDlg(self)
        redlg.Signal_TwoParameter_1.connect(self.redlg_click_btn_ok)
        redlg.Signal_OneParameter_2.connect(self.redlg_click_btn_ok_2)
        redlg.Signal_OneParameter_4.connect(self.redlg_click_btn_ok_3)
        redlg.Signal_OneParameter_Cancel.connect(self.redlg_click_btn_cancel)

        self.edit_board_record.clear()
        ret = redlg.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            self.redlg_close()
        else:
            for index, edr in enumerate(self.edit_board_record):
                pass

    def redlg_close(self):
        self.show_in_history("</Edit mode off>")
        if self.p_btn_set.isEnabled():
            return
        for index, edr in enumerate(self.edit_board_record):
            if edr.mode == self.color2operation_color(self.color):
                self.board.play_my_side(self.map2ve(edr.pos.x, edr.pos.y), guess=False)
                self.board.move_cnt += 1
            elif edr.mode == OperationMode.Remove.ILLEGAL_REMOVE:
                self.board.illegal_remove(self.map2ve(edr.pos.x, edr.pos.y))
            elif edr.mode == OperationMode.Remove.TAKE_REMOVE:
                self.board.take_remove(self.map2ve(edr.pos.x, edr.pos.y))

    def redlg_click_btn_cancel(self, text: QtWidgets.QLineEdit.text):
        """获得编辑棋盘对话框删除棋子的坐标

        Args:
            text (QtWidgets.QLineEdit.text): 坐标
        """
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        flag = self.eat_piece(i, j, mode=OperationMode.Remove.SIMPLE_REMOVE)
        if flag == -1:
            print("该位置没有棋子")
        else:
            for index, edr in enumerate(self.edit_board_record):
                if edr.pos == Pos(i, j):
                    self.edit_board_record.remove(edr)
                    break

    def redlg_click_btn_ok_3(self, text: QtWidgets.QLineEdit.text):
        """获得编辑棋盘对话框落子违规坐标
        落子违规当前颜色的棋子
        Args:
            text (QtWidgets.QLineEdit.text): 坐标
        """
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        flag = self.eat_piece(i, j, mode=OperationMode.Remove.ILLEGAL_REMOVE)
        self.edit_board_record.append(ReplayDict(OperationMode.Remove.ILLEGAL_REMOVE, Pos(i, j)))
        if flag == -1:
            print("该位置没有棋子")

    @staticmethod
    def color2operation_color(color: int):
        if color == ChessAttr.Piece.BLACK:
            return OperationMode.Draw.DRAW_BLACK_PIECE
        elif color == ChessAttr.Piece.WHITE:
            return OperationMode.Draw.DRAW_WITE_PIECE

    @staticmethod
    def operation_color2color(color: int):
        if color == OperationMode.Draw.DRAW_BLACK_PIECE:
            return ChessAttr.Piece.BLACK
        elif color == OperationMode.Draw.DRAW_WITE_PIECE:
            return ChessAttr.Piece.WHITE

    def redlg_click_btn_ok(self, text: QtWidgets.QLineEdit.text, color: int):
        """获得编辑棋盘对话框落子坐标

        Args:
            text (QtWidgets.QLineEdit.text): 落子位置
            color (int): 颜色
        """
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        self.draw_piece(i, j, color)
        self.edit_board_record.append(ReplayDict(self.color2operation_color(color=color), Pos(i, j)))

    def redlg_click_btn_ok_2(self, text: QtWidgets.QLineEdit.text):
        """获得编辑棋盘对话框提子坐标

        Args:
            text (QtWidgets.QLineEdit.text): 坐标
        """
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        flag = self.eat_piece(i, j, mode=OperationMode.Remove.TAKE_REMOVE)
        if flag == -1:
            print("该位置没有棋子")
            return
        if flag == 1:
            self.edit_board_record.append(ReplayDict(OperationMode.Remove.TAKE_REMOVE, Pos(i, j)))

    def click_btn_ok_2(self):
        target_coordinate = self.lineEdit_3.text()
        if target_coordinate == "":
            return
        flag = self.eat_piece(self.chessboard_coordinates2map(target_coordinate)[0], self.chessboard_coordinates2map(target_coordinate)[1], mode=OperationMode.Remove.ILLEGAL_REMOVE)
        if flag == -1:
            print("该位置没有棋子")
            return
        i, j = self.chessboard_coordinates2map(target_coordinate)
        self.board.illegal_remove(self.map2ve(i, j))
        self.board.move_cnt -= 1
        self.lineEdit_3.clear()
        self.enable_btn(self.p_btn_rar)

        self.history_board_record.add(self.board, self.pieces_used, self.pieces_unused)

    def click_btn_cancel_2(self):
        """当落子未违规时，点击按钮 “x”
        """
        target_coordinate = self.lineEdit_3.text()
        self.enable_btn(self.p_btn_rar)
        if target_coordinate == "":
            return
        i, j = self.chessboard_coordinates2map(target_coordinate)
        self.move = self.map2ve(i, j)
        self.board.play_my_side(self.move)
        self.lineEdit_3.clear()
        self.board.move_cnt += 1

        self.history_board_record.add(self.board, self.pieces_used, self.pieces_unused)

    def click_btn_stop(self):
        self.disable_btn(self.p_btn_rar)
        self.enable_btn(self.p_btn_set)
        self.disable_btn(self.p_btn_stop)
        self.disable_btn(self.p_btn_ok)

    def click_btn_cancel(self):
        self.lineEdit_2.clear()

    def click_btn_rar(self):
        """当按下run的时候"""
        self.disable_btn(self.p_btn_rar)

        take_list = []
        for pos in self.take_pieces_list:
            tmp_list = []
            flag = 0
            for pp in self.take_pieces_list:
                if pp - pos == 1:
                    flag = 1
            if flag == 0:
                self.board.take_remove(v=self.map2ve(pos.x, pos.y))
            else:
                take_list.append(self.map2ve(pos.x, pos.y))

        self.board.take_remove(vlist=take_list)

        time = self.lineEdit_1.text()
        if time == "":
            time = 0
        move, rate = self.tree.search(self.board, int(time), ponder=True, clean=True)
        print("win rate:", rate)
        print("move count:", self.board.move_cnt)
        print("------------------------------")

        self.take_pieces_list.clear()
        if move != PASS:
            i, j = self.ve2map(move)
            self.draw_piece(i, j)
            self.lineEdit_3.setText(self.map2chessboard_coordinates(i, j))

        else:
            QMessageBox.warning(None, "warning", "PASS", QMessageBox.Ok)
        self.history_board_record.add(self.board, self.pieces_used, self.pieces_unused)
        self.enable_btn(self.actionBack)
        self.enable_btn(self.actionUndo)

    @staticmethod
    def color2board_color(color: int):
        if color == ChessAttr.Piece.BLACK:
            return 1
        if color == ChessAttr.Piece.WHITE:
            return 0

    def click_btn_set(self):
        ret = self.cadlg.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            self.mode = self.cadlg.mode
            self.color = self.cadlg.color

            # self.board.turn = self.color2board_color(self.color)
            self.board.turn = 1

            self.enable_btn(self.p_btn_rar)
            self.disable_btn(self.p_btn_set)
            self.enable_btn(self.p_btn_ok)
            self.enable_btn(self.p_btn_stop)
            self.enable_btn(self.p_btn_ok_2)
            self.enable_btn(self.actionEditChessboard)
            is_gpu = self.checkBox_gpu.isChecked()
            self.tree = search.Tree("./play/model.ckpt", use_gpu=is_gpu)
            if self.board.turn == 0:
                self.board.move_cnt += 1
                pass
        else:
            return

    def click_btn_ok(self):
        target_coordinate = self.lineEdit_2.text()
        if target_coordinate == "":
            return
        flag = self.eat_piece(self.chessboard_coordinates2map(target_coordinate)[0], self.chessboard_coordinates2map(target_coordinate)[1], mode=OperationMode.Remove.TAKE_REMOVE)
        if flag == -1:
            print("该位置没有棋子")
            return
        i, j = self.chessboard_coordinates2map(target_coordinate)
        self.take_pieces_list.append(Pos(i, j))

        self.history_board_record.add(self.board, self.pieces_used, self.pieces_unused)

    def clicked_btn_timer_1(self):
        if self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.ZERO:
            self.timer_1.set_start()
            self.timer_1.start()
            self.timer_1.setPriority(QThread.TimeCriticalPriority)
            self.p_btn_time_1_push_state = MainWindowGui.TimerBtnState.START

        elif self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.START:
            self.p_btn_time_1_push_state = MainWindowGui.TimerBtnState.STOP
            self.show_in_textEdit_2("计时器1：")
            self.total_time_1 += float(self.p_btn_time_1.text())
            self.show_in_textEdit_2("{}  总时间：{}".format(self.p_btn_time_1.text(), self.total_time_1))
            self.show_in_textEdit_2("-----------------------")

        elif self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.STOP:
            self.p_btn_time_1_push_state = MainWindowGui.TimerBtnState.ZERO
            self.timer_1.quit()

    def clicked_btn_timer_2(self):
        if self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.ZERO:
            self.timer_2.set_start()
            self.timer_2.start()
            self.timer_2.setPriority(QThread.TimeCriticalPriority)
            self.p_btn_time_2_push_state = MainWindowGui.TimerBtnState.START

        elif self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.START:
            self.p_btn_time_2_push_state = MainWindowGui.TimerBtnState.STOP
            self.show_in_textEdit_2("计时器2G：")
            self.total_time_2 += float(self.p_btn_time_2.text())
            self.show_in_textEdit_2("{}  总时间：{}".format(self.p_btn_time_2.text(), self.total_time_2))
            self.show_in_textEdit_2("-----------------------")

        elif self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.STOP:
            self.p_btn_time_2_push_state = MainWindowGui.TimerBtnState.ZERO
            self.timer_2.quit()

    def set_btn_time_1_text(self, time):
        if self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.ZERO:
            self.p_btn_time_1.setText("0.0")
        elif self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.START:
            self.p_btn_time_1.setText(str(time))
        elif self.p_btn_time_1_push_state == MainWindowGui.TimerBtnState.STOP:
            pass

    def set_btn_time_2_text(self, time):
        if self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.ZERO:
            self.p_btn_time_2.setText("0.0")
        elif self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.START:
            self.p_btn_time_2.setText(str(time))
        elif self.p_btn_time_2_push_state == MainWindowGui.TimerBtnState.STOP:
            pass

    @staticmethod
    def map2chessboard_coordinates(i: int, j: int) -> str:
        row_index = 9 - i
        col_index = j + ord('A')
        return str(row_index) + chr(col_index)

    @staticmethod
    def chessboard_coordinates2map(map_cor: str) -> tuple:
        row_index = 9 - int(map_cor[0])
        col_index = ord(map_cor[1]) - ord('A')
        return row_index, col_index

    @staticmethod
    def disable_btn(btn_control: Union[QtWidgets.QPushButton, QtWidgets.QAction]):
        btn_control.setEnabled(False)

    @staticmethod
    def enable_btn(btn_control: Union[QtWidgets.QPushButton, QtWidgets.QAction]):
        btn_control.setEnabled(True)

    def show_in_history(self, lineText: str):
        self.history_s = self.textEdit.toPlainText()
        self.textEdit.setText(self.history_s + lineText + "\n")
        self.log_file.writelines(lineText)
        self.textEdit.moveCursor(self.textEdit.textCursor().End)

    def show_in_textEdit_2(self, text: str):
        history_s = self.textEdit_2.toPlainText()
        self.textEdit_2.setText(history_s + text + "\n")
        self.textEdit_2.moveCursor(self.textEdit_2.textCursor().End)


import ui.background_rc  # NOQA: E402s

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # ui = MainWindowGui()
    # ui.do_model()
    # sys.exit(app.exec_())
    print(OperationMode.Remove.SIMPLE_REMOVE)
