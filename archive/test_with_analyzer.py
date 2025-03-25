#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test main window with real scanner and analyzer
"""

import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
    QTabWidget, QPushButton, QFileDialog, QStatusBar, QProgressBar,
    QHBoxLayout, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QSettings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestApp")

# Create placeholder classes
class PlaceholderView(QWidget):
    """Placeholder for custom views"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"This is a placeholder for {name}"))
        
        # Add method that would be called by MainWindow
        self.update_view = lambda results, analyzer: None

class TestMainWindow(QMainWindow):
    """Test main window with real scanner and analyzer"""
    
    def __init__(self):
        super().__init__()
        logger.info("Initializing TestMainWindow")
        
        # Import real scanner and analyzer
        try:
            from src.core.scanner import DiskScanner
            self.scanner = DiskScanner()  # Using the real scanner
            logger.info("Successfully imported DiskScanner")
        except Exception as e:
            logger.error(f"Error importing DiskScanner: {e}")
            QMessageBox.critical(self, "Import Error", f"Failed to import DiskScanner: {e}")
            from mock_classes import MockScanner
            self.scanner = MockScanner()
        
        try:
            from src.core.analyzer import DataAnalyzer
            self.analyzer = DataAnalyzer()  # Using the real analyzer
            logger.info("Successfully imported DataAnalyzer")
        except Exception as e:
            logger.error(f"Error importing DataAnalyzer: {e}")
            QMessageBox.critical(self, "Import Error", f"Failed to import DataAnalyzer: {e}")
            from mock_classes import MockAnalyzer
            self.analyzer = MockAnalyzer()
        
        # Initialize other instance variables
        self.current_scan_path = None
        self.scan_results = None
        self.settings = QSettings("StorageStats", "TestApp")
        self.scan_in_progress = False
        
        # Set up window properties
        self.setWindowTitle("Storage Stats - Test with Scanner & Analyzer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create UI components
        self._create_status_bar()
        self._create_central_widget()
        
        # Connect scanner signals
        self.scanner.scan_started.connect(self._on_scan_started)
        self.scanner.scan_progress.connect(self._on_scan_progress)
        self.scanner.scan_finished.connect(self._on_scan_finished)
        self.scanner.scan_error.connect(self._on_scan_error)
        
        logger.info("TestMainWindow initialization complete")
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Set initial status
        self.status_bar.showMessage("Ready")
    
    def _create_central_widget(self):
        """Create the central widget with tab layout"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add scan button
        scan_layout = QHBoxLayout()
        scan_button = QPushButton("Scan Directory")
        scan_button.clicked.connect(self._on_scan_action)
        scan_layout.addWidget(scan_button)
        
        # Add stop button
        stop_button = QPushButton("Stop Scan")
        stop_button.clicked.connect(self._on_stop_scan)
        stop_button.setEnabled(False)
        self.stop_button = stop_button
        scan_layout.addWidget(stop_button)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        scan_layout.addWidget(spacer)
        
        main_layout.addLayout(scan_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create placeholders for all the view components
        # We're using actual imports for each one to see if they cause problems
        try:
            # Try importing the real DashboardView
            from src.ui.dashboard_view import DashboardView
            self.dashboard_view = DashboardView()
            logger.info("Successfully imported DashboardView")
        except Exception as e:
            logger.error(f"Error importing DashboardView: {e}")
            self.dashboard_view = PlaceholderView("Dashboard")
        
        # Use placeholder views for the rest
        self.file_browser_view = PlaceholderView("Files & Folders")
        self.duplicates_view = PlaceholderView("Duplicates")
        self.file_types_view = PlaceholderView("File Types")
        self.recommendations_view = PlaceholderView("Recommendations")
        
        # Add tabs
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        self.tab_widget.addTab(self.file_browser_view, "Files & Folders")
        self.tab_widget.addTab(self.duplicates_view, "Duplicates")
        self.tab_widget.addTab(self.file_types_view, "File Types")
        self.tab_widget.addTab(self.recommendations_view, "Recommendations")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_scan_action(self):
        """Handle scan button click"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Scan",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.current_scan_path = directory
            self.scan_in_progress = True
            
            # Configure scanner
            config = {}  # Add any configuration needed
            self.scanner.configure(config)
            
            # Start scan
            logger.info(f"Starting scan of {directory}")
            self.scanner.scan(directory)
            self.status_bar.showMessage(f"Scanning {directory}...")
            self.stop_button.setEnabled(True)
    
    def _on_stop_scan(self):
        """Handle stop scan button click"""
        if hasattr(self.scanner, '_stop_requested'):
            self.scanner._stop_requested = True
            self.status_bar.showMessage("Stopping scan...")
            logger.info("Stopping scan...")
    
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        logger.info(f"Scan started: {path}")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        try:
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
            # Don't crash on progress update errors
    
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.info("Scan finished")
        self.progress_bar.setVisible(False)
        self.scan_in_progress = False
        self.scan_results = results
        self.stop_button.setEnabled(False)
        
        # Update the current tab with results
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'update_view'):
            current_tab.update_view(results, self.analyzer)
        
        # Show message in status bar
        if results:
            total_size = results.get("total_size", 0)
            total_files = results.get("total_files", 0)
            from src.utils.helpers import human_readable_size
            self.status_bar.showMessage(f"Scan completed: {human_readable_size(total_size)}, {total_files:,} files")
        else:
            self.status_bar.showMessage("Scan stopped")
    
    def _on_scan_error(self, error_msg):
        """Handle scan error signal"""
        logger.error(f"Scan error: {error_msg}")
        self.progress_bar.setVisible(False)
        self.scan_in_progress = False
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Scan failed")
    
    def _on_tab_changed(self, index):
        """Handle tab change signal"""
        tab_name = self.tab_widget.tabText(index)
        logger.info(f"Tab changed to: {tab_name}")
        
        # Update the new tab with scan results if available
        if self.scan_results:
            tab_widget = self.tab_widget.widget(index)
            if hasattr(tab_widget, 'update_view'):
                tab_widget.update_view(self.scan_results, self.analyzer)
        
        self.status_bar.showMessage(f"Viewing {tab_name}")

def main():
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 