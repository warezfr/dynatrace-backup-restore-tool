"""Environments management window"""
import os
from datetime import datetime
import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QDialog, QLineEdit, QCheckBox, QMessageBox,
    QHeaderView, QGroupBox, QComboBox, QListWidget, QListWidgetItem,
    QTabWidget, QTextEdit, QSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from .bulk_operations import BulkBackupDialog, BulkRestoreDialog, BulkCompareDialog

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")


class EnvironmentDialog(QDialog):
    def __init__(self, parent=None, environment=None, api_base: str = API_BASE_URL):
        super().__init__(parent)
        self.environment = environment
        self.api_base = api_base
        self.result_data = None
        self.init_ui()


class GroupDialog(QDialog):
    def __init__(self, parent=None, group=None):
        super().__init__(parent)
        self.group = group
        self.result_data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title_text = "Edit Group" if self.group else "New Group"
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        layout.addWidget(self.desc_input)

        layout.addWidget(QLabel("Environment IDs (comma-separated):"))
        self.env_ids_input = QLineEdit()
        self.env_ids_input.setPlaceholderText("1, 2, 3")
        layout.addWidget(self.env_ids_input)

        if self.group:
            self.name_input.setText(self.group.get("name", ""))
            self.desc_input.setText(self.group.get("description", ""))
            env_ids = self.group.get("environment_ids") or []
            self.env_ids_input.setText(", ".join(str(i) for i in env_ids))

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        save_btn = QPushButton("✓ Save")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        cancel_btn = QPushButton("✕ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setGeometry(150, 150, 420, 260)

    def save(self):
        name = self.name_input.text().strip()
        env_ids_text = self.env_ids_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required")
            return
        env_ids = []
        if env_ids_text:
            try:
                env_ids = [int(x.strip()) for x in env_ids_text.split(",") if x.strip()]
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Environment IDs must be integers separated by commas")
                return
        self.result_data = {
            "name": name,
            "description": self.desc_input.text().strip() or None,
            "environment_ids": env_ids,
        }
        self.accept()
    
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

        # Deployment type (Managed / SaaS)
        layout.addWidget(QLabel("Deployment Type:"))
        self.deployment_combo = QComboBox()
        self.deployment_combo.addItems(["Managed", "SaaS"])
        self.deployment_combo.currentTextChanged.connect(self._update_url_placeholder)
        layout.addWidget(self.deployment_combo)
        
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

        # Prefill if editing
        if self.environment:
            self.name_input.setText(self.environment.get("name", ""))
            env_type = self.environment.get("env_type", "production")
            idx = self.type_combo.findText(env_type.capitalize())
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
            self.url_input.setText(self.environment.get("environment_url", ""))
            self.token_input.setText(self.environment.get("api_token", ""))
            tags = self.environment.get("tags") or []
            self.tags_input.setText(", ".join(tags))
            self.insecure_check.setChecked(bool(self.environment.get("insecure_ssl")))
            if "saas" in [t.lower() for t in tags]:
                self.deployment_combo.setCurrentText("SaaS")
            else:
                self.deployment_combo.setCurrentText("Managed")
        else:
            self._update_url_placeholder("Managed")
        
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
        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        deployment_tag = "saas" if self.deployment_combo.currentText().lower() == "saas" else "managed"
        if deployment_tag not in [t.lower() for t in tags]:
            tags.append(deployment_tag)
        self.result_data = {
            "name": self.name_input.text().strip(),
            "description": None,
            "environment_url": self.url_input.text().strip(),
            "api_token": self.token_input.text().strip(),
            "env_type": self.type_combo.currentText().lower(),
            "insecure_ssl": self.insecure_check.isChecked(),
            "tags": tags,
        }
        self.accept()
    
    def test_connection(self):
        """Test the connection"""
        if not self.environment or not self.environment.get("id"):
            QMessageBox.information(self, "Test Connection", "Save the environment first, then test.")
            return
        
        env_id = self.environment["id"]
        try:
            resp = requests.post(f"{self.api_base}/environments/{env_id}/test", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = "Healthy" if data.get("is_healthy") else "Unhealthy"
                QMessageBox.information(self, "Test Connection", f"{status}: {data.get('message', '')}")
            else:
                QMessageBox.warning(self, "Test Failed", f"HTTP {resp.status_code}: {resp.text}")
        except Exception as exc:
            QMessageBox.critical(self, "Test Error", f"Failed to test connection: {exc}")

class EnvironmentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.api_base = API_BASE_URL
        self.environments_cache = {}
        self.groups_cache = {}
        self.init_ui()
        self.setup_refresh_timer()
        self.refresh_data()
    
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
        self.environments_table.setColumnCount(6)
        self.environments_table.setHorizontalHeaderLabels([
            "Name", "Type", "URL", "Status", "Tags", "Last Tested"
        ])
        
        header = self.environments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

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
        edit_btn.clicked.connect(self.edit_group)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_group)
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
    
    def _add_environment_row(self, env: dict):
        """Add environment row from API payload"""
        row = self.environments_table.rowCount()
        self.environments_table.insertRow(row)

        name_item = QTableWidgetItem(env.get("name", ""))
        name_item.setData(Qt.ItemDataRole.UserRole, env.get("id"))
        self.environments_table.setItem(row, 0, name_item)

        self.environments_table.setItem(row, 1, QTableWidgetItem(env.get("env_type", "")))
        self.environments_table.setItem(row, 2, QTableWidgetItem(env.get("environment_url", "")))

        status_label = "Healthy" if env.get("is_healthy") else "Unhealthy"
        status_item = QTableWidgetItem(status_label)
        status_item.setForeground(QColor(0, 176, 80) if env.get("is_healthy") else QColor(200, 0, 0))
        self.environments_table.setItem(row, 3, status_item)

        tags = env.get("tags") or []
        self.environments_table.setItem(row, 4, QTableWidgetItem(", ".join(tags)))
        self.environments_table.setItem(row, 5, QTableWidgetItem(self._format_last_tested(env.get("last_tested_at"))))
    
    def _add_group_row(self, name: str, description: str, members: str):
        """Add group row"""
        row = self.groups_table.rowCount()
        self.groups_table.insertRow(row)
        
        item = QTableWidgetItem(name)
        self.groups_table.setItem(row, 0, item)
        self.groups_table.setItem(row, 1, QTableWidgetItem(description))
        self.groups_table.setItem(row, 2, QTableWidgetItem(members))
    
    def add_environment(self):
        """Add new environment"""
        dialog = EnvironmentDialog(self, api_base=self.api_base)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                resp = requests.post(
                    f"{self.api_base}/environments",
                    json=dialog.result_data,
                    timeout=10,
                )
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Environment added successfully")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add environment: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def edit_environment(self):
        """Edit selected environment"""
        env_id = self._get_selected_env_id()
        if env_id is None:
            QMessageBox.warning(self, "Error", "Please select an environment")
            return

        current_env = self.environments_cache.get(env_id, {})
        dialog = EnvironmentDialog(self, environment=current_env, api_base=self.api_base)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                resp = requests.put(
                    f"{self.api_base}/environments/{env_id}",
                    json=dialog.result_data,
                    timeout=10,
                )
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Environment updated successfully")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update environment: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def delete_environment(self):
        """Delete selected environment"""
        env_id = self._get_selected_env_id()
        if env_id is None:
            QMessageBox.warning(self, "Error", "Please select an environment")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this environment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                resp = requests.delete(f"{self.api_base}/environments/{env_id}", timeout=10)
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Environment deleted")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete environment: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def test_all_environments(self):
        """Test all environment connections"""
        if not self.environments_cache:
            QMessageBox.information(self, "Test Results", "No environments to test.")
            return
        results = []
        for env_id, env in self.environments_cache.items():
            try:
                resp = requests.post(f"{self.api_base}/environments/{env_id}/test", timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    status = "Healthy" if data.get("is_healthy") else "Unhealthy"
                    results.append(f"{env.get('name')}: {status}")
                else:
                    results.append(f"{env.get('name')}: HTTP {resp.status_code}")
            except Exception as exc:
                results.append(f"{env.get('name')}: Error {exc}")
        QMessageBox.information(self, "Test Results", "\n".join(results))
    
    def add_group(self):
        """Add new group"""
        dialog = GroupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                resp = requests.post(
                    f"{self.api_base}/environments/groups/",
                    json=dialog.result_data,
                    timeout=10,
                )
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Group created")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to create group: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def edit_group(self):
        """Edit selected group"""
        group_id = self._get_selected_group_id()
        if group_id is None:
            QMessageBox.warning(self, "Error", "Please select a group")
            return
        current_group = self.groups_cache.get(group_id, {})
        dialog = GroupDialog(self, group=current_group)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                resp = requests.put(
                    f"{self.api_base}/environments/groups/{group_id}",
                    json=dialog.result_data,
                    timeout=10,
                )
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Group updated")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update group: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def delete_group(self):
        """Delete selected group"""
        group_id = self._get_selected_group_id()
        if group_id is None:
            QMessageBox.warning(self, "Error", "Please select a group")
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Delete this group?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                resp = requests.delete(f"{self.api_base}/environments/groups/{group_id}", timeout=10)
                if resp.status_code == 200:
                    QMessageBox.information(self, "Success", "Group deleted")
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete group: {resp.text}")
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
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
        try:
            resp = requests.get(f"{self.api_base}/environments", timeout=10)
            if resp.status_code != 200:
                QMessageBox.warning(self, "Error", f"Failed to fetch environments: {resp.text}")
                return
            envs = resp.json()
            self.environments_cache = {env["id"]: env for env in envs}
            self.environments_table.setRowCount(0)
            for env in envs:
                self._add_environment_row(env)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Request failed: {exc}")
        
        # Groups
        try:
            resp = requests.get(f"{self.api_base}/environments/groups/", timeout=10)
            if resp.status_code == 200:
                groups = resp.json()
                self.groups_cache = {g["id"]: g for g in groups}
                self.groups_table.setRowCount(0)
                for g in groups:
                    members = g.get("environment_ids") or []
                    row = self.groups_table.rowCount()
                    self.groups_table.insertRow(row)
                    name_item = QTableWidgetItem(g.get("name", ""))
                    name_item.setData(Qt.ItemDataRole.UserRole, g.get("id"))
                    self.groups_table.setItem(row, 0, name_item)
                    self.groups_table.setItem(row, 1, QTableWidgetItem(g.get("description") or ""))
                    self.groups_table.setItem(row, 2, QTableWidgetItem(f"{len(members)} members"))
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch groups: {resp.text}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Request failed: {exc}")
        
        # Bulk operations history
        try:
            resp = requests.get(f"{self.api_base}/environments/bulk/", timeout=10)
            if resp.status_code == 200:
                ops = resp.json()
                self.operations_table.setRowCount(0)
                for op in ops:
                    row = self.operations_table.rowCount()
                    self.operations_table.insertRow(row)
                    self.operations_table.setItem(row, 0, QTableWidgetItem(op.get("name", "")))
                    self.operations_table.setItem(row, 1, QTableWidgetItem(op.get("operation_type", "")))
                    self.operations_table.setItem(row, 2, QTableWidgetItem(str(op.get("total_environments", 0))))
                    status_item = QTableWidgetItem(op.get("status", ""))
                    if op.get("status") in ("success", "completed", "in_progress", "pending"):
                        status_item.setForeground(QColor(0, 176, 80))
                    elif op.get("status") in ("failed", "error"):
                        status_item.setForeground(QColor(200, 0, 0))
                    self.operations_table.setItem(row, 3, status_item)
                    self.operations_table.setItem(row, 4, QTableWidgetItem(self._format_last_tested(op.get("created_at"))))
                    summary = op.get("results_summary") or {}
                    self.operations_table.setItem(row, 5, QTableWidgetItem(str(summary)))
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch bulk operations: {resp.text}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Request failed: {exc}")
    
    def _get_selected_env_id(self):
        """Return selected environment id or None"""
        current_row = self.environments_table.currentRow()
        if current_row < 0:
            return None
        item = self.environments_table.item(current_row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None
    
    def _get_selected_group_id(self):
        """Return selected group id or None"""
        current_row = self.groups_table.currentRow()
        if current_row < 0:
            return None
        item = self.groups_table.item(current_row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _format_last_tested(self, last_tested):
        """Format timestamp from API"""
        if not last_tested:
            return "-"
        try:
            # FastAPI returns ISO string
            dt = datetime.fromisoformat(last_tested.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(last_tested)
    
    def _update_url_placeholder(self, deployment: str):
        """Adjust URL placeholder depending on deployment type"""
        if deployment.lower() == "saas":
            self.url_input.setPlaceholderText("https://abc12345.live.dynatrace.com")
        else:
            self.url_input.setPlaceholderText("https://dynatrace.example.com/e/12345678")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.timer.stop()
        super().closeEvent(event)
