#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer Debug Version
Enhanced logging for troubleshooting segmentation faults
"""

import sys
import os
import logging
import traceback
import signal
import inspect
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject, QMetaObject

# Set up extremely verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("debug_log.txt", mode="w")
    ]
)

logger = logging.getLogger("DebugMain")
logger.setLevel(logging.DEBUG)

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Monkey patch pyqtSignal.connect to log connections
original_connect = pyqtSignal.connect

def debug_connect(self, slot):
    logger.debug(f"SIGNAL CONNECT: {self} -> {slot.__qualname__ if hasattr(slot, '__qualname__') else str(slot)}")
    return original_connect(self, slot)

pyqtSignal.connect = debug_connect

# Monkey patch QMetaObject.invokeMethod to log signal emissions
original_invoke = QMetaObject.invokeMethod

def debug_invoke(obj, *args, **kwargs):
    logger.debug(f"SIGNAL INVOKE: {obj} with args={args}, kwargs={kwargs}")
    return original_invoke(obj, *args, **kwargs)

QMetaObject.invokeMethod = debug_invoke

# Import wrapped scanner class
from src.core.scanner import DiskScanner

# Add debug logging to DiskScanner
original_emit = pyqtSignal.emit

def debug_emit(self, *args):
    # Log signal emissions with parameter types
    signal_name = getattr(self, 'signal', str(self))
    param_types = [f"{arg}({type(arg).__name__})" for arg in args]
    logger.debug(f"SIGNAL EMIT: {signal_name} with args: {param_types}")
    return original_emit(self, *args)

for attr_name in dir(DiskScanner):
    attr = getattr(DiskScanner, attr_name)
    if isinstance(attr, pyqtSignal):
        # Set a descriptive name for better logging
        attr.signal = f"DiskScanner.{attr_name}"
        # Monkey patch this specific signal's emit method
        attr.emit = debug_emit.__get__(attr)

# Add stack trace info to key methods
original_scan = DiskScanner.scan

def debug_scan(self, *args, **kwargs):
    logger.debug(f"ENTERING: DiskScanner.scan with args={args}, kwargs={kwargs}")
    logger.debug(f"STACK: {traceback.format_stack()}")
    return original_scan(self, *args, **kwargs)

DiskScanner.scan = debug_scan

# Import the main window with debugging enhancements
from src.ui.main_window import MainWindow

# Add debug logging to main window signal handlers
original_on_scan_progress = MainWindow._on_scan_progress

def debug_on_scan_progress(self, *args, **kwargs):
    logger.debug(f"HANDLER: MainWindow._on_scan_progress called with args={[f'{arg}({type(arg).__name__})' for arg in args]}, kwargs={kwargs}")
    logger.debug(f"STACK: {traceback.format_stack()[-5:]}")
    return original_on_scan_progress(self, *args, **kwargs)

MainWindow._on_scan_progress = debug_on_scan_progress

# Add signal handler for segmentation faults
def handle_segfault(signum, frame):
    logger.critical("SEGMENTATION FAULT DETECTED!")
    logger.critical(f"Signal: {signum}")
    logger.critical(f"Frame: {frame}")
    logger.critical(f"Stack trace:\n{''.join(traceback.format_stack())}")
    sys.exit(1)

signal.signal(signal.SIGSEGV, handle_segfault)

def main():
    """Debug application entry point"""
    logger.info("Starting debug version of Storage Stats")
    
    # Print system information
    import platform
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    
    # Log PyQt version
    from PyQt6.QtCore import QT_VERSION_STR
    logger.info(f"Qt version: {QT_VERSION_STR}")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Storage Stats [DEBUG]")
    
    # Create main window
    logger.info("Creating main window")
    main_window = MainWindow()
    logger.info("Showing main window")
    main_window.show()
    
    # Add exception hook for unhandled exceptions
    def exception_hook(exc_type, exc_value, exc_traceback):
        logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_hook
    
    # Start application event loop
    logger.info("Starting application event loop")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True) 