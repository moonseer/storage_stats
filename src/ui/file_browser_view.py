#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
File browser view for navigating through the file system
"""

import os
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTreeView, QHeaderView, QSplitter, QPushButton,
    QComboBox, QLineEdit, QToolBar, QMenu, QAbstractItemView,
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, pyqtSignal, QDateTime
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QAction

from src.utils.helpers import human_readable_size, format_timestamp, get_file_icon, categorize_file_by_type

logger = logging.getLogger("StorageStats.FileBrowserView")

class FileSystemModel(QStandardItemModel):
    """Custom model for displaying file system data"""
    
    def __init__(self, parent=None):
        super().__init__(0, 4, parent)
        
        # Set headers
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
        self.setHeaderData(2, Qt.Orientation.Horizontal, "Type")
        self.setHeaderData(3, Qt.Orientation.Horizontal, "Last Modified")
        
        # Set instance variables
        self.root_path = None
        self.file_data = {}
    
    def load_data(self, scan_results, analyzer):
        """Load scan results into the model"""
        if not scan_results:
            return
        
        # Clear existing data
        self.clear()
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
        self.setHeaderData(2, Qt.Orientation.Horizontal, "Type")
        self.setHeaderData(3, Qt.Orientation.Horizontal, "Last Modified")
        
        # Set root path
        root_info = scan_results.get('root_info', {})
        self.root_path = root_info.get('path', '') if isinstance(root_info, dict) else getattr(root_info, 'path', '')
        
        # Process root directory
        self._process_directory(scan_results.get('root_info'))
    
    def _process_directory(self, dir_info):
        """Process a directory and its children"""
        if not dir_info:
            return
        
        # Create root item (parent is null for root)
        root_item = self._create_directory_item(dir_info)
        self.appendRow(root_item)
        
        # Add children
        self._add_children(dir_info, root_item)
    
    def _add_children(self, parent_info, parent_item):
        """Add child items to a parent item"""
        if not parent_info or not hasattr(parent_info, 'children'):
            return
        
        for child in sorted(parent_info.children, key=lambda x: (x.is_dir, x.name), reverse=True):
            if child.is_dir:
                dir_item = self._create_directory_item(child)
                parent_item.appendRow(dir_item)
                self._add_children(child, dir_item)
            else:
                file_item = self._create_file_item(child)
                parent_item.appendRow(file_item)
    
    def _create_directory_item(self, dir_info):
        """Create a directory item for the model"""
        name_item = QStandardItem(dir_info.name or os.path.basename(dir_info.path))
        size_item = QStandardItem(human_readable_size(dir_info.size))
        type_item = QStandardItem("Directory")
        date_item = QStandardItem(format_timestamp(dir_info.last_modified))
        
        # Store sort data
        name_item.setData(dir_info.name.lower(), Qt.ItemDataRole.UserRole)  # For case-insensitive sorting
        size_item.setData(dir_info.size, Qt.ItemDataRole.UserRole)
        date_item.setData(QDateTime(dir_info.last_modified) if dir_info.last_modified else QDateTime(), Qt.ItemDataRole.UserRole)
        
        # Store path for later reference
        name_item.setData(dir_info.path, Qt.ItemDataRole.UserRole + 1)
        
        # Set bold font for directories
        font = name_item.font()
        font.setBold(True)
        name_item.setFont(font)
        
        # Make items not editable
        name_item.setEditable(False)
        size_item.setEditable(False)
        type_item.setEditable(False)
        date_item.setEditable(False)
        
        return [name_item, size_item, type_item, date_item]
    
    def _create_file_item(self, file_info):
        """Create a file item for the model"""
        name_item = QStandardItem(file_info.name)
        size_item = QStandardItem(human_readable_size(file_info.size))
        
        # Determine file type
        file_type = "File"
        if file_info.extension:
            file_type = f"{file_info.extension} File"
        type_item = QStandardItem(file_type)
        
        date_item = QStandardItem(format_timestamp(file_info.last_modified))
        
        # Store sort data
        name_item.setData(file_info.name.lower(), Qt.ItemDataRole.UserRole)  # For case-insensitive sorting
        size_item.setData(file_info.size, Qt.ItemDataRole.UserRole)
        date_item.setData(QDateTime(file_info.last_modified) if file_info.last_modified else QDateTime(), Qt.ItemDataRole.UserRole)
        
        # Store path for later reference
        name_item.setData(file_info.path, Qt.ItemDataRole.UserRole + 1)
        
        # Make items not editable
        name_item.setEditable(False)
        size_item.setEditable(False)
        type_item.setEditable(False)
        date_item.setEditable(False)
        
        return [name_item, size_item, type_item, date_item]

class FileBrowserView(QWidget):
    """File browser view for navigating through the file system"""
    
    # Define signals
    file_selected = pyqtSignal(str)
    dir_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.current_path = None
        self.sort_column = 1  # Default sort by size
        self.sort_order = Qt.SortOrder.DescendingOrder  # Default sort descending
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Create sort selector
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Size", "Type", "Last Modified"])
        self.sort_combo.setCurrentIndex(1)  # Default sort by size
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        
        # Create filter
        filter_label = QLabel("Filter:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter files...")
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        
        # Add widgets to toolbar
        toolbar.addWidget(sort_label)
        toolbar.addWidget(self.sort_combo)
        toolbar.addSeparator()
        toolbar.addWidget(filter_label)
        toolbar.addWidget(self.filter_edit)
        
        # Add toolbar to main layout
        main_layout.addWidget(toolbar)
        
        # Create file tree view
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        
        # Create model and proxy model for sorting/filtering
        self.model = FileSystemModel(self)
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        
        # Set proxy model on tree view BEFORE configuring the header
        self.tree_view.setModel(self.proxy_model)
        
        # NOW configure the header AFTER the model is set - this is the key fix
        try:
            logger.debug("Configuring header safely after setting model")
            header = self.tree_view.header()
            header.setSectionsMovable(False)
            
            # Configure section resize modes safely
            header.setStretchLastSection(False)  # Disable default stretch behavior first
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        except Exception as e:
            logger.error(f"Error configuring header: {str(e)}", exc_info=True)
        
        # Add tree view to main layout
        main_layout.addWidget(self.tree_view)
    
    def update_view(self, scan_results, analyzer):
        """Update the view with scan results"""
        if not scan_results:
            return
        
        # Update model with scan results
        self.model.load_data(scan_results, analyzer)
        
        # Apply default sorting
        self.tree_view.sortByColumn(self.sort_column, self.sort_order)
        
        # Expand root item
        root_index = self.proxy_model.index(0, 0)
        self.tree_view.expand(root_index)
    
    def _on_sort_changed(self, index):
        """Handle sort column change"""
        self.sort_column = index
        self.tree_view.sortByColumn(self.sort_column, self.sort_order)
    
    def _on_filter_changed(self, text):
        """Handle filter text change"""
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(0)  # Filter on name column
        self.proxy_model.setFilterFixedString(text)
    
    def _on_item_double_clicked(self, index):
        """Handle item double click"""
        # Get the source model index
        source_index = self.proxy_model.mapToSource(index)
        
        # Get the name item (column 0)
        name_index = self.model.index(source_index.row(), 0, source_index.parent())
        
        # Get the path from the item data
        path = self.model.data(name_index, Qt.ItemDataRole.UserRole + 1)
        
        if os.path.isdir(path):
            # Emit signal for directory
            self.dir_selected.emit(path)
            
            # Expand directory in tree view
            self.tree_view.expand(index)
        else:
            # Emit signal for file
            self.file_selected.emit(path)
    
    def _show_context_menu(self, position):
        """Show context menu for tree view items"""
        # Get the index at the position
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        # Get the source model index
        source_index = self.proxy_model.mapToSource(index)
        
        # Get the name item (column 0)
        name_index = self.model.index(source_index.row(), 0, source_index.parent())
        
        # Get the path from the item data
        path = self.model.data(name_index, Qt.ItemDataRole.UserRole + 1)
        
        # Create context menu
        menu = QMenu(self)
        
        if os.path.isdir(path):
            # Directory actions
            menu.addAction("Open in File Explorer", lambda: self._open_in_explorer(path))
            menu.addSeparator()
            menu.addAction("Expand All", lambda: self._expand_all(index))
            menu.addAction("Collapse All", lambda: self._collapse_all(index))
        else:
            # File actions
            menu.addAction("Open in File Explorer", lambda: self._open_in_explorer(os.path.dirname(path)))
            menu.addAction("Show File Info", lambda: self._show_file_info(path))
        
        # Show the menu
        menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    def _open_in_explorer(self, path):
        """Open a path in the system file explorer"""
        # This is a placeholder - in a real app, this would use platform-specific code
        QMessageBox.information(
            self,
            "Open in File Explorer",
            f"This would open {path} in the system file explorer."
        )
    
    def _expand_all(self, index):
        """Expand all child items"""
        self.tree_view.expandRecursively(index)
    
    def _collapse_all(self, index):
        """Collapse all child items"""
        self.tree_view.collapse(index)
        
        # Reexpand the clicked item
        self.tree_view.expand(index)
    
    def _show_file_info(self, path):
        """Show detailed information about a file"""
        try:
            # Get file stats
            stat_info = os.stat(path)
            
            # Format info for display
            file_name = os.path.basename(path)
            file_size = human_readable_size(stat_info.st_size)
            file_type = os.path.splitext(path)[1] or "No extension"
            last_modified = format_timestamp(stat_info.st_mtime)
            last_accessed = format_timestamp(stat_info.st_atime)
            creation_time = format_timestamp(stat_info.st_ctime)
            
            # Show dialog with file info
            QMessageBox.information(
                self,
                f"File Information: {file_name}",
                f"<b>Path:</b> {path}<br>"
                f"<b>Size:</b> {file_size}<br>"
                f"<b>Type:</b> {file_type}<br>"
                f"<b>Last Modified:</b> {last_modified}<br>"
                f"<b>Last Accessed:</b> {last_accessed}<br>"
                f"<b>Creation Time:</b> {creation_time}"
            )
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}", exc_info=True)
            QMessageBox.warning(
                self,
                "Error",
                f"Could not get file information: {str(e)}"
            ) 