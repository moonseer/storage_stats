#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer for macOS.

This application allows users to analyze disk usage on their computer, 
identifying large files, duplicate files, and providing recommendations
for freeing up space. It features a modern UI built with PyQt6 for 
visualizing storage data.

Typical usage:
    $ python3 main.py
    $ python3 main.py --path /path/to/scan
    $ python3 main.py --debug
"""

import sys
import os
import logging
import argparse

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import application components
from src.ui.main_window import MainWindow
from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer

def configure_logging(log_level=logging.INFO):
    """
    Configure application logging with appropriate handlers and formatting.
    
    Args:
        log_level (int): The logging level to use (e.g., logging.DEBUG, 
                         logging.INFO). Defaults to logging.INFO.
    
    Returns:
        None
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("storage_stats.log", mode="w")
        ]
    )
    
    # Configure module loggers
    logging.getLogger("StorageStats").setLevel(log_level)

class EnhancedMainWindow(MainWindow):
    """
    Enhanced version of the MainWindow with improved signal handling.
    
    This subclass ensures that all signals are correctly connected and
    components are initialized in the right order, preventing segmentation
    faults and other issues that can occur with PyQt signal/slot connections.
    """
    
    def __init__(self):
        """Initialize the EnhancedMainWindow with extra safety measures."""
        logging.info("Initializing EnhancedMainWindow")
        
        # Call parent constructor
        super().__init__()
        
        # Add extra safety measures for signal handling
        self._ensure_signals_connected()
        
    def _ensure_signals_connected(self):
        """
        Ensure that all scanner signals are correctly connected to their slots.
        
        This method reconnects all signal/slot connections for the scanner
        to prevent parameter mismatches and ensure proper event handling.
        """
        logging.info("Ensuring scanner signals are correctly connected")
        
        # Get scanner instance
        scanner = self.scanner
        
        # Disconnect any existing connections to avoid duplicates
        try:
            scanner.scan_started.disconnect()
            scanner.scan_progress.disconnect()
            scanner.scan_finished.disconnect()
            scanner.scan_error.disconnect()
        except Exception:
            # It's okay if they weren't connected
            pass
        
        # Reconnect signals with the correct parameter order
        try:
            scanner.scan_started.connect(self._on_scan_started)
            scanner.scan_progress.connect(self._on_scan_progress)
            scanner.scan_finished.connect(self._on_scan_finished)
            scanner.scan_error.connect(self._on_scan_error)
            logging.debug("Scanner signals reconnected successfully")
        except Exception as e:
            logging.error(f"Error reconnecting scanner signals: {e}", exc_info=True)

def parse_args():
    """
    Parse command line arguments for the application.
    
    Returns:
        argparse.Namespace: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Storage Stats - Disk Space Analyzer")
    parser.add_argument("--path", help="Path to scan")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def main():
    """
    Main entry point for the Storage Stats application.
    
    This function initializes the application, configures logging,
    creates the main window, and starts the event loop.
    
    Returns:
        int: The application exit code.
    """
    # Parse command line arguments
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    configure_logging(log_level)
    
    # Log start
    logging.info(f"Starting Storage Stats with Python {sys.version}")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Storage Stats")
    
    # Create main window with enhanced implementation
    logging.info("Creating main window with enhanced implementation")
    window = EnhancedMainWindow()
    window.show()
    
    # Start automatic scan if path provided
    if args.path:
        logging.info(f"Starting automatic scan of {args.path}")
        QTimer.singleShot(500, lambda: window.start_scan(args.path))
    
    # Start application event loop
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.critical(f"Unhandled exception: {e}", exc_info=True) 