"""Backup wizard window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QLineEdit, QTextEdit, QCheckBox, QSpinBox, QGroupBox, QProgressBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class BackupWizardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Create New Backup")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Connection selection
        conn_group = QGroupBox("Dynatrace Connection")
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Environment:"))
        self.conn_combo = QComboBox()
        self.conn_combo.addItems(["Select a connection", "Production", "Staging", "Development"])
        conn_layout.addWidget(self.conn_combo)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Config type selection
        config_group = QGroupBox("Configuration Type")
        config_layout = QVBoxLayout()
        
        self.config_checks = []
        for config_type in [
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
            "Extensions",
        ]:
            check = QCheckBox(config_type)
            check.setChecked(config_type == "All Configurations")
            self.config_checks.append(check)
            config_layout.addWidget(check)
        
        # Management zone filter
        mz_layout = QHBoxLayout()
        mz_layout.addWidget(QLabel("Filter by Management Zone:"))
        self.mz_combo = QComboBox()
        self.mz_combo.addItems(["All Zones", "Zone 1", "Zone 2", "Zone 3"])
        mz_layout.addWidget(self.mz_combo)
        config_layout.addLayout(mz_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.compress_check = QCheckBox("Compress backup (ZIP)")
        self.compress_check.setChecked(True)
        options_layout.addWidget(self.compress_check)
        
        self.encrypt_check = QCheckBox("Encrypt sensitive data")
        options_layout.addWidget(self.encrypt_check)
        
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_text = QTextEdit()
        self.desc_text.setMaximumHeight(80)
        desc_layout.addWidget(self.desc_text)
        options_layout.addLayout(desc_layout)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready to start")
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.validate_btn = QPushButton("✓ Validate")
        self.validate_btn.clicked.connect(self.validate_config)
        button_layout.addWidget(self.validate_btn)
        
        self.start_btn = QPushButton("▶ Start Backup")
        self.start_btn.clicked.connect(self.start_backup)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("✕ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_backup)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def validate_config(self):
        """Validate backup configuration"""
        if self.conn_combo.currentText() == "Select a connection":
            QMessageBox.warning(self, "Validation Error", "Please select a Dynatrace connection")
            return
        
        QMessageBox.information(self, "Validation", "Configuration is valid ✓")
    
    def start_backup(self):
        """Start the backup"""
        self.progress_label.setText("Starting backup...")
        self.progress_bar.setValue(0)
        # TODO: Connect to API
    
    def cancel_backup(self):
        """Cancel the backup"""
        self.progress_label.setText("Cancelled")
        self.progress_bar.setValue(0)
