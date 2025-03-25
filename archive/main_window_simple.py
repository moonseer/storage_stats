#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified MainWindow test to isolate segmentation fault issues
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MainWindowSimple")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, 
    QStatusBar, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QObject

# Import just the scanner class, not the whole MainWindow
from src.core.scanner import DiskScanner

class SimplifiedMainWindow(QMainWindow):
    """Simplified version of MainWindow focusing on just the signal handling"""
    
    def __init__(self):
        logger.debug("Initializing SimplifiedMainWindow")
        super().__init__()
        self.setWindowTitle("Simplified Main Window")
        self.resize(800, 600)
        
        # Create scanner
        logger.debug("Creating DiskScanner")
        self.scanner = DiskScanner()
        
        # Create UI components
        self._create_ui()
        
        # Connect signals - NOTE: Connect them after UI is created
        logger.debug("Connecting scanner signals")
        self.scanner.scan_started.connect(self._on_scan_started)
        self.scanner.scan_progress.connect(self._on_scan_progress)
        self.scanner.scan_finished.connect(self._on_scan_finished)
        self.scanner.scan_error.connect(self._on_scan_error)
        
        logger.debug("SimplifiedMainWindow initialized")
    
    def _create_ui(self):
        """Create the user interface"""
        logger.debug("Creating UI")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        main_layout = QVBoxLayout(central_widget)
        
        # Add test buttons
        test_button = QPushButton("Test Scanner Signals")
        test_button.clicked.connect(self._test_signals)
        main_layout.addWidget(test_button)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        logger.debug("UI created")
    
    def _test_signals(self):
        """Test scanner signals by manually emitting them"""
        logger.debug("Testing scanner signals")
        
        try:
            # Emit scan_started
            self.scanner.scan_started.emit("/test/path")
            
            # Emit scan_progress
            for i in range(0, 101, 10):
                self.scanner.scan_progress.emit(i, 100, f"/test/path/file_{i}.txt")
            
            # Emit scan_finished
            self.scanner.scan_finished.emit({
                "total_size": 1000000,
                "total_files": 100,
                "total_dirs": 10,
                "scan_time": 1.5
            })
            
            logger.debug("All signals emitted successfully")
            
        except Exception as e:
            logger.error(f"Error testing signals: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        logger.debug(f"_on_scan_started called with path={path}")
        self.status_bar.showMessage(f"Scanning {path}...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        logger.debug(f"_on_scan_progress: current={current}({type(current)}), " 
                   f"total={total}({type(total)}), current_path={current_path}({type(current_path)})")
        
        try:
            # Convert parameters to integers if they're strings
            if isinstance(total, str):
                logger.debug(f"Converting total '{total}' to int")
                total = int(total)
            if isinstance(current, str):
                logger.debug(f"Converting current '{current}' to int")
                current = int(current)
            
            # Calculate percentage
            if total > 0:
                percent = int((current / total) * 100)
                logger.debug(f"Progress percentage: {percent}%")
                self.progress_bar.setValue(percent)
            
            self.status_bar.showMessage(f"Scanning: {current_path}")
            
        except Exception as e:
            logger.error(f"Error in scan progress handler: {e}", exc_info=True)
            # Don't crash on progress updates
    
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.debug(f"_on_scan_finished called with results={type(results)}")
        self.status_bar.showMessage("Scan completed")
        self.progress_bar.setVisible(False)
    
    def _on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.debug(f"_on_scan_error called with error_message={error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")
        self.progress_bar.setVisible(False)

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = SimplifiedMainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 