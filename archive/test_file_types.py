#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test 2: MainWindow with DashboardView and FileTypesView
"""

import sys
import os
import logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PyQt6.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test2")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import UI components
from src.ui.dashboard_view import DashboardView
from src.ui.file_types_view import FileTypesView

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test 2: DashboardView and FileTypesView")
        self.resize(800, 600)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create Dashboard view
        self.dashboard_view = DashboardView()
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        
        # Create FileTypes view
        self.file_types_view = FileTypesView()
        self.tab_widget.addTab(self.file_types_view, "File Types")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    window = TestMainWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 