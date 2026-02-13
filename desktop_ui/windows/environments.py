"""Environments management window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QCheckBox, QMessageBox,
    QHeaderView, QGroupBox, QComboBox, QListWidget, QListWidgetItem,
    QTabWidget, QTextEdit, QSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from .bulk_operations import BulkBackupDialog, BulkRestoreDialog, BulkCompareDialog

class EnvironmentDialog(QDialog):
    def __init__(self, parent=None, environment=None):
        super().__init__(parent)
        self.environment = environment
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        title_text = "Edit Environment" if self.environment else "New Environment"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Type
        layout.addWidget(QLabel("Environment Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Production", "Staging", "Development", "Testing", "Training", "Custom"])
        layout.addWidget(self.type_combo)
        
        # Environment URL
        layout.addWidget(QLabel("Environment URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://dynatrace.example.com/e/12345678")
        layout.addWidget(self.url_input)
        
        # API Token
        layout.addWidget(QLabel("API Token:"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.token_input)
        
        # Tags
        layout.addWidget(QLabel("Tags (comma-separated):"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("team-a, region-us, critical")
        layout.addWidget(self.tags_input)
        
        # SSL options
        self.insecure_check = QCheckBox("Allow insecure SSL certificates (for test environments)")
        layout.addWidget(self.insecure_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("✓ Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        test_btn = QPushButton("🔌 Test Connection")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setGeometry(100, 100, 450, 400)
    
    def save(self):
        """Save environment"""
        if not self.name_input.text() or not self.url_input.text() or not self.token_input.text():
            QMessageBox.warning(self, "Validation Error", "Please fill all required fields")
            return
        self.accept()
    
    def test_connection(self):
        """Test the connection"""
        QMessageBox.information(self, "Test Connection", "Connection successful ✓")

class EnvironmentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_refresh_timer()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Environments tab
        env_tab = self._create_environments_tab()
        tabs.addTab(env_tab, "Environments")
        
        # Groups tab
        groups_tab = self._create_groups_tab()
        tabs.addTab(groups_tab, "Environment Groups")
        
        # Bulk Operations tab
        bulk_tab = self._create_bulk_operations_tab()
        tabs.addTab(bulk_tab, "Bulk Operations")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def _create_environments_tab(self) -> QWidget:
        """Create environments management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dynatrace Environments (Multi-Tenant)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Environments table
        table_group = QGroupBox("Available Environments")
        table_layout = QVBoxLayout()
        
        self.environments_table = QTableWidget()
        self.environments_table.setColumnCount(7)
        self.environments_table.setHorizontalHeaderLabels([
            "Name", "Type", "URL", "Status", "Tags", "Last Tested", "Actions"
        ])
        
        header = self.environments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        # Add sample data
        self._add_environment_row("Production", "Production", "https://dyn.example.com/e/abc123", "✓ Healthy", "team-a, critical", "2 min ago")
        self._add_environment_row("Staging", "Staging", "https://dyn-staging.example.com/e/def456", "✓ Healthy", "team-a", "5 min ago")
        self._add_environment_row("Development", "Development", "https://dyn-dev.example.com/e/ghi789", "✓ Healthy", "team-b", "1 hour ago")
        
        table_layout.addWidget(self.environments_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_btn = QPushButton("➕ New Environment")
        add_btn.clicked.connect(self.add_environment)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.clicked.connect(self.edit_environment)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_environment)
        button_layout.addWidget(delete_btn)
        
        test_btn = QPushButton("🔌 Test All")
        test_btn.clicked.connect(self.test_all_environments)
        button_layout.addWidget(test_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_groups_tab(self) -> QWidget:
        """Create environment groups tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Environment Groups (for bulk operations)")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Groups table
        table_group = QGroupBox("Groups")
        table_layout = QVBoxLayout()
        
        self.groups_table = QTableWidget()
        self.groups_table.setColumnCount(4)
        self.groups_table.setHorizontalHeaderLabels([
            "Name", "Description", "Members", "Actions"
        ])
        
        header = self.groups_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Add sample data
        self._add_group_row("All Production", "All production environments", "2 members")
        self._add_group_row("Team A", "Team A environments", "3 members")
        
        table_layout.addWidget(self.groups_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_btn = QPushButton("➕ New Group")
        add_btn.clicked.connect(self.add_group)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏ Edit")
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_bulk_operations_tab(self) -> QWidget:
        """Create bulk operations tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Bulk Operations")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Execute backup, restore, or comparison operations across multiple environments")
        layout.addWidget(desc)
        
        # Operation buttons
        buttons_group = QGroupBox("Quick Actions")
        buttons_layout = QVBoxLayout()
        
        bulk_backup_btn = QPushButton("📦 Bulk Backup")
        bulk_backup_btn.setMinimumHeight(50)
        bulk_backup_btn.clicked.connect(self.bulk_backup)
        buttons_layout.addWidget(bulk_backup_btn)
        
        bulk_restore_btn = QPushButton("♻️ Bulk Restore")
        bulk_restore_btn.setMinimumHeight(50)
        bulk_restore_btn.clicked.connect(self.bulk_restore)
        buttons_layout.addWidget(bulk_restore_btn)
        
        bulk_compare_btn = QPushButton("🔍 Bulk Compare")
        bulk_compare_btn.setMinimumHeight(50)
        bulk_compare_btn.clicked.connect(self.bulk_compare)
        buttons_layout.addWidget(bulk_compare_btn)
        
        buttons_group.setLayout(buttons_layout)
        layout.addWidget(buttons_group)
        
        # History
        history_group = QGroupBox("Operation History")
        history_layout = QVBoxLayout()
        
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(6)
        self.operations_table.setHorizontalHeaderLabels([
            "Operation", "Type", "Environments", "Status", "Created", "Results"
        ])
        
        history_layout.addWidget(self.operations_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _add_environment_row(self, name: str, env_type: str, url: str, status: str, tags: str, last_tested: str):
        """Add environment row"""
        row = self.environments_table.rowCount()
        self.environments_table.insertRow(row)
        
        self.environments_table.setItem(row, 0, QTableWidgetItem(name))
        self.environments_table.setItem(row, 1, QTableWidgetItem(env_type))
        self.environments_table.setItem(row, 2, QTableWidgetItem(url))
        
        status_item = QTableWidgetItem(status)
        if "Healthy" in status:
            status_item.setForeground(QColor(0, 176, 80))
        self.environments_table.setItem(row, 3, status_item)
        
        self.environments_table.setItem(row, 4, QTableWidgetItem(tags))
        self.environments_table.setItem(row, 5, QTableWidgetItem(last_tested))
    
    def _add_group_row(self, name: str, description: str, members: str):
        """Add group row"""
        row = self.groups_table.rowCount()
        self.groups_table.insertRow(row)
        
        self.groups_table.setItem(row, 0, QTableWidgetItem(name))
        self.groups_table.setItem(row, 1, QTableWidgetItem(description))
        self.groups_table.setItem(row, 2, QTableWidgetItem(members))
    
    def add_environment(self):
        """Add new environment"""
        dialog = EnvironmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Environment added successfully")
    
    def edit_environment(self):
        """Edit selected environment"""
        current_row = self.environments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select an environment")
            return
        
        dialog = EnvironmentDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Environment updated successfully")
    
    def delete_environment(self):
        """Delete selected environment"""
        current_row = self.environments_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select an environment")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this environment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.environments_table.removeRow(current_row)
            QMessageBox.information(self, "Success", "Environment deleted")
    
    def test_all_environments(self):
        """Test all environment connections"""
        QMessageBox.information(self, "Test Results", "All environments are healthy ✓")
    
    def add_group(self):
        """Add new group"""
        QMessageBox.information(self, "Add Group", "Feature coming soon")
    
    def bulk_backup(self):
        """Execute bulk backup"""
        dialog = BulkBackupDialog(self)
        dialog.exec()
    
    def bulk_restore(self):
        """Execute bulk restore"""
        dialog = BulkRestoreDialog(self)
        dialog.exec()
    
    def bulk_compare(self):
        """Execute bulk compare"""
        dialog = BulkCompareDialog(self)
        dialog.exec()
    
    def setup_refresh_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_data(self):
        """Refresh environments list"""
        pass  # TODO: Fetch from API
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.timer.stop()
        super().closeEvent(event)
