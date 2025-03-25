#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Gradual initialization version to identify segmentation fault
"""

import sys
import os
import logging
import argparse
import time
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import QSettings, QTimer

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("gradual_init.log", mode="w")
    ]
)
logger = logging.getLogger("GradualInit")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

class GradualMainWindow(QMainWindow):
    """Main window that initializes components gradually"""
    
    def __init__(self):
        logger.debug("Starting main window initialization")
        super().__init__()
        self.setWindowTitle("Storage Stats - Gradual Init")
        self.resize(800, 600)
        
        # Create a central widget with buttons for initialization steps
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Add status label
        self.status_label = QLabel("Ready - Click buttons to initialize components")
        self.layout.addWidget(self.status_label)
        
        # Add initialization buttons
        self.add_init_button("1. Import Core Classes", self._import_core_classes)
        self.add_init_button("2. Create Scanner and Analyzer", self._create_scanner_analyzer)
        self.add_init_button("3. Import UI Views", self._import_ui_views)
        self.add_init_button("4. Create UI Components", self._create_ui_components)
        self.add_init_button("5. Connect Signals", self._connect_signals)
        self.add_init_button("6. Initialize Views", self._initialize_views)
        self.add_init_button("7. Test Signal Emissions", self._test_signals)
        
        logger.debug("Basic main window initialization complete")
    
    def add_init_button(self, text, callback):
        """Add an initialization button to the layout"""
        button = QPushButton(text)
        button.clicked.connect(callback)
        self.layout.addWidget(button)
    
    def _import_core_classes(self):
        """Import core classes"""
        try:
            logger.debug("Importing core classes...")
            self.status_label.setText("Importing core classes...")
            
            # Import core modules
            from src.core.scanner import DiskScanner
            from src.core.analyzer import DataAnalyzer
            
            logger.debug("Core classes imported successfully")
            self.status_label.setText("Core classes imported successfully")
            self._log_memory_usage("After importing core classes")
            return True
        except Exception as e:
            logger.error(f"Error importing core classes: {e}", exc_info=True)
            self.status_label.setText(f"Error importing core classes: {str(e)}")
            self._show_error(f"Error importing core classes: {str(e)}", traceback.format_exc())
            return False
    
    def _create_scanner_analyzer(self):
        """Create scanner and analyzer instances"""
        try:
            logger.debug("Creating scanner and analyzer...")
            self.status_label.setText("Creating scanner and analyzer...")
            
            # Import if not already imported
            if not self._import_core_classes():
                return False
            
            # Create instances
            from src.core.scanner import DiskScanner
            from src.core.analyzer import DataAnalyzer
            
            self.scanner = DiskScanner()
            self.analyzer = DataAnalyzer()
            
            logger.debug("Scanner and analyzer created successfully")
            self.status_label.setText("Scanner and analyzer created successfully")
            self._log_memory_usage("After creating scanner and analyzer")
            return True
        except Exception as e:
            logger.error(f"Error creating scanner and analyzer: {e}", exc_info=True)
            self.status_label.setText(f"Error creating scanner and analyzer: {str(e)}")
            self._show_error(f"Error creating scanner and analyzer: {str(e)}", traceback.format_exc())
            return False
    
    def _import_ui_views(self):
        """Import UI view classes"""
        try:
            logger.debug("Importing UI views...")
            self.status_label.setText("Importing UI views...")
            
            # Import UI components one by one and log after each
            
            logger.debug("Importing DashboardView...")
            from src.ui.dashboard_view import DashboardView
            logger.debug("DashboardView imported")
            self._log_memory_usage("After importing DashboardView")
            
            logger.debug("Importing FileBrowserView...")
            from src.ui.file_browser_view import FileBrowserView
            logger.debug("FileBrowserView imported")
            self._log_memory_usage("After importing FileBrowserView")
            
            logger.debug("Importing DuplicatesView...")
            from src.ui.duplicates_view import DuplicatesView
            logger.debug("DuplicatesView imported")
            self._log_memory_usage("After importing DuplicatesView")
            
            logger.debug("Importing FileTypesView...")
            from src.ui.file_types_view import FileTypesView
            logger.debug("FileTypesView imported")
            self._log_memory_usage("After importing FileTypesView")
            
            logger.debug("Importing RecommendationsView...")
            from src.ui.recommendations_view import RecommendationsView
            logger.debug("RecommendationsView imported")
            self._log_memory_usage("After importing RecommendationsView")
            
            logger.debug("All UI views imported successfully")
            self.status_label.setText("All UI views imported successfully")
            return True
        except Exception as e:
            logger.error(f"Error importing UI views: {e}", exc_info=True)
            self.status_label.setText(f"Error importing UI views: {str(e)}")
            self._show_error(f"Error importing UI views: {str(e)}", traceback.format_exc())
            return False
    
    def _create_ui_components(self):
        """Create UI components"""
        try:
            logger.debug("Creating UI components...")
            self.status_label.setText("Creating UI components...")
            
            # Import UI views if not already imported
            if not self._import_ui_views():
                return False
            
            # Create scanner and analyzer if not already created
            if not hasattr(self, 'scanner') or not hasattr(self, 'analyzer'):
                if not self._create_scanner_analyzer():
                    return False
            
            # Import UI views
            from src.ui.dashboard_view import DashboardView
            from src.ui.file_browser_view import FileBrowserView
            from src.ui.duplicates_view import DuplicatesView
            from src.ui.file_types_view import FileTypesView
            from src.ui.recommendations_view import RecommendationsView
            
            # Create tab widget
            from PyQt6.QtWidgets import QTabWidget
            self.tab_widget = QTabWidget()
            
            # Create views step by step with logging
            logger.debug("Creating DashboardView...")
            self.dashboard_view = DashboardView()
            logger.debug("DashboardView created")
            self._log_memory_usage("After creating DashboardView")
            
            logger.debug("Creating FileBrowserView...")
            self.file_browser_view = FileBrowserView()
            logger.debug("FileBrowserView created")
            self._log_memory_usage("After creating FileBrowserView")
            
            logger.debug("Creating DuplicatesView...")
            self.duplicates_view = DuplicatesView()
            logger.debug("DuplicatesView created")
            self._log_memory_usage("After creating DuplicatesView")
            
            logger.debug("Creating FileTypesView...")
            self.file_types_view = FileTypesView()
            logger.debug("FileTypesView created")
            self._log_memory_usage("After creating FileTypesView")
            
            logger.debug("Creating RecommendationsView...")
            self.recommendations_view = RecommendationsView()
            logger.debug("RecommendationsView created")
            self._log_memory_usage("After creating RecommendationsView")
            
            # Add tabs to tab widget
            logger.debug("Adding views to tab widget...")
            self.tab_widget.addTab(self.dashboard_view, "Dashboard")
            self.tab_widget.addTab(self.file_browser_view, "Files & Folders")
            self.tab_widget.addTab(self.duplicates_view, "Duplicates")
            self.tab_widget.addTab(self.file_types_view, "File Types")
            self.tab_widget.addTab(self.recommendations_view, "Recommendations")
            
            # Add tab widget to layout
            self.layout.addWidget(self.tab_widget)
            
            logger.debug("UI components created successfully")
            self.status_label.setText("UI components created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating UI components: {e}", exc_info=True)
            self.status_label.setText(f"Error creating UI components: {str(e)}")
            self._show_error(f"Error creating UI components: {str(e)}", traceback.format_exc())
            return False
    
    def _connect_signals(self):
        """Connect scanner signals to handlers"""
        try:
            logger.debug("Connecting signals...")
            self.status_label.setText("Connecting signals...")
            
            # Create scanner and analyzer if not already created
            if not hasattr(self, 'scanner') or not hasattr(self, 'analyzer'):
                if not self._create_scanner_analyzer():
                    return False
            
            # Connect signals with correct parameter order
            logger.debug("Connecting scan_started signal...")
            self.scanner.scan_started.connect(self._on_scan_started)
            
            logger.debug("Connecting scan_progress signal...")
            self.scanner.scan_progress.connect(self._on_scan_progress)
            
            logger.debug("Connecting scan_finished signal...")
            self.scanner.scan_finished.connect(self._on_scan_finished)
            
            logger.debug("Connecting scan_error signal...")
            self.scanner.scan_error.connect(self._on_scan_error)
            
            logger.debug("Signals connected successfully")
            self.status_label.setText("Signals connected successfully")
            return True
        except Exception as e:
            logger.error(f"Error connecting signals: {e}", exc_info=True)
            self.status_label.setText(f"Error connecting signals: {str(e)}")
            self._show_error(f"Error connecting signals: {str(e)}", traceback.format_exc())
            return False
    
    def _initialize_views(self):
        """Initialize views with stub data"""
        try:
            logger.debug("Initializing views...")
            self.status_label.setText("Initializing views...")
            
            # Create UI components if not already created
            if not hasattr(self, 'dashboard_view'):
                if not self._create_ui_components():
                    return False
            
            # Create empty results dictionary
            mock_results = {
                "total_size": 1000000,
                "total_files": 100,
                "total_dirs": 10,
                "root_info": None
            }
            
            # Initialize views with mock data
            logger.debug("Initializing DashboardView...")
            if hasattr(self.dashboard_view, 'update_view'):
                self.dashboard_view.update_view(mock_results, self.analyzer)
            
            logger.debug("Initializing FileBrowserView...")
            if hasattr(self.file_browser_view, 'update_view'):
                self.file_browser_view.update_view(mock_results, self.analyzer)
            
            logger.debug("Initializing DuplicatesView...")
            if hasattr(self.duplicates_view, 'update_view'):
                self.duplicates_view.update_view(mock_results, self.analyzer)
            
            logger.debug("Initializing FileTypesView...")
            if hasattr(self.file_types_view, 'update_view'):
                self.file_types_view.update_view(mock_results, self.analyzer)
            
            logger.debug("Initializing RecommendationsView...")
            if hasattr(self.recommendations_view, 'update_view'):
                self.recommendations_view.update_view(mock_results, self.analyzer)
            
            logger.debug("Views initialized successfully")
            self.status_label.setText("Views initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing views: {e}", exc_info=True)
            self.status_label.setText(f"Error initializing views: {str(e)}")
            self._show_error(f"Error initializing views: {str(e)}", traceback.format_exc())
            return False
    
    def _test_signals(self):
        """Test signal emissions"""
        try:
            logger.debug("Testing signal emissions...")
            self.status_label.setText("Testing signal emissions...")
            
            # Connect signals if not already connected
            if not self._connect_signals():
                return False
            
            # Create progress bar if it doesn't exist
            if not hasattr(self, 'progress_bar'):
                from PyQt6.QtWidgets import QProgressBar
                self.progress_bar = QProgressBar()
                self.layout.addWidget(self.progress_bar)
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                self.progress_bar.setVisible(True)
            
            # Emit scan_started signal
            logger.debug("Emitting scan_started signal...")
            self.scanner.scan_started.emit("/test/path")
            
            # Emit scan_progress signals
            logger.debug("Emitting scan_progress signals...")
            for i in range(0, 101, 20):
                logger.debug(f"Emitting progress {i}%...")
                self.scanner.scan_progress.emit(i, 100, f"/test/path/file_{i}.txt")
                QApplication.processEvents()  # Process events to update UI
                time.sleep(0.2)  # Short delay to see progress
            
            # Emit scan_finished signal
            logger.debug("Emitting scan_finished signal...")
            self.scanner.scan_finished.emit({
                "total_size": 1000000,
                "total_files": 100,
                "total_dirs": 10,
                "scan_time": 1.5,
                "root_info": type('obj', (object,), {'path': '/test/path'})
            })
            
            logger.debug("Signal emissions tested successfully")
            self.status_label.setText("Signal emissions tested successfully")
            return True
        except Exception as e:
            logger.error(f"Error testing signal emissions: {e}", exc_info=True)
            self.status_label.setText(f"Error testing signal emissions: {str(e)}")
            self._show_error(f"Error testing signal emissions: {str(e)}", traceback.format_exc())
            return False
    
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        logger.debug(f"_on_scan_started called with path={path}")
        self.status_label.setText(f"Scan started: {path}")
        
        # Show progress bar if it exists
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal with CORRECT parameter order"""
        logger.debug(f"_on_scan_progress called with current={current}, total={total}, current_path={current_path}")
        
        try:
            # Convert parameters to integers if they're strings
            if isinstance(total, str):
                total = int(total)
            if isinstance(current, str):
                current = int(current)
            
            # Update progress bar if it exists
            if hasattr(self, 'progress_bar') and total > 0:
                percent = int((current / total) * 100)
                self.progress_bar.setValue(percent)
            
            self.status_label.setText(f"Scanning: {current_path}")
        except Exception as e:
            logger.error(f"Error in scan progress handler: {e}", exc_info=True)
            # Don't crash on progress updates
    
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.debug(f"_on_scan_finished called with results of type {type(results)}")
        self.status_label.setText("Scan completed")
        
        # Hide progress bar if it exists
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
    
    def _on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.debug(f"_on_scan_error called with error_message={error_message}")
        self.status_label.setText(f"Error: {error_message}")
        
        # Hide progress bar if it exists
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
    
    def _show_error(self, message, details):
        """Show error dialog with detailed information"""
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.setDetailedText(details)
        error_box.exec()
    
    def _log_memory_usage(self, description):
        """Log memory usage for debugging"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            logger.debug(f"Memory usage ({description}): {memory_info.rss / 1024 / 1024:.2f} MB")
        except ImportError:
            logger.debug(f"Memory usage logging skipped - psutil not available")
        except Exception as e:
            logger.debug(f"Error logging memory usage: {e}")

def main():
    """Application entry point"""
    # Configure logging
    logging.info("Starting gradual initialization application")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Storage Stats - Gradual Init")
    
    # Create main window
    logging.info("Creating main window")
    main_window = GradualMainWindow()
    logging.info("Showing main window")
    main_window.show()
    
    # Start application event loop
    logging.info("Starting application event loop")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1) 