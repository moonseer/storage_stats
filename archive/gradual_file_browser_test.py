#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gradual FileBrowserView test to identify the component causing segmentation fault
"""

import sys
import os
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("GradualFileBrowserTest")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
    QPushButton, QTreeView, QHeaderView, QToolBar, QComboBox
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class GradualTestMainWindow(QMainWindow):
    def __init__(self):
        logger.debug("Starting GradualTestMainWindow initialization")
        super().__init__()
        self.setWindowTitle("Gradual FileBrowserView Test")
        self.resize(800, 600)
        
        # Create central widget and layout
        logger.debug("Creating central widget")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        logger.debug("Creating layout")
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add status label
        logger.debug("Creating status label")
        self.status_label = QLabel("Click buttons to test components")
        self.layout.addWidget(self.status_label)
        
        # Create test buttons
        self.create_test_buttons()
        
        # Add container for test views
        self.test_container = QWidget()
        self.test_layout = QVBoxLayout(self.test_container)
        self.layout.addWidget(self.test_container)
        
        logger.debug("GradualTestMainWindow initialization complete")
    
    def create_test_buttons(self):
        logger.debug("Creating test buttons")
        
        button_layout = QVBoxLayout()
        
        # Button 1: Create basic QTreeView
        self.basic_tree_button = QPushButton("1. Create Basic QTreeView")
        self.basic_tree_button.clicked.connect(self.create_basic_tree_view)
        button_layout.addWidget(self.basic_tree_button)
        
        # Button 2: Create QTreeView with headers
        self.header_tree_button = QPushButton("2. Create QTreeView with Headers")
        self.header_tree_button.clicked.connect(self.create_tree_with_headers)
        button_layout.addWidget(self.header_tree_button)
        
        # Button 3: Create QTreeView with model
        self.model_tree_button = QPushButton("3. Create QTreeView with Model")
        self.model_tree_button.clicked.connect(self.create_tree_with_model)
        button_layout.addWidget(self.model_tree_button)
        
        # Button 4: Create QTreeView with model and proxy
        self.proxy_tree_button = QPushButton("4. Create QTreeView with Model + Proxy")
        self.proxy_tree_button.clicked.connect(self.create_tree_with_proxy)
        button_layout.addWidget(self.proxy_tree_button)
        
        # Button 5: Create complete simple file browser
        self.complete_button = QPushButton("5. Create Complete Simple File Browser")
        self.complete_button.clicked.connect(self.create_complete_file_browser)
        button_layout.addWidget(self.complete_button)
        
        # Button 6: Try importing FileSystemModel from real code
        self.import_model_button = QPushButton("6. Try importing FileSystemModel")
        self.import_model_button.clicked.connect(self.try_import_real_model)
        button_layout.addWidget(self.import_model_button)
        
        # Button 7: Try creating real FileBrowserView 
        self.create_real_view_button = QPushButton("7. Try creating real FileBrowserView")
        self.create_real_view_button.clicked.connect(self.try_create_real_view)
        button_layout.addWidget(self.create_real_view_button)
        
        # Add button layout to main layout
        self.layout.addLayout(button_layout)
        
        logger.debug("Test buttons created")
    
    def clear_test_container(self):
        """Clear the test container before adding new widgets"""
        logger.debug("Clearing test container")
        # Remove all widgets from the layout
        while self.test_layout.count():
            item = self.test_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Reset status
        self.status_label.setText("Test container cleared")
    
    def create_basic_tree_view(self):
        """Create a basic QTreeView with no model or headers"""
        logger.debug("Creating basic QTreeView")
        try:
            self.clear_test_container()
            
            tree_view = QTreeView()
            self.test_layout.addWidget(tree_view)
            
            self.status_label.setText("Basic QTreeView created successfully")
            logger.debug("Basic QTreeView created successfully")
        except Exception as e:
            logger.error(f"Error creating basic QTreeView: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")
    
    def create_tree_with_headers(self):
        """Create a QTreeView with configured headers"""
        logger.debug("Creating QTreeView with headers")
        try:
            self.clear_test_container()
            
            tree_view = QTreeView()
            tree_view.setAlternatingRowColors(True)
            
            # Configure header
            header = tree_view.header()
            header.setSectionsMovable(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            
            self.test_layout.addWidget(tree_view)
            
            self.status_label.setText("QTreeView with headers created successfully")
            logger.debug("QTreeView with headers created successfully")
        except Exception as e:
            logger.error(f"Error creating QTreeView with headers: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")
    
    def create_tree_with_model(self):
        """Create a QTreeView with a standard item model"""
        logger.debug("Creating QTreeView with model")
        try:
            self.clear_test_container()
            
            tree_view = QTreeView()
            tree_view.setAlternatingRowColors(True)
            
            # Configure header
            header = tree_view.header()
            header.setSectionsMovable(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            
            # Create model
            model = QStandardItemModel(0, 2)
            model.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
            
            # Add some items
            root_item = QStandardItem("Root")
            size_item = QStandardItem("0 B")
            model.appendRow([root_item, size_item])
            
            # Add child items
            for i in range(5):
                child_item = QStandardItem(f"Item {i}")
                child_size = QStandardItem(f"{i*100} KB")
                root_item.appendRow([child_item, child_size])
            
            # Set model on tree view
            tree_view.setModel(model)
            
            self.test_layout.addWidget(tree_view)
            
            self.status_label.setText("QTreeView with model created successfully")
            logger.debug("QTreeView with model created successfully")
        except Exception as e:
            logger.error(f"Error creating QTreeView with model: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")
    
    def create_tree_with_proxy(self):
        """Create a QTreeView with model and proxy model"""
        logger.debug("Creating QTreeView with model and proxy")
        try:
            self.clear_test_container()
            
            tree_view = QTreeView()
            tree_view.setAlternatingRowColors(True)
            
            # Configure header
            header = tree_view.header()
            header.setSectionsMovable(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            
            # Create model
            model = QStandardItemModel(0, 2)
            model.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
            
            # Add some items
            root_item = QStandardItem("Root")
            size_item = QStandardItem("0 B")
            model.appendRow([root_item, size_item])
            
            # Add child items
            for i in range(5):
                child_item = QStandardItem(f"Item {i}")
                child_size = QStandardItem(f"{i*100} KB")
                root_item.appendRow([child_item, child_size])
            
            # Create proxy model
            proxy_model = QSortFilterProxyModel()
            proxy_model.setSourceModel(model)
            
            # Set model on tree view
            tree_view.setModel(proxy_model)
            
            self.test_layout.addWidget(tree_view)
            
            self.status_label.setText("QTreeView with model and proxy created successfully")
            logger.debug("QTreeView with model and proxy created successfully")
        except Exception as e:
            logger.error(f"Error creating QTreeView with model and proxy: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")
    
    def create_complete_file_browser(self):
        """Create a complete simple file browser with all components"""
        logger.debug("Creating complete simple file browser")
        try:
            self.clear_test_container()
            
            # Create container widget with layout
            browser_widget = QWidget()
            browser_layout = QVBoxLayout(browser_widget)
            
            # Create toolbar with controls
            toolbar = QToolBar()
            sort_label = QLabel("Sort by:")
            sort_combo = QComboBox()
            sort_combo.addItems(["Name", "Size"])
            toolbar.addWidget(sort_label)
            toolbar.addWidget(sort_combo)
            browser_layout.addWidget(toolbar)
            
            # Create tree view
            tree_view = QTreeView()
            tree_view.setAlternatingRowColors(True)
            
            # Configure header
            header = tree_view.header()
            header.setSectionsMovable(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            
            # Create model
            model = QStandardItemModel(0, 2)
            model.setHeaderData(0, Qt.Orientation.Horizontal, "Name")
            model.setHeaderData(1, Qt.Orientation.Horizontal, "Size")
            
            # Add some items
            root_item = QStandardItem("Root")
            size_item = QStandardItem("0 B")
            model.appendRow([root_item, size_item])
            
            # Add child items
            for i in range(5):
                child_item = QStandardItem(f"Item {i}")
                child_size = QStandardItem(f"{i*100} KB")
                root_item.appendRow([child_item, child_size])
            
            # Create proxy model
            proxy_model = QSortFilterProxyModel()
            proxy_model.setSourceModel(model)
            
            # Set model on tree view
            tree_view.setModel(proxy_model)
            
            # Add tree view to layout
            browser_layout.addWidget(tree_view)
            
            # Add the browser widget to test container
            self.test_layout.addWidget(browser_widget)
            
            self.status_label.setText("Complete simple file browser created successfully")
            logger.debug("Complete simple file browser created successfully")
        except Exception as e:
            logger.error(f"Error creating complete file browser: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")
    
    def try_import_real_model(self):
        """Try importing the real FileSystemModel from the source code"""
        logger.debug("Trying to import real FileSystemModel")
        try:
            self.clear_test_container()
            
            # Try importing
            from ui.file_browser_view import FileSystemModel
            
            # Create a status label to show result
            result_label = QLabel("Successfully imported FileSystemModel from ui.file_browser_view")
            self.test_layout.addWidget(result_label)
            
            self.status_label.setText("FileSystemModel imported successfully")
            logger.debug("FileSystemModel imported successfully")
        except Exception as e:
            logger.error(f"Error importing FileSystemModel: {e}", exc_info=True)
            self.status_label.setText(f"Import error: {str(e)}")
            error_label = QLabel(f"Import error: {str(e)}\n{traceback.format_exc()}")
            error_label.setWordWrap(True)
            self.test_layout.addWidget(error_label)
    
    def try_create_real_view(self):
        """Try creating the real FileBrowserView from the source code"""
        logger.debug("Trying to create real FileBrowserView")
        try:
            self.clear_test_container()
            
            # Try importing
            from ui.file_browser_view import FileBrowserView
            
            # Try creating an instance
            file_browser_view = FileBrowserView()
            
            # Add to layout
            self.test_layout.addWidget(file_browser_view)
            
            self.status_label.setText("FileBrowserView created successfully")
            logger.debug("FileBrowserView created successfully")
        except Exception as e:
            logger.error(f"Error creating FileBrowserView: {e}", exc_info=True)
            self.status_label.setText(f"Creation error: {str(e)}")
            error_label = QLabel(f"Creation error: {str(e)}\n{traceback.format_exc()}")
            error_label.setWordWrap(True)
            self.test_layout.addWidget(error_label)

def main():
    # Create application
    logger.info("Creating QApplication")
    app = QApplication(sys.argv)
    
    # Create window
    logger.info("Creating GradualTestMainWindow")
    window = GradualTestMainWindow()
    
    # Show window
    logger.info("Showing window")
    window.show()
    
    logger.info("Application started")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 