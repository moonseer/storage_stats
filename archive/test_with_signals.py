#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test 5: MainWindow with views, core modules, and signal connections
"""

import sys
import os
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, 
    QStatusBar, QProgressBar, QPushButton, QToolBar
)
from PyQt6.QtCore import Qt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test5")

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
        self.setWindowTitle("Test 5: Views with Signals")
        self.resize(800, 600)
        
        # Create scanner and analyzer
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        
        # Connect scanner signals - NOTE: THIS IS WHERE THE SEGFAULT MIGHT OCCUR
        try:
            logger.info("Connecting scanner signals")
            self.scanner.scan_started.connect(self._on_scan_started)
            logger.info("Connected scan_started signal")
            
            self.scanner.scan_progress.connect(self._on_scan_progress)
            logger.info("Connected scan_progress signal")
            
            self.scanner.scan_finished.connect(self._on_scan_finished)
            logger.info("Connected scan_finished signal")
            
            self.scanner.scan_error.connect(self._on_scan_error)
            logger.info("Connected scan_error signal")
        except Exception as e:
            logger.error(f"Error connecting signals: {e}")
        
        # Setup UI
        self._setup_ui()
        
        # Initialize scan results
        self.scan_results = None
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create layout
        main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Add scan button
        scan_btn = QPushButton("Test Signal Connection")
        scan_btn.clicked.connect(self._test_signals)
        toolbar.addWidget(scan_btn)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
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
    
    def _test_signals(self):
        """Test if signals are working by manually emitting them"""
        logger.info("Testing signals...")
        self.status_bar.showMessage("Testing signals...")
        
        try:
            # Emit scan_started signal
            logger.info("Emitting scan_started signal")
            self.scanner.scan_started.emit("/test/path")
            
            # Emit scan_progress signal - note the parameter order matches signal definition
            # scan_progress = pyqtSignal(int, int, str)  # current, total, current_path
            logger.info("Emitting scan_progress signal")
            self.scanner.scan_progress.emit(50, 100, "/test/path/file.txt")
            
            # Create empty results dict
            results = {
                "root_info": type('obj', (object,), {'path': '/test/path'}),
                "total_size": 1000000,
                "total_files": 100,
                "total_dirs": 10,
                "scan_time": 1.5
            }
            
            # Emit scan_finished signal
            logger.info("Emitting scan_finished signal")
            self.scanner.scan_finished.emit(results)
            
            self.status_bar.showMessage("Signals test completed")
        except Exception as e:
            logger.error(f"Error testing signals: {e}")
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        logger.info(f"Scan started signal received: {path}")
        self.status_bar.showMessage(f"Scanning {path}...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        try:
            logger.info(f"Progress signal received: current={current}, total={total}, path={current_path}")
            
            # Convert parameters to integers if they're strings
            if isinstance(total, str):
                total = int(total)
            if isinstance(current, str):
                current = int(current)
                
            if total > 0:
                percent = int((current / total) * 100)
                self.progress_bar.setValue(percent)
            self.status_bar.showMessage(f"Scanning: {current_path}")
        except Exception as e:
            logger.error(f"Error in scan progress handler: {e}")
    
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.info("Scan finished signal received")
        self.status_bar.showMessage("Scan completed")
        self.progress_bar.setVisible(False)
        
        # Save scan results
        self.scan_results = results
        
        # We'll skip updating views with actual data in this test
        logger.info("Scan results received")
    
    def _on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.error(f"Scan error signal received: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")
        self.progress_bar.setVisible(False)

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    logger.info("Creating main window")
    window = TestMainWindow()
    logger.info("Showing main window")
    window.show()
    
    # Start event loop
    logger.info("Starting event loop")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 