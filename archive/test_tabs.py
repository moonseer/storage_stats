#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test application with tab widget to debug segmentation fault
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QTabWidget, QPushButton, QFileDialog, QStatusBar, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer

class TabTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create button to test file dialog
        scan_button = QPushButton("Open File Dialog")
        scan_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(scan_button)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tab pages
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        
        # Set up layouts for tabs
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("This is tab 1"))
        
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("This is tab 2"))
        
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("This is tab 3"))
        
        # Add tabs
        self.tab_widget.addTab(tab1, "Dashboard")
        self.tab_widget.addTab(tab2, "Files & Folders")
        self.tab_widget.addTab(tab3, "Duplicates")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Create simulated scan button with progress
        simulate_button = QPushButton("Simulate Scan")
        simulate_button.clicked.connect(self.simulate_scan)
        main_layout.addWidget(simulate_button)

    def on_tab_changed(self, index):
        """Handle tab change signal"""
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Switched to {tab_name} tab")
    
    def open_file_dialog(self):
        """Test file dialog"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.status_bar.showMessage(f"Selected: {directory}")
    
    def simulate_scan(self):
        """Simulate a scan with progress updates"""
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Using QTimer to simulate progress
        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)  # Update every 100ms
    
    def update_progress(self):
        """Update progress bar"""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.timer.stop()
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Scan completed")
        else:
            self.status_bar.showMessage(f"Scanning... {self.progress_value}%")

def main():
    app = QApplication(sys.argv)
    window = TabTest()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 