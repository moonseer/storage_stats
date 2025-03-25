#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test application to debug segmentation fault
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MinimalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("This is a minimal test application")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    window = MinimalWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 