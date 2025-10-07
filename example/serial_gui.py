# serial_gui.py
import sys
import time
from PySide6 import QtCore, QtWidgets
import serial
import serial.tools.list_ports


class SerialWorker(QtCore.QThread):
    data_received = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, port, baud=9600, timeout=1):
        super().__init__()
        self._stop = False
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(
                self.port, baudrate=self.baud, timeout=self.timeout)
        except Exception as e:
            self.error.emit(f"Erreur ouverture port: {e}")
            return

        while not self._stop:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline()
                    try:
                        text = line.decode(errors='ignore').strip()
                    except:
                        text = repr(line)
                    self.data_received.emit(text)
                else:
                    # éviter boucle CPU à 100%
                    time.sleep(0.05)
            except Exception as e:
                self.error.emit(f"Erreur lecture: {e}")
                break

        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except:
            pass

    def stop(self):
        self._stop = True
        self.wait(1000)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IHM Test — PySide6 + pyserial")

        # Widgets
        self.port_combo = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("Refresh ports")
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)

        # Layout
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.port_combo)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.connect_btn)

        main = QtWidgets.QVBoxLayout(self)
        main.addLayout(top)
        main.addWidget(self.log)

        # actions
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.toggle_connection)

        self.worker = None
        self.refresh_ports()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(f"{p.device} — {p.description}", p.device)
        if self.port_combo.count() == 0:
            self.port_combo.addItem("Aucun port détecté", "")

    def toggle_connection(self):
        if self.worker and self.worker.isRunning():
            self.append_log("Arrêt du worker...")
            self.worker.stop()
            self.worker = None
            self.connect_btn.setText("Connect")
            return

        port = self.port_combo.currentData()
        if not port:
            self.append_log("Sélectionne un port valide.")
            return

        self.worker = SerialWorker(port, baud=9600, timeout=0.5)
        self.worker.data_received.connect(self.on_data)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        self.connect_btn.setText("Disconnect")
        self.append_log(f"Connecté sur {port}")

    def on_data(self, txt):
        self.append_log(f"RX: {txt}")

    def on_error(self, err):
        self.append_log(f"ERREUR: {err}")

    def append_log(self, msg):
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.log.append(f"[{timestamp}] {msg}")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(700, 400)
    w.show()
    sys.exit(app.exec())
