"""
@author: Michael
@version: 2021-07-20
"""
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QWidget, QApplication

BLACK = 1
WHITE = 2


class Ui_ReplayDlg(QDialog):
    Signal_OneParameter_1 = pyqtSignal(str)
    Signal_OneParameter_2 = pyqtSignal(str)
    Signal_OneParameter_3 = pyqtSignal(str)
    Signal_TwoParameter_1 = pyqtSignal(str, int)
    Signal_NoneParameter_1 = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        ReplayDlg = self
        self.buttonBox = QtWidgets.QDialogButtonBox(ReplayDlg)
        self.groupBox_2 = QtWidgets.QGroupBox(ReplayDlg)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.p_btn_ok = QtWidgets.QPushButton(self.groupBox_2)
        self.radioButton_B = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioButton_W = QtWidgets.QRadioButton(self.groupBox_2)
        self.p_btn_cancel = QtWidgets.QPushButton(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(ReplayDlg)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_3)
        self.p_btn_ok_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.p_btn_cancel_2 = QtWidgets.QPushButton(self.groupBox_3)

        self.setupUi()

        self.set_edit_digits_and_letter_only(self.lineEdit_2)
        self.set_edit_digits_and_letter_only(self.lineEdit_3)

        self.radioButton_B.setChecked(True)

        self.color = BLACK

    def setupUi(self):
        ReplayDlg = self
        ReplayDlg.setObjectName("ReplayDlg")
        ReplayDlg.resize(430, 174)
        ReplayDlg.setMinimumSize(QtCore.QSize(430, 174))
        ReplayDlg.setMaximumSize(QtCore.QSize(430, 174))
        self.buttonBox.setGeometry(QtCore.QRect(330, 100, 71, 51))
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
        self.radioButton_B.setGeometry(QtCore.QRect(230, 30, 41, 21))
        self.radioButton_B.setObjectName("radioButton_B")
        self.radioButton_W.setGeometry(QtCore.QRect(180, 30, 41, 21))
        self.radioButton_W.setObjectName("radioButton_W")
        self.p_btn_cancel.setGeometry(QtCore.QRect(130, 30, 31, 21))
        font = QtGui.QFont()
        font.setFamily("JetBrains Mono")
        self.p_btn_cancel.setFont(font)
        self.p_btn_cancel.setObjectName("p_btn_cancel")
        self.groupBox_3.setGeometry(QtCore.QRect(20, 90, 221, 61))
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

        self.retranslateUi(ReplayDlg)
        self.buttonBox.accepted.connect(ReplayDlg.accept)
        self.buttonBox.rejected.connect(ReplayDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(ReplayDlg)
        ReplayDlg.setTabOrder(self.lineEdit_2, self.p_btn_ok)

    def retranslateUi(self, ReplayDlg):
        _translate = QtCore.QCoreApplication.translate
        ReplayDlg.setWindowTitle(_translate("ReplayDlg", "编辑棋盘"))
        self.groupBox_2.setTitle(_translate("ReplayDlg", "落子"))
        self.p_btn_ok.setText(_translate("ReplayDlg", "√"))
        self.radioButton_B.setText(_translate("ReplayDlg", "黑"))
        self.radioButton_W.setText(_translate("ReplayDlg", "白"))
        self.p_btn_cancel.setText(_translate("ReplayDlg", "×"))
        self.groupBox_3.setTitle(_translate("ReplayDlg", "提子"))
        self.p_btn_ok_2.setText(_translate("ReplayDlg", "√"))
        self.p_btn_cancel_2.setText(_translate("ReplayDlg", "×"))

    def do_model(self):
        self.show()
        self.connect_all_controls()

    def connect_all_controls(self):
        self.p_btn_ok.clicked.connect(self.click_btn_ok)
        self.p_btn_ok_2.clicked.connect(self.click_btn_ok_2)
        self.p_btn_cancel.clicked.connect(self.click_btn_cancel)
        self.p_btn_cancel_2.clicked.connect(self.click_btn_cancel_2)

    # def closeEvent(self, event: QtGui.QCloseEvent) -> None:
    #     self.Signal_NoneParameter_1.emit()
    #     event.accept()

    # def close(self) -> bool:
    #     # self.close()
    #     self.destroy()

    # def accept(self) -> None:
    #     self.Signal_NoneParameter_1.emit()
    #     self.destroy()
    #
    # def reject(self) -> None:
    #     self.Signal_NoneParameter_1.emit()
    #     self.destroy()

    def changing_lineText_2(self):
        pass

    def click_btn_ok(self):
        if self.radioButton_B.isChecked():
            self.color = BLACK
        if self.radioButton_W.isChecked():
            self.color = WHITE
        self.Signal_TwoParameter_1.emit(self.lineEdit_2.text(), self.color)

    def click_btn_ok_2(self):
        self.Signal_OneParameter_2.emit(self.lineEdit_3.text())

    def click_btn_cancel(self):
        self.lineEdit_2.clear()

    def click_btn_cancel_2(self):
        self.lineEdit_3.clear()

    @staticmethod
    def set_edit_digits_and_letter_only(edit: QtWidgets.QLineEdit):
        reg = QRegExp("^[0-9]{1}[A-I]{1}$")
        validator = QRegExpValidator(reg)
        edit.setValidator(validator)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_ReplayDlg()
    ui.do_model()
    sys.exit(app.exec_())
