from math import sqrt
import csv
from datetime import datetime
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from .Signal import Signal

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Raspberry BLE Client")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        self.recording = False
        self.saved_data = []
        self.record_button = QPushButton("Iniciar Grabación", self)
        self.save_button = QPushButton("Guardar CSV", self)

        self.record_button.clicked.connect(self.start_recording)
        self.save_button.clicked.connect(self.saveCSV)
        self.save_button.setVisible(False)

        self.accel_data = []
        self.accel_plot = pg.PlotWidget(title="Gráfico de Aceleración")
        self.accel_plot.setFixedSize(760, 300)
        self.accel_plot.addLegend()
        self.accel_plot.setLabel('left', 'Aceleración (m/s²)')
        self.accel_plot.setLabel('bottom', 'Muestras')
        self.accel_plot.setYRange(-20, 20)

        self.signals = Signal()

        self.min_time = 2000
        self.signals.accel_data_signal.connect(self.update_accel_data)
        self.signals.temp_data_signal.connect(self.update_temp_data)
        self.signals.server_data_signal.connect(self.update_server_data)

        self.accel_button = QPushButton("Gráfico de aceleración", self)
        self.temp_button = QPushButton("Temperatura actual", self)
        self.server_button = QPushButton("Información del servidor", self)
        self.range_button = QPushButton("Ajustar ventana", self)

        self.accel_button.clicked.connect(self.on_accel_button_pressed)
        self.temp_button.clicked.connect(self.on_temp_button_pressed)
        self.server_button.clicked.connect(self.on_server_button_pressed)
        self.range_button.clicked.connect(self.on_range_button_pressed)

        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        button_layout.addWidget(self.accel_button)
        button_layout.addWidget(self.temp_button)
        button_layout.addWidget(self.server_button)
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.save_button)

        self.accel_info = QGroupBox("Aceleración")
        self.temp_info = QGroupBox("Temperatura")
        self.server_info = QGroupBox("Servidor")

        self.temp_label = QLabel("Temperatura: N/A", self)
        self.server_label = QLabel("Información del servidor: N/A", self)

        self.rms_label = QLabel("RMSx: N/A | RMSy: N/A | RMSz: N/A", self)
        self.peak_label = QLabel("Peak+ X: N/A | Peak+ Y: N/A | Peak+ Z: N/A", self)
        self.p2p_label = QLabel("Pk-Pk X: N/A | Pk-Pk Y: N/A | Pk-Pk Z: N/A", self)

        self.accel_info.setVisible(False)
        self.temp_info.setVisible(False)
        self.server_info.setVisible(False)

        layout.addWidget(self.button_container, alignment=Qt.AlignTop)
        layout.addWidget(self.accel_info)
        layout.addWidget(self.temp_info)
        layout.addWidget(self.server_info)

        accel_layout = QVBoxLayout(self.accel_info)
        accel_layout.addWidget(self.accel_plot)
        accel_layout.addWidget(self.rms_label)
        accel_layout.addWidget(self.peak_label)
        accel_layout.addWidget(self.p2p_label)
        accel_layout.addWidget(self.range_button)

        temp_layout = QVBoxLayout(self.temp_info)
        temp_layout.addWidget(self.temp_label)

        server_layout = QVBoxLayout(self.server_info)
        server_layout.addWidget(self.server_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._alive = True
        self.destroyed.connect(self._on_destroyed)
    
    def on_accel_button_pressed(self) -> None:
        self.accel_info.setVisible(not self.accel_info.isVisible())

    def on_temp_button_pressed(self) -> None:
        self.temp_info.setVisible(not self.temp_info.isVisible())

    def on_server_button_pressed(self) -> None:
        self.server_info.setVisible(not self.server_info.isVisible())

    def on_range_button_pressed(self) -> None:
        value, ok = QInputDialog.getInt(
            self,
            "Ajustar ventana de aceleración",
            "Min time (ms):",
            self.min_time,
            2000,
            15000,
            1,
        )
        if ok:
            self.min_time = value
            if self.accel_data:
                self.plot_accel_data(self.accel_data[-1][3])

    def _on_destroyed(self, obj=None) -> None:
        self._alive = False

    def is_alive(self) -> bool:
        return self._alive

    def update_accel_data(self, timestamp: int, x: float, y: float, z: float) -> None:

        if self.recording:
            self.saved_data.append((x, y, z, timestamp))

        if len(self.accel_data) < 20000:
            self.accel_data.append((x, y, z, timestamp))

        else:
            self.accel_data.pop(0)
            self.accel_data.append((x, y, z, timestamp))

        self.plot_accel_data(timestamp)

    def plot_accel_data(self, timestamp: int) -> None:
        recent_samples = [sample for sample in self.accel_data if sample[3] - timestamp + self.min_time >= 0]

        if not recent_samples:
            return

        t_data = [sample[3] - timestamp + self.min_time for sample in recent_samples]
        x_data = [sample[0] for sample in recent_samples]
        y_data = [sample[1] for sample in recent_samples]
        z_data = [sample[2] for sample in recent_samples]

        self.accel_plot.clear()
        self.accel_plot.setXRange(0, self.min_time, padding=0)
        self.accel_plot.plot(t_data, x_data, pen='r', name='X')
        self.accel_plot.plot(t_data, y_data, pen='g', name='Y')
        self.accel_plot.plot(t_data, z_data, pen='b', name='Z')

        if len(self.accel_data) < 1000:
            return

        x_data, y_data, z_data, _ = zip(*self.accel_data)

        def rms(values):
            return sqrt(sum(v * v for v in values) / len(values))

        rms_x = rms(x_data)
        rms_y = rms(y_data)
        rms_z = rms(z_data)

        max_x = max(x_data)
        max_y = max(y_data)
        max_z = max(z_data)

        p2p_x = max_x - min(x_data)
        p2p_y = max_y - min(y_data)
        p2p_z = max_z - min(z_data)

        self.rms_label.setText(f"RMSx: {rms_x:.2f} | RMSy: {rms_y:.2f} | RMSz: {rms_z:.2f}")
        self.peak_label.setText(f"Max X: {max_x:.2f} | Max Y: {max_y:.2f} | Max Z: {max_z:.2f}")
        self.p2p_label.setText(f"Distancia pico a pico X: {p2p_x:.2f} | Distancia pico a pico Y: {p2p_y:.2f} | Distancia pico a pico Z: {p2p_z:.2f}")

    def update_temp_data(self, timestamp: int, temp: float) -> None:

        if self.recording:
            self.saved_data.append((temp, timestamp))

        self.temp_label.setText(f"Temperatura: {temp} °C. Última actualización: {timestamp}")

    def update_server_data(self, info: str) -> None:

        timestamp = datetime.now().timestamp()
        if self.recording:
            self.saved_data.append((info, timestamp))

        self.server_label.setText(f"Información del servidor: {info}. Última actualización: {timestamp}")
    
    def start_recording(self) -> None:
        self.recording = True
        self.record_button.setVisible(False)
        self.save_button.setVisible(True)

    def saveCSV(self) -> None:
        self.recording = False
        self.record_button.setVisible(True)
        self.save_button.setVisible(False)

        with open('data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Source', 'ax', 'ay', 'az', 'Temperatura', 'valor_celular'])

            for i in self.saved_data:
                if len(i) == 4:
                    writer.writerow([i[3], 'ESP32', i[0], i[1], i[2], '', ''])

                elif isinstance(i[0], float):
                    writer.writerow([i[1], 'ESP32', '', '', '', i[0], ''])

                else:
                    writer.writerow([i[1], 'Celular', '', '', '', '', i[0]])

        self.saved_data = []
        