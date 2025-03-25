#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core modules test application
"""

import sys
import os
import logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import core modules
from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CoreTest")

class CoreTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Core Modules Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create scanner and analyzer
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("Test for core modules DiskScanner and DataAnalyzer")
        layout.addWidget(label)
        
        # Add buttons to test scanner and analyzer
        scanner_btn = QPushButton("Create Scanner")
        scanner_btn.clicked.connect(self.test_scanner)
        layout.addWidget(scanner_btn)
        
        analyzer_btn = QPushButton("Create Analyzer")
        analyzer_btn.clicked.connect(self.test_analyzer)
        layout.addWidget(analyzer_btn)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def test_scanner(self):
        """Test creating and using the scanner"""
        try:
            logger.info("Testing scanner...")
            self.status_label.setText(f"Scanner version: {self.scanner.__class__.__name__}")
            logger.info("Scanner test successful")
        except Exception as e:
            logger.error(f"Scanner error: {str(e)}")
            self.status_label.setText(f"Scanner error: {str(e)}")
    
    def test_analyzer(self):
        """Test creating and using the analyzer"""
        try:
            logger.info("Testing analyzer...")
            self.status_label.setText(f"Analyzer version: {self.analyzer.__class__.__name__}")
            logger.info("Analyzer test successful")
        except Exception as e:
            logger.error(f"Analyzer error: {str(e)}")
            self.status_label.setText(f"Analyzer error: {str(e)}")

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    window = CoreTestWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 