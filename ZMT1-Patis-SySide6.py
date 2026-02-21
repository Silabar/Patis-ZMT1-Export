import sys
import os
import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                               QLineEdit, QPushButton, QGridLayout,
                               QFileDialog, QGroupBox, QVBoxLayout)
from PySide6.QtCore import Qt


class PatisZMT1App(QMainWindow):
    def __init__(self, landingzone=""):
        super().__init__()
        self.patis_landingzone = landingzone
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Patis-ZMT1")
        self.setMinimumWidth(350)

        # Zentrales Widget und Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        grid_layout = QGridLayout()

        # Eingabefelder (Widgets)
        self.labels = ["Sachnummer", "Startserialnummer", "Endserialnummer", "Auftrag", "Rev-Stand"]
        self.entries = {}

        for i, text in enumerate(self.labels):
            lbl = QLabel(text)
            entry = QLineEdit()
            grid_layout.addWidget(lbl, i, 0)
            grid_layout.addWidget(entry, i, 1)
            self.entries[text] = entry

        # Buttons
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.reset_fields)

        btn_exec = QPushButton("ZMT1-File erzeugen")
        btn_exec.setStyleSheet("background-color: #e1e1e1; font-weight: bold;")
        btn_exec.clicked.connect(self.check_inputs)

        grid_layout.addWidget(btn_reset, 5, 0)
        grid_layout.addWidget(btn_exec, 5, 1)

        # Status Bereich (ähnlich LabelFrame)
        self.status_group = QGroupBox("Status:")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Bitte Werte eintragen")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        self.status_group.setLayout(status_layout)

        # Alles zusammenfügen
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.status_group)

        self.set_status("Bereit", "yellow")

    def set_status(self, text, color):
        # Farbanpassung für Qt Stylesheets
        color_map = {
            "green": "#90EE90",
            "red": "#FFB6C1",
            "yellow": "#FFFFE0"
        }
        hex_color = color_map.get(color, color)
        self.status_label.setText(text)
        self.status_group.setStyleSheet(f"background-color: {hex_color};")

    def reset_fields(self):
        for entry in self.entries.values():
            entry.clear()
        self.entries["Sachnummer"].setFocus()
        self.set_status("Reset erfolgreich", "green")

    def check_inputs(self):
        # Daten aus Dictionary holen
        s = self.entries["Sachnummer"].text()
        ss = self.entries["Startserialnummer"].text()
        se = self.entries["Endserialnummer"].text()
        a = self.entries["Auftrag"].text()
        r = self.entries["Rev-Stand"].text()

        if not s.isdigit() or not (7 <= len(s) <= 8):
            return self.set_status("Sachnummer muss 7-8 Stellen haben!", "red")
        if not ss.isdigit() or not se.isdigit():
            return self.set_status("Seriennummern müssen Zahlen sein!", "red")
        if int(ss) > int(se):
            return self.set_status("Endserial >= Startserial!", "red")
        if not a.isdigit() or len(a) != 7:
            return self.set_status("Auftrag muss 7 Stellen haben!", "red")

        self.create_zmt1_file(s, ss, se, a, r)

    def create_zmt1_file(self, sachnummer, serialstart, serialend, auftrag, revstand):
        jetzt = datetime.datetime.now()

        # Verzeichnis wählen
        initial_dir = self.patis_landingzone if os.path.exists(self.patis_landingzone) else ""
        verzeichnis = QFileDialog.getExistingDirectory(self, "Verzeichnis wählen", initial_dir)

        if not verzeichnis:
            return self.set_status("Abbruch durch Benutzer", "red")

        eintraege = []
        for i in range(int(serialstart), int(serialend) + 1):
            line = (sachnummer.zfill(18) + str(i)).ljust(36) + \
                   "1030" + auftrag.zfill(12) + \
                   " " * 13 + revstand.zfill(2) + "  n.a." + \
                   " " * 26 + jetzt.strftime("%Y%m%d") + "FME     "
            eintraege.append(line)

        filename = f"FME_ZMT1_{jetzt.strftime('%M%S_%Y%m%d_%H')}.DAT"
        path = os.path.join(verzeichnis, filename)

        try:
            with open(path, "w") as f:
                f.write(str(len(eintraege)).zfill(6) + "\n")
                for x in eintraege:
                    f.write(x + "\n")
            self.set_status(f"Datei {filename} erzeugt", "green")
        except IOError:
            self.set_status("Schreibfehler!", "red")


if __name__ == "__main__":
    landing = sys.argv[1] if len(sys.argv) > 1 else ""
    app = QApplication(sys.argv)
    window = PatisZMT1App(landing)
    window.show()
    sys.exit(app.exec())