import typing
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5 import QtWidgets
import time
class Timer(QThread):
    sinOut = pyqtSignal(str)
    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.start_time:float = 0.0
    
    def set_start(self):
        self.start_time = time.perf_counter()
        return 1
    
    def run(self) -> None:
        while True:
            cur_time = time.perf_counter()  
            QThread.msleep(90)
            self.sinOut.emit(str(abs(round(cur_time - self.start_time, 1))))