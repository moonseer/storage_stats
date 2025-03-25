#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Filter dialog for customizing file filters
"""

import logging
import os
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QCheckBox, QComboBox, QGroupBox, QRadioButton,
    QSpinBox, QDateEdit, QTabWidget, QListWidget, QListWidgetItem,
    QGridLayout, QFileDialog, QDialogButtonBox, QWidget
)
from PyQt6.QtCore import Qt, QDate

logger = logging.getLogger("StorageStats.FilterDialog")

class FilterDialog(QDialog):
    """Dialog for configuring file filters"""
    
    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Filters")
        self.setMinimumSize(600, 500)
        
        # Initialize with current filters if provided
        self.current_filters = current_filters or {}
        
        # Create the UI
        self._create_ui()
        
        # Load current filters
        self._load_current_filters()
    
    def _create_ui(self):
        """Create the dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Create tabs
        self._create_basic_filters_tab(tab_widget)
        self._create_file_type_tab(tab_widget)
        self._create_date_size_tab(tab_widget)
        self._create_advanced_tab(tab_widget)
        
        layout.addWidget(tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self._reset_filters)
        layout.addWidget(button_box)
    
    def _create_basic_filters_tab(self, tab_widget):
        """Create the basic filters tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Name filter group
        name_group = QGroupBox("Name Filters")
        name_layout = QVBoxLayout()
        
        # Contains text
        contains_layout = QHBoxLayout()
        contains_layout.addWidget(QLabel("Contains text:"))
        self.contains_edit = QLineEdit()
        contains_layout.addWidget(self.contains_edit)
        name_layout.addLayout(contains_layout)
        
        # Does not contain text
        not_contains_layout = QHBoxLayout()
        not_contains_layout.addWidget(QLabel("Does not contain:"))
        self.not_contains_edit = QLineEdit()
        not_contains_layout.addWidget(self.not_contains_edit)
        name_layout.addLayout(not_contains_layout)
        
        # Extensions filter
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("Extension filter:"))
        self.extension_edit = QLineEdit()
        self.extension_edit.setPlaceholderText("e.g. jpg,png,mp4 or !exe,dll")
        ext_layout.addWidget(self.extension_edit)
        name_layout.addLayout(ext_layout)
        
        name_group.setLayout(name_layout)
        layout.addWidget(name_group)
        
        # Path filter group
        path_group = QGroupBox("Path Filters")
        path_layout = QVBoxLayout()
        
        # Path includes
        path_includes_layout = QHBoxLayout()
        path_includes_layout.addWidget(QLabel("Path includes:"))
        self.path_includes_edit = QLineEdit()
        path_includes_layout.addWidget(self.path_includes_edit)
        path_layout.addLayout(path_includes_layout)
        
        # Path excludes
        path_excludes_layout = QHBoxLayout()
        path_excludes_layout.addWidget(QLabel("Path excludes:"))
        self.path_excludes_edit = QLineEdit()
        path_excludes_layout.addWidget(self.path_excludes_edit)
        path_layout.addLayout(path_excludes_layout)
        
        # Special filters
        special_layout = QGridLayout()
        
        self.hidden_files_check = QCheckBox("Include hidden files")
        special_layout.addWidget(self.hidden_files_check, 0, 0)
        
        self.system_files_check = QCheckBox("Include system files")
        special_layout.addWidget(self.system_files_check, 0, 1)
        
        self.symlinks_check = QCheckBox("Follow symbolic links")
        special_layout.addWidget(self.symlinks_check, 1, 0)
        
        self.temp_files_check = QCheckBox("Include temporary files")
        special_layout.addWidget(self.temp_files_check, 1, 1)
        
        path_layout.addLayout(special_layout)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Add some stretch at the end
        layout.addStretch()
        
        tab_widget.addTab(tab, "Basic Filters")
    
    def _create_file_type_tab(self, tab_widget):
        """Create the file type filters tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File type selection
        type_group = QGroupBox("File Types")
        type_layout = QVBoxLayout()
        
        # File type filter mode
        filter_mode_layout = QHBoxLayout()
        self.include_types_radio = QRadioButton("Include selected types")
        self.exclude_types_radio = QRadioButton("Exclude selected types")
        self.include_types_radio.setChecked(True)
        
        filter_mode_layout.addWidget(self.include_types_radio)
        filter_mode_layout.addWidget(self.exclude_types_radio)
        type_layout.addLayout(filter_mode_layout)
        
        # File type grid with checkboxes
        type_grid = QGridLayout()
        
        # Define common file types
        file_types = [
            ("Documents", ["doc", "docx", "pdf", "txt", "rtf", "odt"]),
            ("Images", ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"]),
            ("Audio", ["mp3", "wav", "ogg", "flac", "aac", "m4a"]),
            ("Video", ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"]),
            ("Archives", ["zip", "rar", "7z", "tar", "gz", "bz2"]),
            ("Code", ["py", "js", "html", "css", "java", "cpp", "c", "h"]),
            ("Data", ["csv", "json", "xml", "sql", "db", "xlsx"]),
            ("Executables", ["exe", "msi", "app", "dmg", "apk"]),
            ("System", ["dll", "sys", "so", "dylib", "bin"])
        ]
        
        self.file_type_checks = {}
        
        for i, (type_name, _) in enumerate(file_types):
            row, col = divmod(i, 3)
            check = QCheckBox(type_name)
            type_grid.addWidget(check, row, col)
            self.file_type_checks[type_name] = check
        
        type_layout.addLayout(type_grid)
        
        # Custom file type
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom file type:"))
        self.custom_type_edit = QLineEdit()
        self.custom_type_edit.setPlaceholderText("e.g. swift,rb,php")
        custom_layout.addWidget(self.custom_type_edit)
        type_layout.addLayout(custom_layout)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Add some stretch at the end
        layout.addStretch()
        
        tab_widget.addTab(tab, "File Types")
    
    def _create_date_size_tab(self, tab_widget):
        """Create the date and size filters tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Size filter group
        size_group = QGroupBox("Size Filters")
        size_layout = QGridLayout()
        
        # Minimum size
        size_layout.addWidget(QLabel("Minimum size:"), 0, 0)
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000000)
        self.min_size_spin.setValue(0)
        size_layout.addWidget(self.min_size_spin, 0, 1)
        
        self.min_size_unit = QComboBox()
        self.min_size_unit.addItems(["Bytes", "KB", "MB", "GB"])
        self.min_size_unit.setCurrentIndex(1)  # Default to KB
        size_layout.addWidget(self.min_size_unit, 0, 2)
        
        # Maximum size
        size_layout.addWidget(QLabel("Maximum size:"), 1, 0)
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 1000000)
        self.max_size_spin.setValue(0)
        self.max_size_spin.setSpecialValueText("No limit")
        size_layout.addWidget(self.max_size_spin, 1, 1)
        
        self.max_size_unit = QComboBox()
        self.max_size_unit.addItems(["Bytes", "KB", "MB", "GB"])
        self.max_size_unit.setCurrentIndex(3)  # Default to GB
        size_layout.addWidget(self.max_size_unit, 1, 2)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Date filter group
        date_group = QGroupBox("Date Filters")
        date_layout = QVBoxLayout()
        
        # Date filter type
        date_type_layout = QHBoxLayout()
        date_type_layout.addWidget(QLabel("Filter by:"))
        self.date_type_combo = QComboBox()
        self.date_type_combo.addItems(["Modified", "Created", "Accessed"])
        date_type_layout.addWidget(self.date_type_combo)
        date_layout.addLayout(date_type_layout)
        
        # Date range options
        range_layout = QGridLayout()
        
        # Quick date ranges
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems([
            "Any time", 
            "Today", 
            "Yesterday",
            "Last 7 days", 
            "Last 30 days", 
            "Last 90 days",
            "Last year",
            "Custom range"
        ])
        self.date_range_combo.currentIndexChanged.connect(self._on_date_range_changed)
        range_layout.addWidget(QLabel("Quick range:"), 0, 0)
        range_layout.addWidget(self.date_range_combo, 0, 1, 1, 2)
        
        # Custom date range
        range_layout.addWidget(QLabel("From:"), 1, 0)
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        range_layout.addWidget(self.date_from, 1, 1)
        
        range_layout.addWidget(QLabel("To:"), 2, 0)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        range_layout.addWidget(self.date_to, 2, 1)
        
        date_layout.addLayout(range_layout)
        
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Add some stretch at the end
        layout.addStretch()
        
        tab_widget.addTab(tab, "Size & Date")
    
    def _create_advanced_tab(self, tab_widget):
        """Create the advanced filters tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Save and load filters
        presets_group = QGroupBox("Filter Presets")
        presets_layout = QVBoxLayout()
        
        # Presets list
        self.presets_list = QListWidget()
        presets_layout.addWidget(self.presets_list)
        
        # Buttons for presets
        presets_buttons = QHBoxLayout()
        
        save_preset_btn = QPushButton("Save Current")
        save_preset_btn.clicked.connect(self._save_preset)
        presets_buttons.addWidget(save_preset_btn)
        
        load_preset_btn = QPushButton("Load Selected")
        load_preset_btn.clicked.connect(self._load_preset)
        presets_buttons.addWidget(load_preset_btn)
        
        delete_preset_btn = QPushButton("Delete Selected")
        delete_preset_btn.clicked.connect(self._delete_preset)
        presets_buttons.addWidget(delete_preset_btn)
        
        presets_layout.addLayout(presets_buttons)
        presets_group.setLayout(presets_layout)
        layout.addWidget(presets_group)
        
        # Regular expression filter
        regex_group = QGroupBox("Regular Expression Filter")
        regex_layout = QVBoxLayout()
        
        regex_help = QLabel("Use regular expressions for advanced pattern matching.")
        regex_help.setWordWrap(True)
        regex_layout.addWidget(regex_help)
        
        regex_name_layout = QHBoxLayout()
        regex_name_layout.addWidget(QLabel("Name pattern:"))
        self.regex_name_edit = QLineEdit()
        regex_name_layout.addWidget(self.regex_name_edit)
        regex_layout.addLayout(regex_name_layout)
        
        regex_path_layout = QHBoxLayout()
        regex_path_layout.addWidget(QLabel("Path pattern:"))
        self.regex_path_edit = QLineEdit()
        regex_path_layout.addWidget(self.regex_path_edit)
        regex_layout.addLayout(regex_path_layout)
        
        self.regex_case_sensitive = QCheckBox("Case sensitive")
        regex_layout.addWidget(self.regex_case_sensitive)
        
        regex_group.setLayout(regex_layout)
        layout.addWidget(regex_group)
        
        # Add some stretch at the end
        layout.addStretch()
        
        tab_widget.addTab(tab, "Advanced")
    
    def _on_date_range_changed(self, index):
        """Handle date range combo box changes"""
        today = QDate.currentDate()
        enable_custom = index == self.date_range_combo.count() - 1
        
        self.date_from.setEnabled(enable_custom)
        self.date_to.setEnabled(enable_custom)
        
        # Set appropriate date ranges based on selection
        if not enable_custom:
            if index == 1:  # Today
                self.date_from.setDate(today)
                self.date_to.setDate(today)
            elif index == 2:  # Yesterday
                yesterday = today.addDays(-1)
                self.date_from.setDate(yesterday)
                self.date_to.setDate(yesterday)
            elif index == 3:  # Last 7 days
                self.date_from.setDate(today.addDays(-7))
                self.date_to.setDate(today)
            elif index == 4:  # Last 30 days
                self.date_from.setDate(today.addDays(-30))
                self.date_to.setDate(today)
            elif index == 5:  # Last 90 days
                self.date_from.setDate(today.addDays(-90))
                self.date_to.setDate(today)
            elif index == 6:  # Last year
                self.date_from.setDate(today.addDays(-365))
                self.date_to.setDate(today)
    
    def _save_preset(self):
        """Save current filter settings as a preset"""
        # Get a name for the preset
        name, ok = QInputDialog.getText(
            self, 
            "Save Filter Preset", 
            "Enter a name for this filter preset:"
        )
        
        if not ok or not name:
            return
        
        # Get current filters
        filters = self.get_filters()
        
        # Add to presets list
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, filters)
        self.presets_list.addItem(item)
        
        # Save to settings
        self._save_presets_to_settings()
    
    def _load_preset(self):
        """Load the selected preset"""
        selected_items = self.presets_list.selectedItems()
        if not selected_items:
            return
        
        # Get filters from the selected item
        filters = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Apply filters to UI
        self._apply_filters(filters)
    
    def _delete_preset(self):
        """Delete the selected preset"""
        selected_items = self.presets_list.selectedItems()
        if not selected_items:
            return
        
        # Remove from list
        for item in selected_items:
            self.presets_list.takeItem(self.presets_list.row(item))
        
        # Save updated presets
        self._save_presets_to_settings()
    
    def _save_presets_to_settings(self):
        """Save all presets to settings"""
        # This would typically save to QSettings
        pass
    
    def _load_current_filters(self):
        """Load current filters into the UI"""
        if self.current_filters:
            self._apply_filters(self.current_filters)
    
    def _apply_filters(self, filters):
        """Apply filter settings to the UI"""
        # Basic filters
        self.contains_edit.setText(filters.get("contains", ""))
        self.not_contains_edit.setText(filters.get("not_contains", ""))
        self.extension_edit.setText(filters.get("extensions", ""))
        self.path_includes_edit.setText(filters.get("path_includes", ""))
        self.path_excludes_edit.setText(filters.get("path_excludes", ""))
        
        # Special filters
        self.hidden_files_check.setChecked(filters.get("include_hidden", False))
        self.system_files_check.setChecked(filters.get("include_system", False))
        self.symlinks_check.setChecked(filters.get("follow_symlinks", False))
        self.temp_files_check.setChecked(filters.get("include_temp", False))
        
        # File types
        file_types = filters.get("file_types", {})
        exclude_types = filters.get("exclude_types", False)
        
        self.include_types_radio.setChecked(not exclude_types)
        self.exclude_types_radio.setChecked(exclude_types)
        
        for type_name, check in self.file_type_checks.items():
            check.setChecked(type_name in file_types)
        
        self.custom_type_edit.setText(filters.get("custom_types", ""))
        
        # Size filters
        min_size = filters.get("min_size", 0)
        min_unit = filters.get("min_size_unit", 1)
        max_size = filters.get("max_size", 0)
        max_unit = filters.get("max_size_unit", 3)
        
        self.min_size_spin.setValue(min_size)
        self.min_size_unit.setCurrentIndex(min_unit)
        self.max_size_spin.setValue(max_size)
        self.max_size_unit.setCurrentIndex(max_unit)
        
        # Date filters
        date_type = filters.get("date_type", 0)
        date_range = filters.get("date_range", 0)
        
        self.date_type_combo.setCurrentIndex(date_type)
        self.date_range_combo.setCurrentIndex(date_range)
        
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        
        if from_date:
            self.date_from.setDate(QDate.fromString(from_date, Qt.DateFormat.ISODate))
        
        if to_date:
            self.date_to.setDate(QDate.fromString(to_date, Qt.DateFormat.ISODate))
        
        # Regex filters
        self.regex_name_edit.setText(filters.get("regex_name", ""))
        self.regex_path_edit.setText(filters.get("regex_path", ""))
        self.regex_case_sensitive.setChecked(filters.get("regex_case_sensitive", False))
    
    def _reset_filters(self):
        """Reset all filters to default values"""
        # Basic filters
        self.contains_edit.clear()
        self.not_contains_edit.clear()
        self.extension_edit.clear()
        self.path_includes_edit.clear()
        self.path_excludes_edit.clear()
        
        # Special filters
        self.hidden_files_check.setChecked(False)
        self.system_files_check.setChecked(False)
        self.symlinks_check.setChecked(False)
        self.temp_files_check.setChecked(False)
        
        # File types
        self.include_types_radio.setChecked(True)
        
        for check in self.file_type_checks.values():
            check.setChecked(False)
        
        self.custom_type_edit.clear()
        
        # Size filters
        self.min_size_spin.setValue(0)
        self.min_size_unit.setCurrentIndex(1)
        self.max_size_spin.setValue(0)
        self.max_size_unit.setCurrentIndex(3)
        
        # Date filters
        self.date_type_combo.setCurrentIndex(0)
        self.date_range_combo.setCurrentIndex(0)
        
        # Regex filters
        self.regex_name_edit.clear()
        self.regex_path_edit.clear()
        self.regex_case_sensitive.setChecked(False)
    
    def get_filters(self):
        """Get the current filter settings as a dictionary"""
        filters = {}
        
        # Basic filters
        filters["contains"] = self.contains_edit.text()
        filters["not_contains"] = self.not_contains_edit.text()
        filters["extensions"] = self.extension_edit.text()
        filters["path_includes"] = self.path_includes_edit.text()
        filters["path_excludes"] = self.path_excludes_edit.text()
        
        # Special filters
        filters["include_hidden"] = self.hidden_files_check.isChecked()
        filters["include_system"] = self.system_files_check.isChecked()
        filters["follow_symlinks"] = self.symlinks_check.isChecked()
        filters["include_temp"] = self.temp_files_check.isChecked()
        
        # File types
        file_types = []
        for type_name, check in self.file_type_checks.items():
            if check.isChecked():
                file_types.append(type_name)
        
        filters["file_types"] = file_types
        filters["exclude_types"] = self.exclude_types_radio.isChecked()
        filters["custom_types"] = self.custom_type_edit.text()
        
        # Size filters
        filters["min_size"] = self.min_size_spin.value()
        filters["min_size_unit"] = self.min_size_unit.currentIndex()
        filters["max_size"] = self.max_size_spin.value()
        filters["max_size_unit"] = self.max_size_unit.currentIndex()
        
        # Date filters
        filters["date_type"] = self.date_type_combo.currentIndex()
        filters["date_range"] = self.date_range_combo.currentIndex()
        filters["from_date"] = self.date_from.date().toString(Qt.DateFormat.ISODate)
        filters["to_date"] = self.date_to.date().toString(Qt.DateFormat.ISODate)
        
        # Regex filters
        filters["regex_name"] = self.regex_name_edit.text()
        filters["regex_path"] = self.regex_path_edit.text()
        filters["regex_case_sensitive"] = self.regex_case_sensitive.isChecked()
        
        return filters
    
    @staticmethod
    def get_filters_dialog(parent=None, current_filters=None):
        """Static method to create and show the dialog"""
        dialog = FilterDialog(parent, current_filters)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.get_filters()
        else:
            return None 