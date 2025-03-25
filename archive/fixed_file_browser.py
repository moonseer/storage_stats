#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fixed version of FileBrowserView that avoids segmentation faults
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FixedFileBrowser")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QTreeView, QHeaderView, QComboBox, QLineEdit, QToolBar
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class SafeFileSystemModel(QStandardItemModel):
    """Safe model for displaying file system data"""
    
    def __init__(self, parent=None):
        logger.debug("Initializing SafeFileSystemModel")
        super().__init__(0, 2, parent)  # Just name and size columns
        
        # Set headers
        self.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        self.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
        
        # Set root item with test data
        root_item = QStandardItem("Root")
        size_item = QStandardItem("0 B")
        
        # Make items not editable
        root_item.setEditable(False)
        size_item.setEditable(False)
        
        self.appendRow([root_item, size_item])
        
        # Add some children
        for i in range(5):
            child_item = QStandardItem(f"Item {i}")
            child_size = QStandardItem(f"{i*100} KB")
            child_item.setEditable(False)
            child_size.setEditable(False)
            root_item.appendRow([child_item, child_size])
        
        logger.debug("SafeFileSystemModel initialized")

class FixedFileBrowserView(QWidget):
    """Fixed FileBrowserView that avoids segmentation faults"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        logger.debug("Initializing FixedFileBrowserView")
        super().__init__(parent)
        
        # Create layout first
        self.layout = QVBoxLayout(self)
        
        # Add a label
        self.label = QLabel("Fixed File Browser View")
        self.layout.addWidget(self.label)
        
        # Create a simple toolbar
        self._create_toolbar()
        
        # Create and set up tree view SAFELY - avoiding the header configuration that causes segfaults
        self._create_tree_view_safely()
        
        logger.debug("FixedFileBrowserView initialized")
    
    def _create_toolbar(self):
        """Create toolbar with controls"""
        logger.debug("Creating toolbar")
        
        toolbar = QToolBar()
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Size"])
        toolbar.addWidget(sort_label)
        toolbar.addWidget(self.sort_combo)
        
        filter_label = QLabel("Filter:")
        self.filter_edit = QLineEdit()
        toolbar.addWidget(filter_label)
        toolbar.addWidget(self.filter_edit)
        
        # Connect filter edit to proxy model
        # self.filter_edit.textChanged.connect(self._update_filter)
        
        self.layout.addWidget(toolbar)
        logger.debug("Toolbar created")
    
    def _create_tree_view_safely(self):
        """Create tree view with model but avoid problematic header configuration"""
        logger.debug("Creating tree view safely")
        
        # Create QTreeView first
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        
        # Create model and set it on the tree view BEFORE configuring the header
        self.model = SafeFileSystemModel(self)
        
        # Create proxy model
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        
        # Set model on tree view
        self.tree_view.setModel(self.proxy_model)
        
        # NOW configure the header AFTER the model is set
        try:
            logger.debug("Configuring header safely")
            header = self.tree_view.header()
            # Avoid setSectionsMovable which caused issues
            # Instead of header.setSectionResizeMode on index 0, set it on all sections
            header.setStretchLastSection(True)
        except Exception as e:
            logger.error(f"Error configuring header (safe approach used): {e}", exc_info=True)
        
        # Add tree view to layout
        self.layout.addWidget(self.tree_view)
        logger.debug("Tree view created safely")
    
    def update_view(self, scan_results, analyzer):
        """Update view with scan results - safely implemented"""
        logger.debug("update_view called (safe implementation)")
        
        # Clear the model first
        self.model.clear()
        
        # Reset headers after clearing
        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
        
        # If we have results, show them
        if scan_results:
            logger.info(f"Updating view with scan results: {len(scan_results)} items")
            # Add data safely...
        else:
            logger.warning("No scan results to show")

# Test main window to verify fixed components
class TestMainWindow(QMainWindow):
    def __init__(self):
        logger.debug("Initializing TestMainWindow")
        super().__init__()
        self.setWindowTitle("Fixed FileBrowserView Test")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create and add FixedFileBrowserView
        logger.debug("About to create FixedFileBrowserView")
        self.file_browser_view = FixedFileBrowserView()
        logger.debug("FixedFileBrowserView created successfully")
        layout.addWidget(self.file_browser_view)
        
        logger.debug("TestMainWindow initialized")

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    logger.info("Creating test window")
    window = TestMainWindow()
    logger.info("Showing test window")
    window.show()
    
    # Start event loop
    logger.info("Starting event loop")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 