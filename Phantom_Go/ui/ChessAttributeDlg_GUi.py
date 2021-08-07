"""
@author: Michael
@version: 2021-07-21
"""
import sys
from ui.utils import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QWidget, QApplication

TAKE_TURNS = True
ONE_SIDE = False

class ChessAttributeDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        Dialog = self
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.radioButton = QtWidgets.QRadioButton(Dialog)
        self.radioButton_2 = QtWidgets.QRadioButton(Dialog)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.radioButton_3 = QtWidgets.QRadioButton(self.groupBox)
        self.radioButton_4 = QtWidgets.QRadioButton(self.groupBox)

        self.mode = None
        self.color = None

        self.is_accept = False

        self.setupUi()
        self.init_dlg()

    def init_dlg(self):
        self.radioButton.setChecked(True)
        self.radioButton_3.setChecked(True)

    def setupUi(self):
        Dialog = self
        Dialog.setObjectName("Dialog")
        Dialog.resize(381, 145)
        self.buttonBox.setGeometry(QtCore.QRect(110, 100, 161, 32))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.radioButton.setGeometry(QtCore.QRect(30, 30, 89, 16))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.radioButton.setFont(font)
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2.setGeometry(QtCore.QRect(30, 60, 89, 16))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setObjectName("radioButton_2")
        self.groupBox.setGeometry(QtCore.QRect(130, 20, 191, 61))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.radioButton_3.setGeometry(QtCore.QRect(20, 30, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.radioButton_3.setFont(font)
        self.radioButton_3.setObjectName("radioButton_3")
        self.radioButton_4.setGeometry(QtCore.QRect(110, 30, 61, 16))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.radioButton_4.setFont(font)
        self.radioButton_4.setObjectName("radioButton_4")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "下棋属性"))
        self.radioButton.setText(_translate("Dialog", "轮流下棋"))
        self.radioButton_2.setText(_translate("Dialog", "只下一边"))
        self.groupBox.setTitle(_translate("Dialog", "先下者棋色or己方棋色"))
        self.radioButton_3.setText(_translate("Dialog", "黑"))
        self.radioButton_4.setText(_translate("Dialog", "白"))

    def do_model(self):
        self.is_accept = False
        self.show()
        self.connect_all_controls()

    def connect_all_controls(self):
        pass

    def accept(self) -> None:
        if self.radioButton.isChecked():
            self.mode = OperationMode.Draw.TAKE_TURNS
        elif self.radioButton_2.isChecked():
            self.mode = OperationMode.Draw.ONE_SIDE

        if self.radioButton_3.isChecked():
            self.color = ChessAttr.Piece.BLACK
        elif self.radioButton_4.isChecked():
            self.color = ChessAttr.Piece.WHITE
        self.is_accept = True
        self.done(QtWidgets.QDialog.Accepted)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = ChessAttributeDlg()
    ui.do_model()
    sys.exit(app.exec_())
