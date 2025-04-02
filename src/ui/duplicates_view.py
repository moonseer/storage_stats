#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Duplicates view for displaying and managing duplicate files
"""

import os
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTreeWidget, QTreeWidgetItem, QHeaderView, QSplitter, QPushButton,
    QCheckBox, QRadioButton, QButtonGroup, QComboBox, QLineEdit, 
    QToolBar, QMessageBox, QFrame, QSpinBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QAction

from src.utils.helpers import human_readable_size, format_timestamp, safe_delete

logger = logging.getLogger("StorageStats.DuplicatesView")

class DuplicatesView(QWidget):
    """Duplicates view for displaying and managing duplicate files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.duplicate_groups = {}
        self.total_duplicates = 0
        self.total_wasted_space = 0
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create header section
        header_layout = QHBoxLayout()
        
        self.stats_label = QLabel("No duplicate files found.")
        stats_font = self.stats_label.font()
        stats_font.setPointSize(12)
        stats_font.setBold(True)
        self.stats_label.setFont(stats_font)
        
        header_layout.addWidget(self.stats_label)
        header_layout.addStretch()
        
        # Add sorting options
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Wasted Space (largest first)", "File Size", "Number of Duplicates"])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        
        header_layout.addWidget(sort_label)
        header_layout.addWidget(self.sort_combo)
        
        # Add min size filter
        min_size_label = QLabel("Min Size:")
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 10000)
        self.min_size_spin.setValue(1)
        self.min_size_spin.setSuffix(" MB")
        self.min_size_spin.valueChanged.connect(self._on_filter_changed)
        
        header_layout.addWidget(min_size_label)
        header_layout.addWidget(self.min_size_spin)
        
        main_layout.addLayout(header_layout)
        
        # Add instructions
        instructions_label = QLabel(
            "Below are groups of identical files. You can select files to keep or remove. "
            "This application will not delete any files; it will only provide recommendations."
        )
        instructions_label.setWordWrap(True)
        main_layout.addWidget(instructions_label)
        
        # Create tree widget for duplicates
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(4)
        self.tree_widget.setHeaderLabels(["File Path", "Size", "Last Modified", "Actions"])
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Configure header
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.tree_widget)
        
        # Add actions toolbar
        actions_layout = QHBoxLayout()
        
        self.select_originals_btn = QPushButton("Select Originals")
        self.select_originals_btn.setToolTip("Select the oldest file in each duplicate group")
        self.select_originals_btn.clicked.connect(self._select_originals)
        
        self.select_newest_btn = QPushButton("Select Newest")
        self.select_newest_btn.setToolTip("Select the newest file in each duplicate group")
        self.select_newest_btn.clicked.connect(self._select_newest)
        
        self.copy_to_clipboard_btn = QPushButton("Copy File List")
        self.copy_to_clipboard_btn.setToolTip("Copy list of selected files to clipboard")
        self.copy_to_clipboard_btn.clicked.connect(self._copy_to_clipboard)
        
        actions_layout.addWidget(self.select_originals_btn)
        actions_layout.addWidget(self.select_newest_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.copy_to_clipboard_btn)
        
        main_layout.addLayout(actions_layout)
        
        # Add empty view message
        self.empty_view_label = QLabel(
            "No duplicate files found. Run a scan to find duplicates."
        )
        self.empty_view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_view_font = self.empty_view_label.font()
        empty_view_font.setPointSize(14)
        self.empty_view_label.setFont(empty_view_font)
        
        main_layout.addWidget(self.empty_view_label)
        
        # Initially show empty view
        self.tree_widget.setVisible(False)
        self.empty_view_label.setVisible(True)
        self.select_originals_btn.setEnabled(False)
        self.select_newest_btn.setEnabled(False)
        self.copy_to_clipboard_btn.setEnabled(False)
    
    def update_view(self, scan_results, analyzer):
        """Update the view with scan results"""
        if not scan_results:
            return
        
        # Get duplicate files from analyzer
        self.duplicate_groups = analyzer.get_duplicate_files()
        
        # Check if duplicates were found
        if not self.duplicate_groups:
            self.tree_widget.setVisible(False)
            self.empty_view_label.setVisible(True)
            self.stats_label.setText("No duplicate files found.")
            self.select_originals_btn.setEnabled(False)
            self.select_newest_btn.setEnabled(False)
            self.copy_to_clipboard_btn.setEnabled(False)
            return
        
        # Add human-readable size fields to each group
        for hash_key, group in self.duplicate_groups.items():
            group['size_human'] = human_readable_size(group['size'])
            group['wasted_space_human'] = human_readable_size(group['wasted_space'])
            
            # Ensure each file has the expected fields
            for file_info in group['files']:
                # Convert mtime to last_modified for compatibility with the tree view
                if 'mtime' in file_info and 'last_modified' not in file_info:
                    file_info['last_modified'] = file_info['mtime']
        
        # Calculate statistics
        self.total_duplicates = sum(group['count'] for group in self.duplicate_groups.values())
        self.total_wasted_space = sum(group['wasted_space'] for group in self.duplicate_groups.values())
        
        # Update stats label
        self.stats_label.setText(
            f"Found {len(self.duplicate_groups)} duplicate groups with {self.total_duplicates} files "
            f"wasting {human_readable_size(self.total_wasted_space)}"
        )
        
        # Show tree widget and hide empty view
        self.tree_widget.setVisible(True)
        self.empty_view_label.setVisible(False)
        self.select_originals_btn.setEnabled(True)
        self.select_newest_btn.setEnabled(True)
        
        # Populate tree widget
        self._populate_tree()
    
    def _populate_tree(self):
        """Populate the tree widget with duplicate groups"""
        # Clear existing items
        self.tree_widget.clear()
        
        # Get min size filter
        min_size_bytes = self.min_size_spin.value() * 1024 * 1024
        
        # Sort the duplicate groups based on the current sort option
        sorted_groups = self._get_sorted_groups()
        
        # Add groups to tree
        for hash_value, group in sorted_groups:
            # Skip groups smaller than min size
            if group['size'] < min_size_bytes:
                continue
                
            # Create group item
            group_item = QTreeWidgetItem(self.tree_widget)
            group_item.setText(0, f"Group of {group['count']} identical files")
            group_item.setText(1, group['size_human'])
            group_item.setText(2, f"Wasted: {group['wasted_space_human']}")
            
            # Set bold font for group
            font = group_item.font(0)
            font.setBold(True)
            for i in range(4):
                group_item.setFont(i, font)
            
            # Set background color for group header
            for i in range(4):
                group_item.setBackground(i, QColor("#e0e0e0"))
            
            # Add files to group
            for i, file_info in enumerate(group['files']):
                file_item = QTreeWidgetItem(group_item)
                file_item.setText(0, file_info['path'])
                file_item.setText(1, group['size_human'])
                file_item.setText(2, format_timestamp(file_info['last_modified']))
                
                # Store file data for later use
                file_item.setData(0, Qt.ItemDataRole.UserRole, {
                    'path': file_info['path'],
                    'last_modified': file_info['last_modified']
                })
                
                # Add select button (this would be implemented with a custom delegate in a real app)
                # For simplicity, we're just adding text here
                file_item.setText(3, "Keep" if i == 0 else "Remove")
            
            # Expand the group
            group_item.setExpanded(True)
    
    def _get_sorted_groups(self):
        """Get duplicate groups sorted according to current sort option"""
        sort_index = self.sort_combo.currentIndex()
        
        if sort_index == 0:  # Wasted Space
            key_func = lambda x: x[1]['wasted_space']
        elif sort_index == 1:  # File Size
            key_func = lambda x: x[1]['size']
        elif sort_index == 2:  # Number of Duplicates
            key_func = lambda x: x[1]['count']
        else:
            key_func = lambda x: x[1]['wasted_space']
        
        # Convert dict to list of (key, value) tuples and sort
        return sorted(self.duplicate_groups.items(), key=key_func, reverse=True)
    
    def _on_sort_changed(self, index):
        """Handle sort option change"""
        if self.duplicate_groups:
            self._populate_tree()
    
    def _on_filter_changed(self, value):
        """Handle min size filter change"""
        if self.duplicate_groups:
            self._populate_tree()
    
    def _on_selection_changed(self):
        """Handle selection change in tree widget"""
        # Enable/disable copy button based on selection
        self.copy_to_clipboard_btn.setEnabled(len(self.tree_widget.selectedItems()) > 0)
    
    def _select_originals(self):
        """Select the oldest file in each duplicate group"""
        self.tree_widget.clearSelection()
        
        # Iterate through top-level items (groups)
        for i in range(self.tree_widget.topLevelItemCount()):
            group_item = self.tree_widget.topLevelItem(i)
            
            # Find the oldest file in the group
            oldest_index = -1
            oldest_time = None
            
            for j in range(group_item.childCount()):
                child_item = group_item.child(j)
                file_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                
                if file_data and 'last_modified' in file_data:
                    if oldest_time is None or file_data['last_modified'] < oldest_time:
                        oldest_time = file_data['last_modified']
                        oldest_index = j
            
            # Select the oldest file
            if oldest_index >= 0:
                oldest_item = group_item.child(oldest_index)
                oldest_item.setSelected(True)
    
    def _select_newest(self):
        """Select the newest file in each duplicate group"""
        self.tree_widget.clearSelection()
        
        # Iterate through top-level items (groups)
        for i in range(self.tree_widget.topLevelItemCount()):
            group_item = self.tree_widget.topLevelItem(i)
            
            # Find the newest file in the group
            newest_index = -1
            newest_time = None
            
            for j in range(group_item.childCount()):
                child_item = group_item.child(j)
                file_data = child_item.data(0, Qt.ItemDataRole.UserRole)
                
                if file_data and 'last_modified' in file_data:
                    if newest_time is None or file_data['last_modified'] > newest_time:
                        newest_time = file_data['last_modified']
                        newest_index = j
            
            # Select the newest file
            if newest_index >= 0:
                newest_item = group_item.child(newest_index)
                newest_item.setSelected(True)
    
    def _copy_to_clipboard(self):
        """Copy list of selected files to clipboard"""
        selected_items = self.tree_widget.selectedItems()
        
        if not selected_items:
            return
        
        # Build file list
        file_list = []
        for item in selected_items:
            # Skip group items (they don't have file data)
            if item.parent() is None:
                continue
                
            file_data = item.data(0, Qt.ItemDataRole.UserRole)
            if file_data and 'path' in file_data:
                file_list.append(file_data['path'])
        
        # Copy to clipboard
        if file_list:
            QApplication.clipboard().setText('\n'.join(file_list))
            
            QMessageBox.information(
                self,
                "Copied to Clipboard",
                f"Copied {len(file_list)} file paths to clipboard"
            ) 