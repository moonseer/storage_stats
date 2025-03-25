#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive MainWindow test with multiple views
"""

import sys
import os
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, 
    QWidget, QTabWidget, QStatusBar, QToolBar, QMenuBar, QMenu,
    QFileDialog, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal

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

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiViewTest")

class ComprehensiveMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Comprehensive Main Window Test")
        self.resize(900, 700)
        
        # Create scanner and analyzer
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        
        # Connect scanner signals
        self.scanner.scan_started.connect(self._on_scan_started)
        self.scanner.scan_progress.connect(self._on_scan_progress)
        self.scanner.scan_finished.connect(self._on_scan_completed)
        self.scanner.scan_error.connect(self._on_scan_error)
        
        # Setup UI
        self._setup_ui()
        
        # Initialize scan results
        self.scan_results = None
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create central widget with tab widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create and add views
        self.dashboard_view = DashboardView()
        self.dashboard_view.scan_requested.connect(self.select_directory)
        
        self.file_types_view = FileTypesView()
        self.file_browser_view = FileBrowserView()
        
        # Add tabs
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        self.tab_widget.addTab(self.file_types_view, "File Types")
        self.tab_widget.addTab(self.file_browser_view, "Browser")
        
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
        
        scan_action = file_menu.addAction("Scan Directory")
        scan_action.triggered.connect(self.select_directory)
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        scan_btn = QPushButton("Scan Directory")
        scan_btn.clicked.connect(self.select_directory)
        toolbar.addWidget(scan_btn)
    
    def select_directory(self):
        """Open a directory selection dialog and start scan"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Scan",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.scan_directory(directory)
    
    def scan_directory(self, directory):
        """Start scanning a directory"""
        try:
            logger.info(f"Starting scan of {directory}")
            self.scanner.scan_directory(directory)
        except Exception as e:
            logger.error(f"Error starting scan: {str(e)}")
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def _on_scan_started(self, directory):
        """Handle scan started signal"""
        logger.info(f"Scan started: {directory}")
        self.status_bar.showMessage(f"Scanning {directory}...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        try:
            if total > 0:
                percent = int((current / total) * 100)
                self.progress_bar.setValue(percent)
            self.status_bar.showMessage(f"Scanning: {current_path}")
        except Exception as e:
            logger.error(f"Error in scan progress handler: {e}")
            # Don't crash on progress updates
    
    def _on_scan_completed(self, results):
        """Handle scan completed signal"""
        logger.info("Scan completed")
        self.status_bar.showMessage("Scan completed")
        self.progress_bar.setVisible(False)
        
        # Save scan results
        self.scan_results = results
        
        # Process results with analyzer
        self.analyzer.process_scan_results(results)
        
        # Update views
        try:
            self.dashboard_view.update_view(results, self.analyzer)
            self.file_types_view.update_view(results, self.analyzer)
            self.file_browser_view.update_view(results, self.analyzer)
        except Exception as e:
            logger.error(f"Error updating views: {str(e)}")
    
    def _on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.error(f"Scan error: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")
        self.progress_bar.setVisible(False)
        
def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    window = ComprehensiveMainWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 