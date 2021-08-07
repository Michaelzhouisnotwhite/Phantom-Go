"""
@author: Michael
@version: 2021-07-18
"""
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QMessageBox
import sys
from collections import deque
from ReplayDlg_Gui import *
from ChessAttributeDlg_GUi import *

# --------Qwidget棋盘宽高-----------
WIDTH = 430
HEIGHT = 430
# -------------------
MARGIN = 24  # 窗口边缘宽度
GRID = (WIDTH - 2 * MARGIN) / 8
# 棋子大小
PIECE = 34
EMPTY = 0
BLACK = 1
WHITE = 2

# 下棋模式
TAKE_TURNS = True
ONE_SIDE = False


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # -------------------界面初始化----------------------------------
        self.dlg = Ui_ReplayDlg(self)
        self.cadlg = Ui_ChessAttributeDlg(self)
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
        self.p_btn_rar = QtWidgets.QPushButton(self.centralwidget)
        self.p_btn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)

        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_4)
        self.p_btn_ok_2 = QtWidgets.QPushButton(self.groupBox_4)
        self.p_btn_cancel_2 = QtWidgets.QPushButton(self.groupBox_4)

        # ------------------------------------------------------------------
        self.black = QPixmap('img/black.png')
        self.white = QPixmap('img/white.png')
        # 音效加载
        self.sound_piece = QSound("sound/move.wav")

        self.piece_now = BLACK
        self.step = 0  # 步数
        # 添加Qlabel作为棋子
        self.pieces = [QLabel(self) for i in range(81)]

        self.setupUi()

        # 已下棋子和未下棋子用队列装起来记录，方便删除和添加
        self.pieces_used = deque()
        self.pieces_unused = deque()

        # 界面初始化操作
        self.init_mainWindow()

        self.history_s = None

        # 下棋模式
        self.mode = ONE_SIDE
        self.color = BLACK

    def init_mainWindow(self):
        self.init_pieces_deque()
        self.disable_btn(self.p_btn_rar)
        self.disable_btn(self.p_btn_ok)
        self.disable_btn(self.p_btn_stop)
        self.disable_btn(self.p_btn_ok_2)

        self.set_edit_digits_only(self.lineEdit_1)
        self.set_edit_digits_and_letter_only(self.lineEdit_3)
        self.set_edit_digits_and_letter_only(self.lineEdit_2)

    def init_pieces_deque(self):
        for i in range(81):
            self.pieces_unused.append(i)

    def lay_piece(self, i, j) -> int:
        used_p = self.pieces_unused.popleft()
        for _, pd in enumerate(self.pieces_used):
            if pd["pos"] == (i, j):
                print("Error, 棋子重叠！！")
                return -1
        self.pieces_used.append({"piece_no": used_p, "pos": (i, j)})
        return used_p

    def eat_piece(self, i: int, j: int) -> int:
        """吃掉指定逻辑坐标的棋子"""
        for _, pd in enumerate(self.pieces_used):
            if pd["pos"] == (i, j):
                self.pieces_unused.append(pd["piece_no"])
                self.pieces_used.remove(pd)
                print(pd)
                self.pieces[pd["piece_no"]].clear()
                self.show_in_history("remove:" + self.pretty_print_coordinate(self.map2chessboard_coordinates(i, j)))
                return 1
        return -1

    def draw_piece(self, i, j, color=None):
        """下指定坐标的棋子"""
        x, y = self.map2pixel(i, j)
        index = self.lay_piece(i, j)
        if index == -1:
            return
        if color is None:
            if self.mode == TAKE_TURNS:
                # 一次黑棋一次白棋
                if self.piece_now == BLACK:
                    self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
                    self.piece_now = WHITE
                else:
                    self.pieces[index].setPixmap(self.white)  # 放置白色棋子
                    self.piece_now = BLACK
            elif self.mode == ONE_SIDE:
                if self.color == BLACK:
                    self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
                elif self.color == WHITE:
                    self.pieces[index].setPixmap(self.white)  # 放置白色棋子
        else:
            if color == BLACK:
                self.pieces[index].setPixmap(self.black)  # 放置黑色棋子
            elif color == WHITE:
                self.pieces[index].setPixmap(self.white)  # 放置白色棋子

        self.pieces[index].setGeometry(x, y, PIECE, PIECE)  # 画出棋子
        self.sound_piece.play()  # 落子音效
        # self.step += 1  # 步数+1

        chessboard_coordinate = self.map2chessboard_coordinates(i, j)
        self.show_in_history("placed:" + self.pretty_print_coordinate(chessboard_coordinate))

        winner = EMPTY  # 判断输赢
        if winner != EMPTY:
            # self.mouse_point.clear()
            self.game_over(winner)

    @staticmethod
    def pretty_print_coordinate(map_cdt: str):
        map_cdt = "(" + map_cdt[0] + ", " + map_cdt[1] + ")"
        return map_cdt

    def remove_all_piece(self):
        for _, pd in enumerate(self.pieces_used):
            self.pieces_unused.append(pd["piece_no"])
            self.pieces_used.remove(pd)
            print(pd)
            self.pieces[pd["piece_no"]].clear()
            # self.show_in_history("remove:" + self.pretty_print_coordinate(self.map2chessboard_coordinates(i, j)))

    def map2pixel(self, i, j):
        """从逻辑坐标到 UI 上的绘制坐标的转换"""
        mh = self.menuBar.height()
        x = self.widget_chessboard.geometry().x()
        y = self.widget_chessboard.geometry().y()
        return MARGIN + j * GRID - PIECE / 2 + x, MARGIN + i * GRID - PIECE / 2 + mh + y  # 加上菜单栏的高度

    def setupUi(self):
        """界面初始化"""
        MainWindow = self

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(856, 496)
        MainWindow.setMinimumSize(QtCore.QSize(856, 496))
        MainWindow.setMaximumSize(QtCore.QSize(856, 496))

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
        self.groupBox_3.setGeometry(QtCore.QRect(690, 20, 151, 351))

        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")

        self.textEdit.setGeometry(QtCore.QRect(10, 20, 131, 321))

        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(9)
        self.textEdit.setFont(font)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        self.p_btn_rar.setGeometry(QtCore.QRect(460, 400, 131, 31))

        self.groupBox_4.setGeometry(QtCore.QRect(460, 310, 221, 71))
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

        MainWindow.setMenuBar(self.menuBar)

        # self.actionReplay.setObjectName("actionReplay")
        # self.actionRerun.setObjectName("actionRerun")
        # self.actionCompleteReplay.setObjectName("actionCompleteReplay")
        # self.actionCancelReplay.setObjectName("actionCancelReplay")
        self.menu_operate.addAction(self.actionEditChessboard)
        self.menuBar.addAction(self.menu_operate.menuAction())

        # self.menu_operate.addAction(self.actionReplay)
        # self.menu_operate.addAction(self.actionCompleteReplay)
        # self.menu_operate.addAction(self.actionCancelReplay)

        self.retranslate_Ui()
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
        if winner == BLACK:
            self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 失败
        else:
            self.sound_defeated.play()
            reply = QMessageBox.question(self, 'You Lost!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        # 若选择Yes，重置棋盘
        if reply == QMessageBox.Yes:
            self.piece_now = BLACK
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

    def retranslate_Ui(self):
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
        self.actionEditChessboard.setText(_translate("MainWindow", "编辑棋盘"))

    def do_model(self):
        self.show()
        self.connect_all_controls()

    def connect_all_controls(self):
        self.p_btn_rar.clicked.connect(self.click_btn_rar)
        self.p_btn_set.clicked.connect(self.click_btn_set)
        self.p_btn_ok.clicked.connect(self.click_btn_ok)
        self.p_btn_stop.clicked.connect(self.click_btn_stop)
        self.p_btn_cancel.clicked.connect(self.click_btn_cancel)
        self.actionEditChessboard.triggered.connect(self.clicked_action_edit_chessboard)
        self.p_btn_ok_2.clicked.connect(self.click_btn_ok_2)
        self.p_btn_cancel_2.clicked.connect(self.click_btn_cancel_2)

    def clicked_action_edit_chessboard(self):
        # self.remove_all_piece()
        self.show_in_history("<Edit mode on>")
        self.dlg.Signal_TwoParameter_1.connect(self.get_dlg_lineText_2)
        self.dlg.Signal_OneParameter_2.connect(self.get_dlg_lineText_3)
        # self.dlg.Signal_NoneParameter_1.connect(self.dlg_close)
        self.dlg.do_model()
        if self.dlg.exec_() != -1:
            self.dlg_close()

    def dlg_close(self):
        self.show_in_history("</Edit mode off>")

    def get_dlg_lineText_2(self, text: QtWidgets.QLineEdit, color: int):
        # print(text)
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        self.draw_piece(i, j, color)

    def get_dlg_lineText_3(self, text: QtWidgets.QLineEdit):
        # print(text)
        if text == "":
            return
        i, j = self.chessboard_coordinates2map(text)
        self.eat_piece(i, j)

    def click_btn_ok_2(self):
        target_coordinate = self.lineEdit_3.text()
        flag = self.eat_piece(self.chessboard_coordinates2map(target_coordinate)[0],
                              self.chessboard_coordinates2map(target_coordinate)[1])
        if flag == -1:
            print("该位置没有棋子")
    def click_btn_cancel_2(self):
        self.lineEdit_3.clear()
    def click_btn_stop(self):
        self.disable_btn(self.p_btn_rar)
        self.enable_btn(self.p_btn_set)
        self.disable_btn(self.p_btn_stop)
        self.disable_btn(self.p_btn_ok)

    def click_btn_cancel(self):
        self.lineEdit_2.clear()

    def click_btn_rar(self):
        """当按下run的时候"""
        # -------test----------测试按下按钮时添加（3, 4）的棋子
        self.draw_piece(3, 4)

    def click_btn_set(self):
        is_gpu = self.checkBox_gpu.isChecked()
        main_time = self.lineEdit_1.text()
        # print(main_time, is_gpu)
        ret = self.cadlg.exec_()
        if ret == QtWidgets.QDialog.Accepted:
            self.mode = self.cadlg.mode
            self.color = self.cadlg.color
            self.enable_btn(self.p_btn_rar)
            self.disable_btn(self.p_btn_set)
            self.enable_btn(self.p_btn_ok)
            self.enable_btn(self.p_btn_stop)
            self.enable_btn(self.p_btn_ok_2)
        else:
            return

    def click_btn_ok(self):
        target_coordinate = self.lineEdit_2.text()
        if not ord("0") < ord(target_coordinate[0]) <= ord("9") and "A" <= target_coordinate[1] <= "I" \
                and len(target_coordinate) == 2:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("输入错误")
            msgBox.setWindowTitle("Error!")
            msgBox.setStandardButtons(QMessageBox.Ok)
        else:
            flag = self.eat_piece(self.chessboard_coordinates2map(target_coordinate)[0],
                                  self.chessboard_coordinates2map(target_coordinate)[1])
            if flag == -1:
                print("该位置没有棋子")

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
    def disable_btn(btn_control: QtWidgets.QPushButton):
        btn_control.setEnabled(False)

    @staticmethod
    def enable_btn(btn_control: QtWidgets.QPushButton):
        btn_control.setEnabled(True)

    def show_in_history(self, lineText: str):
        self.history_s = self.textEdit.toPlainText()
        self.textEdit.setText(self.history_s + lineText + "\n")


import background_rc

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.do_model()
    sys.exit(app.exec_())
