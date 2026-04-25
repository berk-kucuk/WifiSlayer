from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QLabel, QMessageBox, QAbstractItemView, QApplication)
from PyQt6.QtCore import QTimer, Qt, QItemSelectionModel
from backend import WifiSlayerBackend
import sys

DARK_STYLESHEET = """
QWidget {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
}
QTableWidget {
    background-color: #050505;
    alternate-background-color: #0a0a0a;
    gridline-color: #222222;
    border: 1px solid #222222;
    color: #ffffff;
}
QTableWidget::item:selected {
    background-color: #aa0000;
    color: #ffffff;
    font-weight: bold;
}
QHeaderView::section {
    background-color: #111111;
    color: #ffffff;
    padding: 2px;
    border: 1px solid #000000;
    font-weight: bold;
    font-size: 10px;
}
QPushButton {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #333333;
    border-radius: 2px;
    padding: 6px;
}
QPushButton:hover {
    background-color: #333333;
}
QPushButton:disabled {
    background-color: #0a0a0a;
    color: #555555;
    border: 1px solid #111111;
}
QComboBox {
    background-color: #111111;
    border: 1px solid #333333;
    padding: 2px;
    color: #ffffff;
}
"""

class WifiSlayerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = WifiSlayerBackend()
        self.is_scanning = False
        self.is_attacking = False

        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        self.setWindowTitle("WifiSlayer - Deauth")
        self.setStyleSheet(DARK_STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        top_layout = QHBoxLayout()
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(self.backend.get_wireless_interfaces())

        self.btn_monitor = QPushButton("Set")
        self.btn_monitor.clicked.connect(self.enable_monitor_mode)

        self.btn_exit = QPushButton("X")
        self.btn_exit.setStyleSheet("background-color: #550000; color: white; border: 1px solid #ff0000;")
        self.btn_exit.setFixedWidth(30)
        self.btn_exit.clicked.connect(self.close)

        top_layout.addWidget(self.interface_combo, stretch=2)
        top_layout.addWidget(self.btn_monitor, stretch=1)
        top_layout.addWidget(self.btn_exit)
        layout.addLayout(top_layout)

        self.status_label = QLabel("Status: Waiting")
        self.status_label.setStyleSheet("color: #aaaaaa; font-weight: bold; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["SSID", "BSSID", "CH"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        self.btn_scan = QPushButton("Scan")
        self.btn_scan.setEnabled(False)
        self.btn_scan.clicked.connect(self.toggle_scan)

        self.btn_attack = QPushButton("Attack")
        self.btn_attack.setEnabled(False)
        self.btn_attack.clicked.connect(self.toggle_attack)

        bottom_layout.addWidget(self.btn_scan)
        bottom_layout.addWidget(self.btn_attack)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        self.showFullScreen()

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)

    def force_stop_all(self):
        if self.is_attacking:
            self.toggle_attack()
        if self.is_scanning:
            self.toggle_scan()
        self.table.setRowCount(0)

    def enable_monitor_mode(self):
        iface = self.interface_combo.currentText()
        if not iface:
            QMessageBox.warning(self, "Error", "No interface found.")
            return

        self.force_stop_all()
        self.btn_scan.setEnabled(False)
        self.btn_attack.setEnabled(False)

        self.status_label.setText("Status: Configuring...")
        self.status_label.setStyleSheet("color: #ffff00;")

        QApplication.processEvents()

        mon_iface = self.backend.setup_interface(iface)

        self.status_label.setText(f"Active: {mon_iface}")
        self.status_label.setStyleSheet("color: #00ff00;")
        self.btn_scan.setEnabled(True)

    def toggle_scan(self):
        if not self.is_scanning:
            self.backend.start_scan()
            self.timer.start(1500)
            self.btn_scan.setText("Stop Scan")
            self.btn_scan.setStyleSheet("background-color: #880000; color: white;")
            self.is_scanning = True
            self.btn_attack.setEnabled(False)
        else:
            self.timer.stop()
            self.backend.stop_scan()
            self.btn_scan.setText("Scan")
            self.btn_scan.setStyleSheet("")
            self.is_scanning = False
            self.btn_attack.setEnabled(True)

    def update_table(self):
        targets = self.backend.get_live_targets()

        # Seçili MAC'leri hatırla
        selected_macs = set()
        for item in self.table.selectedItems():
            if item.column() == 1:
                selected_macs.add(item.text())

        # Tabloyu güncelleme sırasında sinyalleri blokla (toggle sorunu önlenir)
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        sel_model = self.table.selectionModel()

        for row, target in enumerate(targets):
            self.table.insertRow(row)
            essid = target['essid']
            if len(essid) > 15:
                essid = essid[:12] + "..."

            self.table.setItem(row, 0, QTableWidgetItem(essid))
            self.table.setItem(row, 1, QTableWidgetItem(target['bssid']))
            self.table.setItem(row, 2, QTableWidgetItem(target['channel']))

            # DÜZELTME: selectRow() yerine selectionModel ile seç (toggle sorunu yok)
            if target['bssid'] in selected_macs:
                for col in range(self.table.columnCount()):
                    idx = self.table.model().index(row, col)
                    sel_model.select(idx, QItemSelectionModel.SelectionFlag.Select)

        self.table.blockSignals(False)

    def toggle_attack(self):
        if not self.is_attacking:
            selected_items = self.table.selectedItems()
            if not selected_items:
                return

            selected_rows = set(item.row() for item in selected_items)

            bssids = []
            channels = []
            essids = []

            for row in selected_rows:
                essids.append(self.table.item(row, 0).text())
                bssids.append(self.table.item(row, 1).text())
                channels.append(self.table.item(row, 2).text())

            self.backend.start_attack(bssids, channels)

            self.btn_attack.setText("Stop Attack")
            self.btn_attack.setStyleSheet("background-color: #aa0000; color: white;")

            if len(selected_rows) == 1:
                status_text = f"ATTACKING: {essids[0]}"
            else:
                status_text = f"ATTACKING: {len(selected_rows)} TARGETS"

            self.status_label.setText(status_text)
            self.status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
            self.is_attacking = True
            self.btn_scan.setEnabled(False)
            self.btn_monitor.setEnabled(False)
        else:
            self.backend.stop_attack()
            self.btn_attack.setText("Attack")
            self.btn_attack.setStyleSheet("")

            mon_iface = self.backend.monitor_interface
            self.status_label.setText(f"Active: {mon_iface}")
            self.status_label.setStyleSheet("color: #00ff00;")

            self.is_attacking = False
            self.btn_scan.setEnabled(True)
            self.btn_monitor.setEnabled(True)

    def closeEvent(self, event):
        self.status_label.setText("Closing...")
        self.backend.cleanup()
        event.accept()
