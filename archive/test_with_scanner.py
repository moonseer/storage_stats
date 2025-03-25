#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 4: MainWindow with views and core modules
"""

import sys
import os
import logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QStatusBar
from PyQt6.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test4")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import core modules
from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer

# Import UI components
from src.ui.dashboard_view import DashboardView
from src.ui.file_types_view import FileTypesView
from src.ui.file_browser_view import FileBrowserView

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test 4: Views with Core Modules")
        self.resize(800, 600)
        
        # Create scanner and analyzer
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        
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
        
        # Create FileBrowser view
        self.file_browser_view = FileBrowserView()
        self.tab_widget.addTab(self.file_browser_view, "Browser")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

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