from PyQt5.QtCore import pyqtSignal, QObject

class Signal(QObject):
    accel_data_signal = pyqtSignal(int, float, float, float)
    temp_data_signal = pyqtSignal(int, float)
    server_data_signal = pyqtSignal(str)