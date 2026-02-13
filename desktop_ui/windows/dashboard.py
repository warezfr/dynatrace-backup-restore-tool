"""Dashboard window"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_refresh_timer()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header
        header = self._create_header()
        layout.addLayout(header)
        
        # Stats section
        stats = self._create_stats()
        layout.addLayout(stats)
        
        # Recent backups table
        table_group = QGroupBox("Recent Backups")
        table_layout = QVBoxLayout()
        self.backups_table = self._create_table()
        table_layout.addWidget(self.backups_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # Recent restores table
        restore_group = QGroupBox("Recent Restores")
        restore_layout = QVBoxLayout()
        self.restore_table = self._create_table()
        restore_layout.addWidget(self.restore_table)
        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)
        
        self.setLayout(layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Create header section"""
        layout = QHBoxLayout()
        
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        return layout
    
    def _create_stats(self) -> QHBoxLayout:
        """Create statistics section"""
        layout = QHBoxLayout()
        
        stats = [
            ("Total Backups", "12", QColor(0, 120, 215)),
            ("Successful", "11", QColor(0, 176, 80)),
            ("Failed", "1", QColor(255, 0, 0)),
            ("Total Size", "24.5 GB", QColor(150, 82, 223)),
        ]
        
        for label, value, color in stats:
            stat_widget = self._create_stat_card(label, value, color)
            layout.addWidget(stat_widget)
        
        return layout
    
    def _create_stat_card(self, label: str, value: str, color: QColor) -> QWidget:
        """Create a single stat card"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Segoe UI", 9))
        label_widget.setStyleSheet(f"color: {color.name()};")
        layout.addWidget(label_widget)
        
        # Value
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(value_widget)
        
        widget.setLayout(layout)
        widget.setStyleSheet(f"border: 1px solid {color.name()}; border-radius: 5px;")
        
        return widget
    
    def _create_table(self) -> QTableWidget:
        """Create a table widget"""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Name", "Type", "Date", "Status", "Size", "Files"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        return table
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # TODO: Fetch data from API
        pass
    
    def setup_refresh_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # Refresh every 30 seconds
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.timer.stop()
        super().closeEvent(event)
