import asyncio
import time
from math import sqrt
import csv
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QInputDialog,
    QTabWidget, QCheckBox, QComboBox, QTableWidget,
    QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt

from classes.Signal import Signal
from classes.Config import Config

class MainWindow(QMainWindow):
    def __init__(self, event: asyncio.Event) -> None:
        super().__init__()

        self.__event = event
        self.__close_event = asyncio.Event()

        self.__config = Config()
        self.__signals = Signal()
        self.__recording = False
        self.__saved_data = []

        self.__signals.accel_data_signal.connect(self.__update_accel_data)
        self.__signals.temp_data_signal.connect(self.__update_temp_data)
        self.__signals.status_data_signal.connect(self.__update_state_data)
        self.__signals.update_status_signal.connect(self.__update_status)

        self.setWindowTitle("Raspberry BLE Client")
        self.setGeometry(100, 100, 800, 600)

        self.__tab_widget = QTabWidget()
        self.__accel_tab = QWidget()
        self.__temp_tab = QWidget()
        self.__status_tab = QWidget()
        self.__config_tab = QWidget()

        self.__min_time = 2000
        self.__accel_data = []
        self.__accel_message_count = 0
        self.__accel_last_timestamp = None
        self.__accel_plot = pg.PlotWidget(title="Gráfico de Aceleración")
        self.__accel_plot.setFixedSize(760, 300)
        self.__accel_plot.addLegend()
        self.__accel_plot.setLabel('left', 'Aceleración (m/s²)')
        self.__accel_plot.setLabel('bottom', 'Muestras')
        self.__accel_plot.setYRange(-20, 20)

        self.__temp_data = []
        self.__temp_message_count = 0
        self.__temp_last_timestamp = None
        self.__temp_plot = pg.PlotWidget(title="Gráfico de Temperatura")
        self.__temp_plot.setFixedSize(760, 300)
        self.__temp_plot.setLabel('left', 'Temperatura (°C)')
        self.__temp_plot.setLabel('bottom', 'Muestras')
        self.__temp_plot.setXRange(0, 30, padding=0)
        self.__temp_plot.setYRange(0, 40)

        self.__record_button = QPushButton("Iniciar Grabación", self)
        self.__range_button = QPushButton("Ajustar ventana", self)

        self.__record_button.clicked.connect(self.__on_record_button_pressed)
        self.__range_button.clicked.connect(self.__on_range_button_pressed)

        self.__temp_label = QLabel("Temperatura: N/A", self)

        self.__rms_label = QLabel("RMSx: N/A | RMSy: N/A | RMSz: N/A", self)
        self.__peak_label = QLabel("Peak+ X: N/A | Peak+ Y: N/A | Peak+ Z: N/A", self)
        self.__p2p_label = QLabel("Pk-Pk X: N/A | Pk-Pk Y: N/A | Pk-Pk Z: N/A", self)

        accel_layout = QVBoxLayout(self.__accel_tab)
        accel_layout.addWidget(self.__accel_plot)
        accel_layout.addWidget(self.__rms_label)
        accel_layout.addWidget(self.__peak_label)
        accel_layout.addWidget(self.__p2p_label)
        accel_layout.addWidget(self.__range_button)

        temp_layout = QVBoxLayout(self.__temp_tab)
        temp_layout.addWidget(self.__temp_label)
        temp_layout.addWidget(self.__temp_plot)
        
        status_layout = QVBoxLayout(self.__status_tab)
        self.__status_table = QTableWidget(2, 4, self)
        self.__status_table.setHorizontalHeaderLabels([
            "Tópico",
            "QoS activo",
            "Último mensaje (s atrás)",
            "Mensajes recibidos",
        ])
        self.__status_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.__status_table.verticalHeader().setVisible(False)
        self.__status_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.__status_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.__status_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.__status_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.__status_table.setItem(0, 0, QTableWidgetItem("Acelerómetro"))
        self.__status_table.setItem(1, 0, QTableWidgetItem("Temperatura"))
        status_layout.addWidget(self.__status_table, 1)

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
        config_layout.addWidget(self.__apply_config_button, alignment=Qt.AlignmentFlag.AlignRight)
        config_layout.addWidget(self.__reload_config_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.__tab_widget.addTab(self.__accel_tab, "Aceleración")
        self.__tab_widget.addTab(self.__temp_tab, "Temperatura")
        self.__tab_widget.addTab(self.__status_tab, "Estado")
        self.__tab_widget.addTab(self.__config_tab, "Configuración")

        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.addWidget(self.__record_button)
        top_bar_layout.addStretch()

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.addWidget(top_bar)
        container_layout.addWidget(self.__tab_widget)
        self.setCentralWidget(container)

    def closeEvent(self, event) -> None:
        self.__close_event.set()
        super().closeEvent(event)

    def __on_range_button_pressed(self) -> None:
        value, ok = QInputDialog.getInt(
            self,
            "Ajustar ventana de aceleración",
            "Min time (ms):",
            self.__min_time,
            2000,
            15000,
            1,
        )
        if ok:
            self.__min_time = value
            if self.__accel_data:
                self.__plot_accel_data(self.__accel_data[-1][3])

    def __update_accel_data(self, timestamp: int, x: float, y: float, z: float) -> None:

        self.__accel_message_count += 1
        self.__accel_last_timestamp = timestamp

        if self.__recording:
            self.__saved_data.append(((x, y, z, timestamp), 0))

        if len(self.__accel_data) >= 20000:
            self.__accel_data.pop(0)
        self.__accel_data.append((x, y, z, timestamp))

        self.__plot_accel_data(timestamp)

    def __plot_accel_data(self, timestamp: int) -> None:
        const = self.__min_time - timestamp
        recent_samples = [sample for sample in self.__accel_data if sample[3] + const >= 0]

        if not recent_samples:
            return

        t_data = [sample[3] + const for sample in recent_samples]
        x_data = [sample[0] for sample in recent_samples]
        y_data = [sample[1] for sample in recent_samples]
        z_data = [sample[2] for sample in recent_samples]

        self.__accel_plot.clear()
        self.__accel_plot.setXRange(0, self.__min_time, padding=0)
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

        self.__temp_message_count += 1
        self.__temp_last_timestamp = timestamp

        if self.__recording:
            self.__saved_data.append(((temp, timestamp), 1))

        if len(self.__temp_data) >= 30:
            self.__temp_data.pop(0)
        self.__temp_data.append(temp)

        self.__temp_label.setText(f"Temperatura: {temp} °C. Última actualización: {timestamp}")

        plot_data = self.__temp_data[-30:]
        self.__temp_plot.clear()
        self.__temp_plot.plot(list(range(len(plot_data))), plot_data, pen='r')
        
    def __update_state_data(self, timestamp: int, status: int) -> None:

        if self.__recording:
            self.__saved_data.append(((status, timestamp), 2))

    def __on_record_button_pressed(self) -> None:

        if not self.__recording:
            self.__recording = True
            self.__record_button.setText("Detener Grabación")
            return
        
        self.__recording = False
        self.__record_button.setText("Iniciar Grabación")

        with open('data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp_ms', 'source', 'topic', 'qos', 'ax', 'ay', 'az', 'temperature'])

            accel_config = self.__config.get_sensors_accel_config()
            temp_config = self.__config.get_sensors_temp_config()

            accel_qos = accel_config.get("qos", 0)
            temp_qos = temp_config.get("qos", 0)

            for data, data_type in self.__saved_data:
                if data_type == 0:
                    writer.writerow([data[3], 'rpi4', 'iot/rpi4/accel', accel_qos, data[0], data[1], data[2], ''])

                elif data_type == 1:
                    writer.writerow([data[1], 'rpi4', 'iot/rpi4/temp', temp_qos, '', '', '', data[0]])

                elif data_type == 2:
                    writer.writerow([data[1], 'rpi4', 'iot/status/rpi4', 1, '', '', '', '', ''])

        self.__saved_data = []

    def __on_apply_config_button_pressed(self) -> None:

        accel_config = self.__config.get_sensors_accel_config()
        temp_config = self.__config.get_sensors_temp_config()

        accel_rate_hz = accel_config.get("rate_hz", 50)
        temp_rate_hz = temp_config.get("rate_hz", 0.067)

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
        self.__event.set()

    def __on_reload_config_button_pressed(self) -> None:
        self.__set_config_values()

    def __set_config_values(self) -> None:
        accel_config = self.__config.get_sensors_accel_config()
        temp_config = self.__config.get_sensors_temp_config()

        self.__accel_enabled_checkbox.setChecked(accel_config.get("enabled"))
        self.__accel_qos_combo.setCurrentText(str(accel_config.get("qos")))

        self.__temp_enabled_checkbox.setChecked(temp_config.get("enabled"))
        self.__temp_qos_combo.setCurrentText(str(temp_config.get("qos")))

    def __update_status(self) -> None:
        now_ms = time.monotonic_ns() // 1_000_000

        accel_config = self.__config.get_sensors_accel_config()
        temp_config = self.__config.get_sensors_temp_config()

        status_rows = [
            (
                "Acelerómetro",
                accel_config.get("qos", 0),
                self.__accel_last_timestamp,
                self.__accel_message_count,
            ),
            (
                "Temperatura",
                temp_config.get("qos", 0),
                self.__temp_last_timestamp,
                self.__temp_message_count,
            ),
        ]

        for row, (topic, qos, last_timestamp, message_count) in enumerate(status_rows):
            self.__status_table.setItem(row, 0, QTableWidgetItem(topic))
            self.__status_table.setItem(row, 1, QTableWidgetItem(str(qos)))

            if last_timestamp is None:
                last_text = "N/A"

            else:
                elapsed_s = max(0.0, (now_ms - last_timestamp) / 1000)
                last_text = f"{elapsed_s:.1f}"

            self.__status_table.setItem(row, 2, QTableWidgetItem(last_text))
            self.__status_table.setItem(row, 3, QTableWidgetItem(str(message_count)))

    def wait_for_close(self) -> asyncio.Future:
        return self.__close_event.wait()

    def emit_accel_signal(self, timestamp: int, ax: float, ay: float, az: float) -> None:
        self.__signals.accel_data_signal.emit(timestamp, ax, ay, az)

    def emit_temp_signal(self, timestamp: int, temperature: float) -> None:
        self.__signals.temp_data_signal.emit(timestamp, temperature)

    def emit_status_signal(self, timestamp: int, status: int) -> None:
        self.__signals.status_data_signal.emit(timestamp, status)
    
    def emit_update_status_signal(self) -> None:
        self.__signals.update_status_signal.emit()
