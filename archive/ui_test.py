#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified MainWindow test application
"""

import sys
import os
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, 
    QWidget, QTabWidget, QStatusBar, QToolBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import core modules
from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer
# Import one UI component
from src.ui.dashboard_view import DashboardView

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UITest")

class SimpleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Main Window Test")
        self.resize(800, 600)
        
        # Create scanner and analyzer
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create central widget with tab widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create Dashboard view
        self.dashboard_view = DashboardView()
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Scan menu
        scan_menu = menu_bar.addMenu("&Scan")
        scan_action = scan_menu.addAction("Scan Directory")
        
        # Report menu
        report_menu = menu_bar.addMenu("&Report")
        report_action = report_menu.addAction("Generate Report")

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    window = SimpleMainWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 