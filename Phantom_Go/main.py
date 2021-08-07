"""
@author: Michael
@Date: 2021-07-24
"""
# -*- coding: utf-8 -*-
from ui.Shadow_Go_Gui import MainWindowGui
from PyQt5.QtWidgets import QApplication
import sys
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindowGui()
    ui.do_model()
    sys.exit(app.exec_())
