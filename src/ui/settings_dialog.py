#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Settings dialog for configuring the application
"""

import os
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QComboBox, QSpinBox, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QLineEdit, QFileDialog,
    QGroupBox, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QIcon

from src.utils.helpers import get_system_paths

logger = logging.getLogger("StorageStats.SettingsDialog")

class SettingsDialog(QDialog):
    """Dialog for configuring application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        
        # Create settings object
        self.settings = QSettings("StorageStats", "StorageStats")
        
        # Set up the UI
        self._setup_ui()
        
        # Load settings
        self._load_settings()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create general settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Scan settings group
        scan_group = QGroupBox("Scan Settings")
        scan_layout = QFormLayout(scan_group)
        
        # Thread count for parallel scanning
        self.thread_spin = QSpinBox()
        self.thread_spin.setMinimum(1)
        self.thread_spin.setMaximum(32)
        self.thread_spin.setValue(4)
        scan_layout.addRow("Max Threads:", self.thread_spin)
        
        # Calculate hashes for duplicate detection
        self.calc_hash_check = QCheckBox("Calculate file hashes for duplicate detection")
        self.calc_hash_check.setChecked(True)
        scan_layout.addRow("", self.calc_hash_check)
        
        # Hash method
        self.hash_method_combo = QComboBox()
        self.hash_method_combo.addItems(["Quick (faster, less accurate)", "Full (slower, more accurate)"])
        scan_layout.addRow("Hash Method:", self.hash_method_combo)
        
        # Skip hidden files
        self.skip_hidden_check = QCheckBox("Skip hidden files and directories")
        self.skip_hidden_check.setChecked(True)
        scan_layout.addRow("", self.skip_hidden_check)
        
        # Follow symlinks
        self.follow_symlinks_check = QCheckBox("Follow symbolic links (may cause duplicates)")
        self.follow_symlinks_check.setChecked(False)
        scan_layout.addRow("", self.follow_symlinks_check)
        
        general_layout.addWidget(scan_group)
        
        # UI settings group
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)
        
        # Default sort order
        self.default_sort_combo = QComboBox()
        self.default_sort_combo.addItems(["Size (largest first)", "Name", "Last Modified"])
        ui_layout.addRow("Default Sort:", self.default_sort_combo)
        
        # Show file sizes in binary units
        self.binary_units_check = QCheckBox("Show file sizes in binary units (KiB, MiB, GiB)")
        self.binary_units_check.setChecked(True)
        ui_layout.addRow("", self.binary_units_check)
        
        general_layout.addWidget(ui_group)
        
        # Add general tab
        tab_widget.addTab(general_tab, "General")
        
        # Create exclusions tab
        exclusions_tab = QWidget()
        exclusions_layout = QVBoxLayout(exclusions_tab)
        
        # Explanation label
        exclusions_label = QLabel(
            "Excluded paths will be skipped during scanning. This can speed up scans and avoid "
            "accessing system directories that don't need to be analyzed."
        )
        exclusions_label.setWordWrap(True)
        exclusions_layout.addWidget(exclusions_label)
        
        # Exclusion list
        self.exclusion_list = QListWidget()
        exclusions_layout.addWidget(self.exclusion_list)
        
        # Buttons for managing exclusions
        exclusion_buttons_layout = QHBoxLayout()
        
        self.add_exclusion_button = QPushButton("Add")
        self.add_exclusion_button.clicked.connect(self._add_exclusion)
        
        self.remove_exclusion_button = QPushButton("Remove")
        self.remove_exclusion_button.clicked.connect(self._remove_exclusion)
        
        self.add_common_button = QPushButton("Add Common System Paths")
        self.add_common_button.clicked.connect(self._add_common_exclusions)
        
        exclusion_buttons_layout.addWidget(self.add_exclusion_button)
        exclusion_buttons_layout.addWidget(self.remove_exclusion_button)
        exclusion_buttons_layout.addStretch()
        exclusion_buttons_layout.addWidget(self.add_common_button)
        
        exclusions_layout.addLayout(exclusion_buttons_layout)
        
        # Add exclusions tab
        tab_widget.addTab(exclusions_tab, "Exclusions")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Add dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def _load_settings(self):
        """Load settings into the UI"""
        # Load general settings
        self.thread_spin.setValue(self.settings.value("max_threads", 4, int))
        self.calc_hash_check.setChecked(self.settings.value("calculate_hashes", True, bool))
        self.hash_method_combo.setCurrentIndex(0 if self.settings.value("hash_method", "quick") == "quick" else 1)
        self.skip_hidden_check.setChecked(self.settings.value("skip_hidden", True, bool))
        self.follow_symlinks_check.setChecked(self.settings.value("follow_symlinks", False, bool))
        
        # Load UI settings
        sort_order = self.settings.value("default_sort", "size")
        if sort_order == "size":
            self.default_sort_combo.setCurrentIndex(0)
        elif sort_order == "name":
            self.default_sort_combo.setCurrentIndex(1)
        elif sort_order == "modified":
            self.default_sort_combo.setCurrentIndex(2)
        
        self.binary_units_check.setChecked(self.settings.value("binary_units", True, bool))
        
        # Load exclusions
        exclusions = self.settings.value("excluded_paths", [])
        if exclusions:
            for path in exclusions:
                self.exclusion_list.addItem(path)
    
    def _save_settings(self):
        """Save settings from the UI"""
        # Save general settings
        self.settings.setValue("max_threads", self.thread_spin.value())
        self.settings.setValue("calculate_hashes", self.calc_hash_check.isChecked())
        self.settings.setValue("hash_method", "quick" if self.hash_method_combo.currentIndex() == 0 else "full")
        self.settings.setValue("skip_hidden", self.skip_hidden_check.isChecked())
        self.settings.setValue("follow_symlinks", self.follow_symlinks_check.isChecked())
        
        # Save UI settings
        sort_order_index = self.default_sort_combo.currentIndex()
        if sort_order_index == 0:
            self.settings.setValue("default_sort", "size")
        elif sort_order_index == 1:
            self.settings.setValue("default_sort", "name")
        else:
            self.settings.setValue("default_sort", "modified")
        
        self.settings.setValue("binary_units", self.binary_units_check.isChecked())
        
        # Save exclusions
        exclusions = []
        for i in range(self.exclusion_list.count()):
            exclusions.append(self.exclusion_list.item(i).text())
        self.settings.setValue("excluded_paths", exclusions)
        
        self.accept()
    
    def _add_exclusion(self):
        """Add a directory to the exclusion list"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Exclude",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            # Check if already in the list
            for i in range(self.exclusion_list.count()):
                if self.exclusion_list.item(i).text() == directory:
                    return
            
            # Add to list
            self.exclusion_list.addItem(directory)
    
    def _remove_exclusion(self):
        """Remove selected directory from the exclusion list"""
        selected_items = self.exclusion_list.selectedItems()
        for item in selected_items:
            self.exclusion_list.takeItem(self.exclusion_list.row(item))
    
    def _add_common_exclusions(self):
        """Add common system paths to the exclusion list"""
        system_paths = get_system_paths()
        
        for path in system_paths:
            # Check if already in the list
            already_exists = False
            for i in range(self.exclusion_list.count()):
                if self.exclusion_list.item(i).text() == path:
                    already_exists = True
                    break
            
            # Add to list if not already there
            if not already_exists:
                self.exclusion_list.addItem(path) 