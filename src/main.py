#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Main application entry point
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("StorageStats")

# Import local modules
try:
    from ui.main_window import MainWindow
    from core.scanner import DiskScanner
    from core.analyzer import DataAnalyzer
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def main():
    """Main application entry point"""
    logger.info("Starting Storage Stats application")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Storage Stats")
    app.setApplicationVersion("0.1.0")
    
    # Set application style and icon
    app_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "resources", "icon.png")
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 