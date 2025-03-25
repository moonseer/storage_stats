#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified FileBrowserView for testing
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SimpleFileBrowser")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
    QTreeView, QHeaderView, QComboBox, QLineEdit, QToolBar
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem

# Create a simplified FileSystemModel without icon loading
class SimpleFileSystemModel(QStandardItemModel):
    """Simplified model for displaying file system data"""
    
    def __init__(self, parent=None):
        logger.debug("Initializing SimpleFileSystemModel")
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
        
        logger.debug("SimpleFileSystemModel initialized")

# Create a simplified FileBrowserView
class SimpleFileBrowserView(QWidget):
    """Simplified FileBrowserView for testing"""
    
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        logger.debug("Initializing SimpleFileBrowserView")
        super().__init__(parent)
        
        # Just create a basic layout
        self.layout = QVBoxLayout(self)
        
        # Add a label
        self.label = QLabel("Simple File Browser View")
        self.layout.addWidget(self.label)
        
        # Create a simple toolbar
        toolbar = QToolBar()
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Size"])
        toolbar.addWidget(sort_label)
        toolbar.addWidget(self.sort_combo)
        self.layout.addWidget(toolbar)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        
        # Configure header
        header = self.tree_view.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Create model and proxy model
        self.model = SimpleFileSystemModel(self)
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        
        # Set model on tree view
        self.tree_view.setModel(self.proxy_model)
        
        # Add tree view to layout
        self.layout.addWidget(self.tree_view)
        
        logger.debug("SimpleFileBrowserView initialized")
    
    def update_view(self, scan_results, analyzer):
        """Simplified update_view that does minimal processing"""
        logger.debug("update_view called (simplified)")
        # Nothing to do, we use static test data

# Create a main window to test the view
class TestWindow(QMainWindow):
    def __init__(self):
        logger.debug("Initializing TestWindow")
        super().__init__()
        self.setWindowTitle("FileBrowserView Test")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create and add SimpleFileBrowserView
        logger.debug("About to create SimpleFileBrowserView")
        self.file_browser_view = SimpleFileBrowserView()
        logger.debug("SimpleFileBrowserView created successfully")
        layout.addWidget(self.file_browser_view)
        
        logger.debug("TestWindow initialized")

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    logger.info("Creating test window")
    window = TestWindow()
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