"""
@author: Michael
@version: 2021-07-20
"""
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp, pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

sys.path.append("..")
sys.path.append(".")
sys.path.append("../play")
sys.path.append("../ui")

from ui.utils import ChessAttr  # NOQA: E402


class ReplayDlg(QDialog):
    Signal_OneParameter_1 = pyqtSignal(str)
    Signal_OneParameter_2 = pyqtSignal(str)
    Signal_OneParameter_3 = pyqtSignal(str)
    Signal_OneParameter_4 = pyqtSignal(str)
    Signal_TwoParameter_1 = pyqtSignal(str, int)
    Signal_NoneParameter_1 = pyqtSignal()
    Signal_NoneParameter_2 = pyqtSignal()
    Signal_OneParameter_Cancel = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        ReplayDlg = self
        self.buttonBox = QtWidgets.QDialogButtonBox(ReplayDlg)
        self.groupBox_2 = QtWidgets.QGroupBox(ReplayDlg)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.p_btn_ok = QtWidgets.QPushButton(self.groupBox_2)
        self.radioButton_w = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_b = QtWidgets.QRadioButton(self.groupBox_2)
        self.p_btn_cancel = QtWidgets.QPushButton(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(ReplayDlg)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_3)
        self.p_btn_ok_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.p_btn_cancel_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(ReplayDlg)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_4)
        self.p_btn_ok_3 = QtWidgets.QPushButton(self.groupBox_4)
        self.p_btn_cancel_3 = QtWidgets.QPushButton(self.groupBox_4)

        self.setupUi()
        self.init_dlg()

    def init_dlg(self):
        self.set_edit_digits_and_letter_only(self.lineEdit_2)
        self.set_edit_digits_and_letter_only(self.lineEdit_3)

        self.radioButton_w.setChecked(True)

        self.color = ChessAttr.Piece.BLACK

        self.set_edit_digits_and_letter_only(self.lineEdit_4)
        self.connect_all_controls()

    def setupUi(self):
        ReplayDlg = self
        ReplayDlg.setObjectName("ReplayDlg")
        ReplayDlg.resize(430, 202)
        ReplayDlg.setMinimumSize(QtCore.QSize(430, 202))
        ReplayDlg.setMaximumSize(QtCore.QSize(430, 202))

        self.buttonBox.setGeometry(QtCore.QRect(340, 140, 71, 51))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(9)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.groupBox_2.setGeometry(QtCore.QRect(20, 10, 291, 61))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")

        self.lineEdit_2.setGeometry(QtCore.QRect(20, 30, 61, 20))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        font.setPointSize(12)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.p_btn_ok.setGeometry(QtCore.QRect(90, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_ok.setFont(font)
        self.p_btn_ok.setObjectName("p_btn_ok")

        self.radioButton_w.setGeometry(QtCore.QRect(230, 30, 41, 21))
        self.radioButton_w.setObjectName("radioButton_B")
        self.radioButton_b.setGeometry(QtCore.QRect(180, 30, 41, 21))
        self.radioButton_b.setObjectName("radioButton_W")

        self.p_btn_cancel.setGeometry(QtCore.QRect(130, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel.setFont(font)
        self.p_btn_cancel.setObjectName("p_btn_cancel")

        self.groupBox_3.setGeometry(QtCore.QRect(20, 70, 221, 61))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(12)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")

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

        self.p_btn_cancel_2.setGeometry(QtCore.QRect(180, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel_2.setFont(font)
        self.p_btn_cancel_2.setObjectName("p_btn_cancel_2")

        self.groupBox_4.setGeometry(QtCore.QRect(20, 130, 221, 61))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(12)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")

        self.lineEdit_4.setGeometry(QtCore.QRect(20, 30, 113, 20))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setObjectName("lineEdit_4")

        self.p_btn_ok_3.setGeometry(QtCore.QRect(140, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_ok_3.setFont(font)
        self.p_btn_ok_3.setObjectName("p_btn_ok_3")

        self.p_btn_cancel_3.setGeometry(QtCore.QRect(180, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel_3.setFont(font)
        self.p_btn_cancel_3.setObjectName("p_btn_cancel_3")

        self.retranslate_ui(ReplayDlg)
        self.buttonBox.accepted.connect(ReplayDlg.accept)
        self.buttonBox.rejected.connect(ReplayDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(ReplayDlg)
        ReplayDlg.setTabOrder(self.lineEdit_2, self.p_btn_ok)

    def retranslate_ui(self, ReplayDlg):
        _translate = QtCore.QCoreApplication.translate
        ReplayDlg.setWindowTitle(_translate("ReplayDlg", "编辑棋盘"))
        self.groupBox_2.setTitle(_translate("ReplayDlg", "落子"))
        self.p_btn_ok.setText(_translate("ReplayDlg", "√"))
        self.radioButton_w.setText(_translate("ReplayDlg", "黑"))
        self.radioButton_b.setText(_translate("ReplayDlg", "白"))
        self.p_btn_cancel.setText(_translate("ReplayDlg", "×"))
        self.groupBox_3.setTitle(_translate("ReplayDlg", "提子"))
        self.p_btn_ok_2.setText(_translate("ReplayDlg", "√"))
        self.p_btn_cancel_2.setText(_translate("ReplayDlg", "×"))
        self.groupBox_4.setTitle(_translate("ReplayDlg", "落子非法"))
        self.p_btn_ok_3.setText(_translate("ReplayDlg", "√"))
        self.p_btn_cancel_3.setText(_translate("ReplayDlg", "×"))

    def do_model(self):
        self.show()
        self.connect_all_controls()

    def accept(self) -> None:
        return super().accept()

    def connect_all_controls(self):
        self.p_btn_ok.clicked.connect(self.click_btn_ok)
        self.p_btn_ok_2.clicked.connect(self.click_btn_ok_2)
        self.p_btn_cancel.clicked.connect(self.click_btn_cancel)
        self.p_btn_cancel_2.clicked.connect(self.click_btn_cancel_2)
        self.p_btn_cancel_3.clicked.connect(self.click_btn_cancel_3)
        self.p_btn_ok_3.clicked.connect(self.click_btn_ok_3)

    def click_btn_ok_3(self):
        self.Signal_OneParameter_4.emit(self.lineEdit_4.text())

    def click_btn_cancel_3(self):
        self.lineEdit_4.clear()

    def changing_lineText_2(self):
        pass

    def click_btn_ok(self):
        if self.radioButton_w.isChecked():
            self.color = ChessAttr.Piece.BLACK
        if self.radioButton_b.isChecked():
            self.color = ChessAttr.Piece.WHITE
        self.Signal_TwoParameter_1.emit(self.lineEdit_2.text(), self.color)

    def click_btn_ok_2(self):
        self.Signal_OneParameter_2.emit(self.lineEdit_3.text())

    def click_btn_cancel(self):
        self.Signal_OneParameter_Cancel.emit(self.lineEdit_2.text())

    def click_btn_cancel_2(self):
        self.lineEdit_3.clear()

    @staticmethod
    def set_edit_digits_and_letter_only(edit: QtWidgets.QLineEdit):
        reg = QRegExp("^[0-9]{1}[A-I]{1}$")
        validator = QRegExpValidator(reg)
        edit.setValidator(validator)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = ReplayDlg()
    f = ui.exec_()
    sys.exit(app.exec_())
