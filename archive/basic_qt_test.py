#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ultra-minimal PyQt test application
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal PyQt Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("This is a minimal PyQt test application")
        layout.addWidget(label)

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show window
    window = MinimalWindow()
    window.show()
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 