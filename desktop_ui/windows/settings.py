"""Settings window"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QCheckBox, QSpinBox, QTabWidget, QWidget, QGroupBox, QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QFont

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 500, 600)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        
        # General settings
        general_tab = self._create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Backup settings
        backup_tab = self._create_backup_tab()
        tabs.addTab(backup_tab, "Backup")
        
        # Advanced settings
        advanced_tab = self._create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("✓ Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Application")
        group_layout = QVBoxLayout()
        
        # Theme
        group_layout.addWidget(QLabel("Theme:"))
        theme_combo = self._create_combo(["Light", "Dark", "Auto"])
        group_layout.addWidget(theme_combo)
        
        # Language
        group_layout.addWidget(QLabel("Language:"))
        lang_combo = self._create_combo(["English", "Français", "Deutsch"])
        group_layout.addWidget(lang_combo)
        
        # Auto-refresh
        auto_refresh = QCheckBox("Auto-refresh dashboard (every 30 seconds)")
        auto_refresh.setChecked(True)
        group_layout.addWidget(auto_refresh)
        
        # Startup
        startup = QCheckBox("Start with system")
        group_layout.addWidget(startup)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_backup_tab(self) -> QWidget:
        """Create backup settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Backup location
        group1 = QGroupBox("Backup Storage")
        group1_layout = QVBoxLayout()
        
        group1_layout.addWidget(QLabel("Backup Directory:"))
        path_layout = QHBoxLayout()
        path_input = QLineEdit()
        path_input.setText("D:\\backups\\dynatrace")
        path_layout.addWidget(path_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: QFileDialog.getExistingDirectory(self))
        path_layout.addWidget(browse_btn)
        group1_layout.addLayout(path_layout)
        
        group1.setLayout(group1_layout)
        layout.addWidget(group1)
        
        # Retention
        group2 = QGroupBox("Retention Policy")
        group2_layout = QVBoxLayout()
        
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Keep backups for:"))
        retention_spin = QSpinBox()
        retention_spin.setMinimum(1)
        retention_spin.setMaximum(365)
        retention_spin.setValue(30)
        retention_layout.addWidget(retention_spin)
        retention_layout.addWidget(QLabel("days"))
        retention_layout.addStretch()
        group2_layout.addLayout(retention_layout)
        
        auto_delete = QCheckBox("Automatically delete old backups")
        auto_delete.setChecked(True)
        group2_layout.addWidget(auto_delete)
        
        group2.setLayout(group2_layout)
        layout.addWidget(group2)
        
        # Compression
        group3 = QGroupBox("Compression")
        group3_layout = QVBoxLayout()
        
        compress = QCheckBox("Compress backups automatically")
        compress.setChecked(True)
        group3_layout.addWidget(compress)
        
        encrypt = QCheckBox("Encrypt sensitive data")
        group3_layout.addWidget(encrypt)
        
        group3.setLayout(group3_layout)
        layout.addWidget(group3)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # API settings
        group1 = QGroupBox("API Configuration")
        group1_layout = QVBoxLayout()
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("API Host:"))
        host_input = QLineEdit()
        host_input.setText("127.0.0.1")
        host_layout.addWidget(host_input)
        group1_layout.addLayout(host_layout)
        
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("API Port:"))
        port_spin = QSpinBox()
        port_spin.setMinimum(1024)
        port_spin.setMaximum(65535)
        port_spin.setValue(8000)
        port_layout.addWidget(port_spin)
        port_layout.addStretch()
        group1_layout.addLayout(port_layout)
        
        group1.setLayout(group1_layout)
        layout.addWidget(group1)
        
        # Logging
        group2 = QGroupBox("Logging")
        group2_layout = QVBoxLayout()
        
        debug = QCheckBox("Enable debug logging")
        group2_layout.addWidget(debug)
        
        group2.setLayout(group2_layout)
        layout.addWidget(group2)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_combo(self, items: list):
        """Create a combo box with items"""
        from PyQt6.QtWidgets import QComboBox
        combo = QComboBox()
        combo.addItems(items)
        return combo
    
    def save_settings(self):
        """Save settings"""
        QMessageBox.information(self, "Success", "Settings saved successfully")
        self.accept()
