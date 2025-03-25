#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bare minimum test application to isolate segmentation fault
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("BareMinimum")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QObject

# Create a simple window that doesn't import any project modules
class SimpleWindow(QMainWindow):
    def __init__(self):
        logger.debug("Initializing SimpleWindow")
        super().__init__()
        self.setWindowTitle("Bare Minimum Test")
        self.resize(400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add label
        label = QLabel("This is a bare minimum test application")
        layout.addWidget(label)
        
        # Add button for next step
        button1 = QPushButton("Step 1: Import DiskScanner")
        button1.clicked.connect(self.step1_import_scanner)
        layout.addWidget(button1)
        
        # Add button for next step
        button2 = QPushButton("Step 2: Create DiskScanner")
        button2.clicked.connect(self.step2_create_scanner)
        layout.addWidget(button2)
        
        # Add button for next step
        button3 = QPushButton("Step 3: Connect Signals")
        button3.clicked.connect(self.step3_connect_signals)
        layout.addWidget(button3)
        
        # Add button for next step
        button4 = QPushButton("Step 4: Test Signals")
        button4.clicked.connect(self.step4_test_signals)
        layout.addWidget(button4)
        
        # Add status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        logger.debug("SimpleWindow initialized")
    
    def step1_import_scanner(self):
        """Import scanner module step by step"""
        try:
            logger.debug("Importing DiskScanner...")
            from src.core.scanner import DiskScanner
            logger.debug("DiskScanner imported successfully")
            self.status_label.setText("DiskScanner imported successfully")
        except Exception as e:
            logger.error(f"Error importing DiskScanner: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def step2_create_scanner(self):
        """Create scanner instance"""
        try:
            logger.debug("Creating DiskScanner instance...")
            from src.core.scanner import DiskScanner
            self.scanner = DiskScanner()
            logger.debug("DiskScanner instance created")
            self.status_label.setText("DiskScanner instance created")
        except Exception as e:
            logger.error(f"Error creating DiskScanner: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def step3_connect_signals(self):
        """Connect scanner signals"""
        try:
            logger.debug("Connecting scanner signals...")
            if not hasattr(self, 'scanner'):
                from src.core.scanner import DiskScanner
                self.scanner = DiskScanner()
            
            # Connect signals
            self.scanner.scan_started.connect(self.on_scan_started)
            self.scanner.scan_progress.connect(self.on_scan_progress)
            self.scanner.scan_finished.connect(self.on_scan_finished)
            self.scanner.scan_error.connect(self.on_scan_error)
            
            logger.debug("Scanner signals connected")
            self.status_label.setText("Scanner signals connected")
        except Exception as e:
            logger.error(f"Error connecting signals: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def step4_test_signals(self):
        """Test emitting scanner signals"""
        try:
            logger.debug("Testing scanner signals...")
            if not hasattr(self, 'scanner'):
                self.status_label.setText("Error: Scanner not created")
                return
            
            # Emit scan_started
            self.scanner.scan_started.emit("/test/path")
            
            # Emit scan_progress with correct parameter order
            self.scanner.scan_progress.emit(50, 100, "/test/path/file.txt")
            
            # Emit scan_finished
            self.scanner.scan_finished.emit({"total_size": 1000000, "total_files": 100})
            
            logger.debug("Signals emitted successfully")
            self.status_label.setText("Signals emitted successfully")
        except Exception as e:
            logger.error(f"Error emitting signals: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def on_scan_started(self, path):
        """Handle scan started signal"""
        logger.debug(f"on_scan_started called with path={path}")
        self.status_label.setText(f"Scan started: {path}")
    
    def on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        logger.debug(f"on_scan_progress called with current={current}, total={total}, current_path={current_path}")
        try:
            # Convert parameters to integers if they're strings
            if isinstance(current, str):
                current = int(current)
            if isinstance(total, str):
                total = int(total)
            
            percent = int((current / total) * 100) if total > 0 else 0
            self.status_label.setText(f"Progress: {percent}% - {current_path}")
        except Exception as e:
            logger.error(f"Error handling progress: {e}", exc_info=True)
            self.status_label.setText(f"Progress error: {str(e)}")
    
    def on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.debug(f"on_scan_finished called with results={results}")
        self.status_label.setText("Scan finished")
    
    def on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.debug(f"on_scan_error called with error_message={error_message}")
        self.status_label.setText(f"Error: {error_message}")

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 