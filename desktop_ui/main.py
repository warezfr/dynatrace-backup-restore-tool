"""Main PyQt6 desktop application"""
import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QLabel, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from .windows.dashboard import DashboardWindow
from .windows.backup_wizard import BackupWizardWindow
from .windows.restore_wizard import RestoreWizardWindow
from .windows.connections import ConnectionsWindow
from .windows.environments import EnvironmentsWindow
from .windows.schedules import SchedulesWindow
from .windows.settings import SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynatrace Backup Manager - Multi-Tenant Edition")
        self.setGeometry(100, 100, 1300, 900)
        
        # Set font
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.dashboard_window = DashboardWindow()
        self.environments_window = EnvironmentsWindow()  # NEW: Multi-environment management
        self.backup_wizard = BackupWizardWindow()
        self.restore_wizard = RestoreWizardWindow()
        self.connections_window = ConnectionsWindow()
        self.schedules_window = SchedulesWindow()
        
        self.tabs.addTab(self.dashboard_window, "Dashboard")
        self.tabs.addTab(self.environments_window, "🌍 Environments")  # NEW
        self.tabs.addTab(self.backup_wizard, "New Backup")
        self.tabs.addTab(self.restore_wizard, "Restore")
        self.tabs.addTab(self.connections_window, "Connections (Legacy)")
        self.tabs.addTab(self.schedules_window, "Schedules")
        
        layout.addWidget(self.tabs)
        
        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready - Multi-Tenant Mode Enabled")
        
        self.show()
    
    def _create_toolbar(self) -> QHBoxLayout:
        """Create toolbar"""
        layout = QHBoxLayout()
        
        label = QLabel("Dynatrace Backup Manager v1.1.0 - Multi-Tenant Edition")
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(label)
        
        layout.addStretch()
        
        # Multi-environment indicator
        env_label = QLabel("📊 Multi-Environment Support: ENABLED")
        env_label.setFont(QFont("Segoe UI", 9))
        layout.addWidget(env_label)
        
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)
        
        return layout
    
    def _open_settings(self):
        """Open settings dialog"""
        settings_window = SettingsWindow(self)
        settings_window.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
