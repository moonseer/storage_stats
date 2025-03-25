#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Dialog for displaying keyboard shortcuts
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

logger = logging.getLogger("StorageStats.ShortcutsDialog")

class ShortcutsDialog(QDialog):
    """Dialog displaying keyboard shortcuts for the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(600, 400)
        self.resize(600, 400)
        self._create_ui()
    
    def _create_ui(self):
        """Create the dialog UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header label
        header_label = QLabel("Storage Stats Keyboard Shortcuts")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description label
        desc_label = QLabel(
            "Use these keyboard shortcuts to navigate and control the application more efficiently."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Shortcuts table
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(2)
        self.shortcuts_table.setHorizontalHeaderLabels(["Shortcut", "Description"])
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.shortcuts_table.verticalHeader().setVisible(False)
        self.shortcuts_table.setAlternatingRowColors(True)
        
        # Populate shortcuts
        self._populate_shortcuts()
        
        layout.addWidget(self.shortcuts_table)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    def _populate_shortcuts(self):
        """Populate the shortcuts table with all available shortcuts"""
        shortcuts = [
            # File menu
            ("Ctrl+O", "Open directory for scanning"),
            ("Ctrl+R", "Resume a previous scan"),
            ("Ctrl+C", "Cancel current scan"),
            ("Ctrl+E", "Export report"),
            ("Ctrl+Q", "Quit application"),
            
            # Edit menu
            ("Ctrl+,", "Open settings"),
            
            # View menu
            ("F5", "Refresh current view"),
            ("Ctrl+1", "Switch to Dashboard tab"),
            ("Ctrl+2", "Switch to Files & Folders tab"),
            ("Ctrl+3", "Switch to Duplicates tab"),
            ("Ctrl+4", "Switch to File Types tab"),
            ("Ctrl+5", "Switch to Recommendations tab"),
            
            # View shortcuts
            ("Ctrl++", "Zoom in"),
            ("Ctrl+-", "Zoom out"),
            ("Ctrl+0", "Reset zoom"),
            
            # File list navigation
            ("Up/Down", "Navigate through files"),
            ("Enter", "Open selected file/directory"),
            ("Delete", "Add file to deletion list"),
            ("Space", "Select/deselect file"),
            
            # Filter and search
            ("Ctrl+F", "Search files"),
            ("Esc", "Clear search/filter"),
            
            # Sorting
            ("Alt+S", "Sort by size"),
            ("Alt+N", "Sort by name"),
            ("Alt+D", "Sort by date"),
            ("Alt+T", "Sort by type"),
            
            # Misc
            ("F1", "Show this help dialog"),
            ("F11", "Toggle fullscreen mode")
        ]
        
        # Set the number of rows needed
        self.shortcuts_table.setRowCount(len(shortcuts))
        
        # Add shortcuts to the table
        for i, (shortcut, description) in enumerate(shortcuts):
            shortcut_item = QTableWidgetItem(shortcut)
            description_item = QTableWidgetItem(description)
            
            # Make items non-editable
            shortcut_item.setFlags(shortcut_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            description_item.setFlags(description_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            self.shortcuts_table.setItem(i, 0, shortcut_item)
            self.shortcuts_table.setItem(i, 1, description_item)
        
        # Resize the first column to content
        self.shortcuts_table.resizeColumnToContents(0)
    
    @staticmethod
    def show_dialog(parent=None):
        """Static method to create and show the dialog"""
        dialog = ShortcutsDialog(parent)
        dialog.exec()
        return dialog 