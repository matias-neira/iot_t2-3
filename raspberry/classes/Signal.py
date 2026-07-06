from PyQt6.QtCore import pyqtSignal, QObject

class Signal(QObject):
    accel_data_signal = pyqtSignal(int, float, float, float)
    temp_data_signal = pyqtSignal(int, float)
    status_data_signal = pyqtSignal(int, int)
    update_status_signal = pyqtSignal()