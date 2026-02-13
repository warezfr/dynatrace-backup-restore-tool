"""Restore wizard window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QCheckBox, QGroupBox, QProgressBar,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class RestoreWizardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Restore Configuration")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Backup selection
        backup_group = QGroupBox("Select Backup")
        backup_layout = QVBoxLayout()
        
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Backup:"))
        self.backup_combo = QComboBox()
        self.backup_combo.addItems([
            "backup_alerting_20260210_123456",
            "backup_dashboards_20260209_102030",
            "backup_all_20260208_150000"
        ])
        select_layout.addWidget(self.backup_combo)
        select_layout.addWidget(QPushButton("📂 Browse"))
        backup_layout.addLayout(select_layout)
        
        # Backup details
        details_label = QLabel("Backup Details:")
        details_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        backup_layout.addWidget(details_label)
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(2)
        self.details_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.details_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.details_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.details_table.setMaximumHeight(150)
        backup_layout.addWidget(self.details_table)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Target environment
        target_group = QGroupBox("Target Environment")
        target_layout = QVBoxLayout()
        
        env_layout = QHBoxLayout()
        env_layout.addWidget(QLabel("Environment:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Production", "Staging", "Development"])
        env_layout.addWidget(self.target_combo)
        target_layout.addLayout(env_layout)
        
        # Management zone filter
        mz_layout = QHBoxLayout()
        mz_layout.addWidget(QLabel("Restore to Management Zone:"))
        self.target_mz_combo = QComboBox()
        self.target_mz_combo.addItems(["All Zones", "Zone 1", "Zone 2", "Zone 3"])
        mz_layout.addWidget(self.target_mz_combo)
        target_layout.addLayout(mz_layout)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # Options
        options_group = QGroupBox("Restore Options")
        options_layout = QVBoxLayout()
        
        self.dry_run_check = QCheckBox("Dry Run (Validate without applying)")
        options_layout.addWidget(self.dry_run_check)
        
        self.overwrite_check = QCheckBox("Overwrite existing configurations")
        self.overwrite_check.setChecked(True)
        options_layout.addWidget(self.overwrite_check)
        
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
        
        self.restore_btn = QPushButton("▶ Start Restore")
        self.restore_btn.clicked.connect(self.start_restore)
        button_layout.addWidget(self.restore_btn)
        
        self.cancel_btn = QPushButton("✕ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_restore)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def validate_config(self):
        """Validate restore configuration"""
        if self.backup_combo.currentText() == "Select a backup":
            QMessageBox.warning(self, "Validation Error", "Please select a backup")
            return
        
        QMessageBox.information(self, "Validation", "Configuration is valid ✓")
    
    def start_restore(self):
        """Start the restore"""
        if self.dry_run_check.isChecked():
            reply = QMessageBox.question(
                self,
                "Dry Run Mode",
                "Running in DRY RUN mode - no changes will be applied. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        else:
            reply = QMessageBox.warning(
                self,
                "Confirm Restore",
                "This will overwrite configurations. Are you sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.progress_label.setText("Starting restore...")
        self.progress_bar.setValue(0)
        # TODO: Connect to API
    
    def cancel_restore(self):
        """Cancel the restore"""
        self.progress_label.setText("Cancelled")
        self.progress_bar.setValue(0)
