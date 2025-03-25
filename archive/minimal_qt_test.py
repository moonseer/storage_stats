#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal PyQt6 test to identify the component causing segmentation fault
"""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MinimalQtTest")

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTreeView
from PyQt6.QtCore import QTimer

class ComponentTester(QMainWindow):
    def __init__(self):
        logger.debug("Starting ComponentTester initialization")
        super().__init__()
        self.setWindowTitle("Component Tester")
        self.resize(400, 300)
        
        # Create central widget and layout
        logger.debug("Creating central widget")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        logger.debug("Creating layout")
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add status label
        logger.debug("Creating status label")
        self.status_label = QLabel("Ready to test components")
        self.layout.addWidget(self.status_label)
        
        # Add test buttons
        self.create_test_buttons()
        
        # Initialize test components as None
        self.tree_view = None
        
        logger.debug("ComponentTester initialization complete")
    
    def create_test_buttons(self):
        logger.debug("Creating test buttons")
        
        # Button to create QTreeView
        self.tree_view_button = QPushButton("Create QTreeView")
        self.tree_view_button.clicked.connect(self.create_tree_view)
        self.layout.addWidget(self.tree_view_button)
        
        logger.debug("Test buttons created")
    
    def create_tree_view(self):
        logger.debug("About to create QTreeView")
        try:
            self.tree_view = QTreeView()
            logger.debug("QTreeView created successfully")
            self.status_label.setText("QTreeView created successfully")
            
            # Add it to layout
            self.layout.addWidget(self.tree_view)
            logger.debug("QTreeView added to layout")
        except Exception as e:
            logger.error(f"Error creating QTreeView: {e}", exc_info=True)
            self.status_label.setText(f"Error: {e}")

def main():
    # Create application
    logger.info("Creating QApplication")
    app = QApplication(sys.argv)
    
    # Create window
    logger.info("Creating ComponentTester window")
    window = ComponentTester()
    
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