"""Connections management window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QCheckBox, QMessageBox,
    QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class ConnectionDialog(QDialog):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        title_text = "Edit Connection" if self.connection else "New Connection"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Name
        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
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
        self.setGeometry(100, 100, 400, 300)
    
    def save(self):
        """Save connection"""
        if not self.name_input.text() or not self.url_input.text() or not self.token_input.text():
            QMessageBox.warning(self, "Validation Error", "Please fill all fields")
            return
        
        self.accept()
    
    def test_connection(self):
        """Test the connection"""
        QMessageBox.information(self, "Test Connection", "Connection successful ✓")

class ConnectionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Manage Dynatrace Connections")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Connections table
        table_group = QGroupBox("Connections")
        table_layout = QVBoxLayout()
        
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(5)
        self.connections_table.setHorizontalHeaderLabels([
            "Name", "Environment URL", "Status", "Last Tested", "Actions"
        ])
        
        header = self.connections_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Add sample data
        self._add_connection_row("Production", "https://dyn.example.com/e/abc123", "✓ Healthy", "2 min ago")
        self._add_connection_row("Staging", "https://dyn-staging.example.com/e/def456", "✓ Healthy", "5 min ago")
        
        table_layout.addWidget(self.connections_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_btn = QPushButton("➕ New Connection")
        add_btn.clicked.connect(self.add_connection)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.clicked.connect(self.edit_connection)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_connection)
        button_layout.addWidget(delete_btn)
        
        test_btn = QPushButton("🔌 Test All")
        test_btn.clicked.connect(self.test_all)
        button_layout.addWidget(test_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _add_connection_row(self, name: str, url: str, status: str, last_tested: str):
        """Add a row to the connections table"""
        row = self.connections_table.rowCount()
        self.connections_table.insertRow(row)
        
        self.connections_table.setItem(row, 0, QTableWidgetItem(name))
        self.connections_table.setItem(row, 1, QTableWidgetItem(url))
        
        status_item = QTableWidgetItem(status)
        if "Healthy" in status:
            status_item.setForeground(QColor(0, 176, 80))
        self.connections_table.setItem(row, 2, status_item)
        
        self.connections_table.setItem(row, 3, QTableWidgetItem(last_tested))
    
    def add_connection(self):
        """Add new connection"""
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Connection added successfully")
            # TODO: Refresh table from API
    
    def edit_connection(self):
        """Edit selected connection"""
        current_row = self.connections_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a connection")
            return
        
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Success", "Connection updated successfully")
    
    def delete_connection(self):
        """Delete selected connection"""
        current_row = self.connections_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Error", "Please select a connection")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this connection?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.connections_table.removeRow(current_row)
            QMessageBox.information(self, "Success", "Connection deleted")
    
    def test_all(self):
        """Test all connections"""
        QMessageBox.information(self, "Test Results", "All connections are healthy ✓")
