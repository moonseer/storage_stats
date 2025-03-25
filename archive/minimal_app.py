#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal test application to debug segmentation fault
"""

import sys
import os
import logging

from PyQt6.QtWidgets import QApplication

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import application modules
from src.ui.main_window import MainWindow

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MinimalTest")

def main():
    """Application entry point"""
    logger.info("Starting minimal test application")
    
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("StorageStats-Test")
        
        # Create main window without parameters
        main_window = MainWindow()
        main_window.show()
        
        # Start application event loop
        return app.exec()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 