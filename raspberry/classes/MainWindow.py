from math import sqrt
import csv
from datetime import datetime
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QInputDialog, QTabWidget, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

from .Signal import Signal
from .Config import Config

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.__config = Config()
        self.signals = Signal()
        self.__recording = False
        self.__saved_data = []

        self.setWindowTitle("Raspberry BLE Client")
        self.setGeometry(100, 100, 800, 600)

        self.__tab_widget = QTabWidget()
        self.__main_tab = QWidget()
        self.__config_tab = QWidget()

        main_layout = QVBoxLayout(self.__main_tab)

        self.__accel_data = []
        self.__accel_plot = pg.PlotWidget(title="Gráfico de Aceleración")
        self.__accel_plot.setFixedSize(760, 300)
        self.__accel_plot.addLegend()
        self.__accel_plot.setLabel('left', 'Aceleración (m/s²)')
        self.__accel_plot.setLabel('bottom', 'Muestras')
        self.__accel_plot.setYRange(-20, 20)

        self.min_time = 2000
        self.signals.accel_data_signal.connect(self.__update_accel_data)
        self.signals.temp_data_signal.connect(self.__update_temp_data)
        self.signals.server_data_signal.connect(self.__update_server_data)

        self.__accel_button = QPushButton("Gráfico de aceleración", self)
        self.__temp_button = QPushButton("Temperatura actual", self)
        self.__server_button = QPushButton("Información del servidor", self)
        self.__record_button = QPushButton("Iniciar Grabación", self)
        self.__range_button = QPushButton("Ajustar ventana", self)

        self.__accel_button.clicked.connect(self.__on_accel_button_pressed)
        self.__temp_button.clicked.connect(self.__on_temp_button_pressed)
        self.__server_button.clicked.connect(self.__on_server_button_pressed)
        self.__record_button.clicked.connect(self.__on_record_button_pressed)
        self.__range_button.clicked.connect(self.__on_range_button_pressed)

        self.__button_container = QWidget()
        button_layout = QHBoxLayout(self.__button_container)
        button_layout.addWidget(self.__accel_button)
        button_layout.addWidget(self.__temp_button)
        button_layout.addWidget(self.__server_button)
        button_layout.addWidget(self.__record_button)
        
        self.__accel_info = QGroupBox("Aceleración")
        self.__temp_info = QGroupBox("Temperatura")
        self.__server_info = QGroupBox("Servidor")

        self.__temp_label = QLabel("Temperatura: N/A", self)
        self.__server_label = QLabel("Información del servidor: N/A", self)

        self.__rms_label = QLabel("RMSx: N/A | RMSy: N/A | RMSz: N/A", self)
        self.__peak_label = QLabel("Peak+ X: N/A | Peak+ Y: N/A | Peak+ Z: N/A", self)
        self.__p2p_label = QLabel("Pk-Pk X: N/A | Pk-Pk Y: N/A | Pk-Pk Z: N/A", self)

        self.__accel_info.setVisible(False)
        self.__temp_info.setVisible(False)
        self.__server_info.setVisible(False)

        main_layout.addWidget(self.__button_container, alignment=Qt.AlignTop)
        main_layout.addWidget(self.__accel_info)
        main_layout.addWidget(self.__temp_info)
        main_layout.addWidget(self.__server_info)

        accel_layout = QVBoxLayout(self.__accel_info)
        accel_layout.addWidget(self.__accel_plot)
        accel_layout.addWidget(self.__rms_label)
        accel_layout.addWidget(self.__peak_label)
        accel_layout.addWidget(self.__p2p_label)
        accel_layout.addWidget(self.__range_button)

        temp_layout = QVBoxLayout(self.__temp_info)
        temp_layout.addWidget(self.__temp_label)

        server_layout = QVBoxLayout(self.__server_info)
        server_layout.addWidget(self.__server_label)

        self.__accel_enabled_checkbox = QCheckBox("Acelerómetro habilitado", self)
        self.__accel_qos_combo = QComboBox(self)
        self.__accel_qos_combo.addItems(["0", "1", "2"])

        accel_sensor_box = QGroupBox("Acelerómetro")
        accel_sensor_layout = QHBoxLayout(accel_sensor_box)
        accel_sensor_layout.addWidget(self.__accel_enabled_checkbox)
        accel_sensor_layout.addWidget(QLabel("QoS:"))
        accel_sensor_layout.addWidget(self.__accel_qos_combo)

        self.__temp_enabled_checkbox = QCheckBox("Temperatura habilitada", self)
        self.__temp_qos_combo = QComboBox(self)
        self.__temp_qos_combo.addItems(["0", "1", "2"])

        temp_sensor_box = QGroupBox("Temperatura")
        temp_sensor_layout = QHBoxLayout(temp_sensor_box)
        temp_sensor_layout.addWidget(self.__temp_enabled_checkbox)
        temp_sensor_layout.addWidget(QLabel("QoS:"))
        temp_sensor_layout.addWidget(self.__temp_qos_combo)

        self.__set_config_values()

        self.__apply_config_button = QPushButton("Aplicar", self)
        self.__apply_config_button.clicked.connect(self.__on_apply_config_button_pressed)

        self.__reload_config_button = QPushButton("Recargar configuración", self)
        self.__reload_config_button.clicked.connect(self.__on_reload_config_button_pressed)

        config_layout = QVBoxLayout(self.__config_tab)
        config_layout.addWidget(accel_sensor_box)
        config_layout.addWidget(temp_sensor_box)
        config_layout.addStretch()
        config_layout.addWidget(self.__apply_config_button, alignment=Qt.AlignRight)
        config_layout.addWidget(self.__reload_config_button, alignment=Qt.AlignRight)

        self.__tab_widget.addTab(self.__main_tab, "Principal")
        self.__tab_widget.addTab(self.__config_tab, "Configuración")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(self.__tab_widget)
        self.setCentralWidget(container)

        self.__alive = True
        self.destroyed.connect(self._on_destroyed)
    
    def __on_accel_button_pressed(self) -> None:
        self.__accel_info.setVisible(not self.__accel_info.isVisible())

    def __on_temp_button_pressed(self) -> None:
        self.__temp_info.setVisible(not self.__temp_info.isVisible())

    def __on_server_button_pressed(self) -> None:
        self.__server_info.setVisible(not self.__server_info.isVisible())

    def __on_range_button_pressed(self) -> None:
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
            if self.__accel_data:
                self.__plot_accel_data(self.__accel_data[-1][3])

    def _on_destroyed(self, obj=None) -> None:
        self.__alive = False

    def is_alive(self) -> bool:
        return self.__alive

    def __update_accel_data(self, timestamp: int, x: float, y: float, z: float) -> None:

        if self.__recording:
            self.__saved_data.append((x, y, z, timestamp))

        if len(self.__accel_data) < 20000:
            self.__accel_data.append((x, y, z, timestamp))

        else:
            self.__accel_data.pop(0)
            self.__accel_data.append((x, y, z, timestamp))

        self.__plot_accel_data(timestamp)

    def __plot_accel_data(self, timestamp: int) -> None:
        recent_samples = [sample for sample in self.__accel_data if sample[3] - timestamp + self.min_time >= 0]

        if not recent_samples:
            return

        t_data = [sample[3] - timestamp + self.min_time for sample in recent_samples]
        x_data = [sample[0] for sample in recent_samples]
        y_data = [sample[1] for sample in recent_samples]
        z_data = [sample[2] for sample in recent_samples]

        self.__accel_plot.clear()
        self.__accel_plot.setXRange(0, self.min_time, padding=0)
        self.__accel_plot.plot(t_data, x_data, pen='r', name='X')
        self.__accel_plot.plot(t_data, y_data, pen='g', name='Y')
        self.__accel_plot.plot(t_data, z_data, pen='b', name='Z')

        if len(self.__accel_data) < 1000:
            return

        x_data, y_data, z_data, _ = zip(*self.__accel_data)

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

        self.__rms_label.setText(f"RMSx: {rms_x:.2f} | RMSy: {rms_y:.2f} | RMSz: {rms_z:.2f}")
        self.__peak_label.setText(f"Max X: {max_x:.2f} | Max Y: {max_y:.2f} | Max Z: {max_z:.2f}")
        self.__p2p_label.setText(f"Distancia pico a pico X: {p2p_x:.2f} | Distancia pico a pico Y: {p2p_y:.2f} | Distancia pico a pico Z: {p2p_z:.2f}")

    def __update_temp_data(self, timestamp: int, temp: float) -> None:

        if self.__recording:
            self.__saved_data.append((temp, timestamp))

        self.__temp_label.setText(f"Temperatura: {temp} °C. Última actualización: {timestamp}")

    def __update_server_data(self, info: str) -> None:

        timestamp = datetime.now().timestamp()
        if self.__recording:
            self.__saved_data.append((info, timestamp))

        self.__server_label.setText(f"Información del servidor: {info}. Última actualización: {timestamp}")
    
    def __on_record_button_pressed(self) -> None:

        if not self.__recording:
            self.__recording = True
            self.__record_button.setText("Detener Grabación")
            return
        
        self.__recording = False
        self.__record_button.setText("Iniciar Grabación")

        with open('data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Source', 'topic', 'qos', 'ax', 'ay', 'az', 'Temperatura'])

            for i in self.__saved_data:
                if len(i) == 4:
                    writer.writerow([i[3], 'ESP32', i[0], i[1], i[2], '', ''])

                elif isinstance(i[0], float):
                    writer.writerow([i[1], 'ESP32', '', '', '', i[0], ''])

                else:
                    writer.writerow([i[1], 'Celular', '', '', '', '', i[0]])

        self.__saved_data = []

    def __on_apply_config_button_pressed(self) -> None:
        sensors_config = self.__config.get_sensors_config()
        accel_rate_hz = sensors_config.get("accel", {}).get("rate_hz", 50)
        temp_rate_hz = sensors_config.get("temp", {}).get("rate_hz", 0.067)

        new_config = {
            "accel": {
                "enabled": self.__accel_enabled_checkbox.isChecked(),
                "qos": int(self.__accel_qos_combo.currentText()),
                "rate_hz": accel_rate_hz
            },
            "temp": {
                "enabled": self.__temp_enabled_checkbox.isChecked(),
                "qos": int(self.__temp_qos_combo.currentText()),
                "rate_hz": temp_rate_hz
            }
        }

        self.__config.save_config(new_config)

    def __on_reload_config_button_pressed(self) -> None:
        self.__config.reset_to_default()
        self.__set_config_values()

    def __set_config_values(self) -> None:
        accel_config = self.__config.get_sensors_config().get("accel")
        temp_config = self.__config.get_sensors_config().get("temp")

        self.__accel_enabled_checkbox.setChecked(accel_config.get("enabled"))
        self.__accel_qos_combo.setCurrentText(str(accel_config.get("qos")))

        self.__temp_enabled_checkbox.setChecked(temp_config.get("enabled"))
        self.__temp_qos_combo.setCurrentText(str(temp_config.get("qos")))

        