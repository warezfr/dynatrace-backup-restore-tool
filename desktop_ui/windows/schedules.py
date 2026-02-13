"""Schedules management window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QCheckBox, QMessageBox,
    QHeaderView, QGroupBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        title_text = "Edit Schedule" if self.schedule else "New Schedule"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Name
        layout.addWidget(QLabel("Schedule Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency:"))
        self.freq_combo = QComboBox()
        self.freq_combo.addItems(["Daily", "Weekly", "Monthly", "Custom Cron"])
        freq_layout.addWidget(self.freq_combo)
        layout.addLayout(freq_layout)
        
        # Time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time:"))
        self.hour_spin = QSpinBox()
        self.hour_spin.setMinimum(0)
        self.hour_spin.setMaximum(23)
        self.hour_spin.setValue(2)
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(QLabel(":"))
        self.minute_spin = QSpinBox()
        self.minute_spin.setMinimum(0)
        self.minute_spin.setMaximum(59)
        time_layout.addWidget(self.minute_spin)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # Backup type
        layout.addWidget(QLabel("Config Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "All Configurations",
            "Alerting Profiles",
            "Dashboards",
            "SLO",
            "Rules",
            "Maintenance Windows",
            "Notification Channels",
            "Management Zones",
            "Anomaly Detection",
            "Auto Tags",
            "Application Detection Rules",
            "Service Detection",
            "Request Attributes",
            "Metric Events",
            "Synthetic Monitors",
            "Extensions"
        ])
        layout.addWidget(self.type_combo)
        
        # Enabled
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("✓ Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setGeometry(100, 100, 400, 350)

class SchedulesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Backup Schedules")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Schedules table
        table_group = QGroupBox("Scheduled Backups")
        table_layout = QVBoxLayout()
        
        self.schedules_table = QTableWidget()
        self.schedules_table.setColumnCount(7)
        self.schedules_table.setHorizontalHeaderLabels([
            "Name", "Type", "Frequency", "Time", "Enabled", "Last Run", "Next Run"
        ])
        
        header = self.schedules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        # Add sample data
        self._add_schedule_row("Daily Alerting Backup", "Alerting", "Daily", "02:00", True, "Today 02:15", "Tomorrow 02:00")
        self._add_schedule_row("Weekly Full Backup", "All Configs", "Weekly", "03:00", True, "Sun 03:30", "Next Sun 03:00")
        self._add_schedule_row("Dashboard Backup", "Dashboards", "Daily", "12:00", False, "N/A", "N/A")
        
        table_layout.addWidget(self.schedules_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_btn = QPushButton("➕ New Schedule")
        add_btn.clicked.connect(self.add_schedule)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.clicked.connect(self.edit_schedule)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_schedule)
        button_layout.addWidget(delete_btn)
        
        toggle_btn = QPushButton("🔄 Toggle")
        toggle_btn.clicked.connect(self.toggle_schedule)
        button_layout.addWidget(toggle_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _add_schedule_row(self, name: str, type_: str, freq: str, time: str, enabled: bool, last_run: str, next_run: str):
        """Add a row to the schedules table"""
        row = self.schedules_table.rowCount()
        self.schedules_table.insertRow(row)
        
        self.schedules_table.setItem(row, 0, QTableWidgetItem(name))
        self.schedules_table.setItem(row, 1, QTableWidgetItem(type_))
        self.schedules_table.setItem(row, 2, QTableWidgetItem(freq))
        self.schedules_table.setItem(row, 3, QTableWidgetItem(time))
        
        status_item = QTableWidgetItem("✓" if enabled else "✕")
        if enabled:
            status_item.setForeground(QColor(0, 176, 80))
        else:
            status_item.setForeground(QColor(255, 0, 0))
        self.schedules_table.setItem(row, 4, status_item)
        
        self.schedules_table.setItem(row, 5, QTableWidgetItem(last_run))
        self.schedules_table.setItem(row, 6, QTableWidgetItem(next_run))
    
    def add_schedule(self):
        """Add new schedule"""
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Schedule created successfully")
    
    def edit_schedule(self):
        """Edit selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a schedule")
            return
        
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Schedule updated successfully")
    
    def delete_schedule(self):
        """Delete selected schedule"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a schedule")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this schedule?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.schedules_table.removeRow(current_row)
            QMessageBox.information(self, "Success", "Schedule deleted")
    
    def toggle_schedule(self):
        """Toggle schedule enabled/disabled"""
        current_row = self.schedules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a schedule")
            return
        
        current_status = self.schedules_table.item(current_row, 4).text()
        new_status = "✕" if current_status == "✓" else "✓"
        self.schedules_table.item(current_row, 4).setText(new_status)
