#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Simplified Debug Version
"""

import sys
import os
import logging
import traceback

# Set up verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("debug_log.txt", mode="w")
    ]
)

logger = logging.getLogger("SimpleDebug")
logger.setLevel(logging.DEBUG)

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

# Import the main window class
from src.ui.main_window import MainWindow
from src.core.scanner import DiskScanner

# Subclass DiskScanner to add logging
class DebugDiskScanner(DiskScanner):
    def __init__(self, max_threads=4):
        super().__init__(max_threads)
        # Save original emit methods
        self._original_scan_started_emit = self.scan_started.emit
        self._original_scan_progress_emit = self.scan_progress.emit
        self._original_scan_finished_emit = self.scan_finished.emit
        self._original_scan_error_emit = self.scan_error.emit
        
        # Override emit methods with debug versions
        def debug_scan_started_emit(path):
            logger.debug(f"Emitting scan_started({path}) with type {type(path)}")
            return self._original_scan_started_emit(path)
            
        def debug_scan_progress_emit(current, total, current_path):
            logger.debug(f"Emitting scan_progress({current}, {total}, {current_path}) with types {type(current)}, {type(total)}, {type(current_path)}")
            return self._original_scan_progress_emit(current, total, current_path)
            
        def debug_scan_finished_emit(results):
            logger.debug(f"Emitting scan_finished(results) with type {type(results)}")
            return self._original_scan_finished_emit(results)
            
        def debug_scan_error_emit(error_message):
            logger.debug(f"Emitting scan_error({error_message}) with type {type(error_message)}")
            return self._original_scan_error_emit(error_message)
        
        # Apply debug methods
        self.scan_started.emit = debug_scan_started_emit
        self.scan_progress.emit = debug_scan_progress_emit
        self.scan_finished.emit = debug_scan_finished_emit
        self.scan_error.emit = debug_scan_error_emit
    
    def scan(self, path, is_blocking=False, resume=False):
        """Override scan method to add logging"""
        logger.debug(f"DebugDiskScanner.scan called with path={path}, is_blocking={is_blocking}, resume={resume}")
        return super().scan(path, is_blocking, resume)

# Subclass MainWindow to add logging
class DebugMainWindow(MainWindow):
    def __init__(self):
        logger.debug("Initializing DebugMainWindow")
        # Override scanner creation
        super().__init__()
        # Replace scanner with debug version
        self.scanner = DebugDiskScanner()
        
        # Connect scanner signals with extra logging
        self.scanner.scan_started.connect(self._debug_on_scan_started)
        self.scanner.scan_progress.connect(self._debug_on_scan_progress)
        self.scanner.scan_finished.connect(self._debug_on_scan_finished)
        self.scanner.scan_error.connect(self._debug_on_scan_error)
        
        logger.debug("DebugMainWindow initialized")
    
    def _debug_on_scan_started(self, path):
        """Wrapper for _on_scan_started with logging"""
        logger.debug(f"_on_scan_started called with path={path} of type {type(path)}")
        try:
            return self._on_scan_started(path)
        except Exception as e:
            logger.error(f"Exception in _on_scan_started: {e}", exc_info=True)
            raise
    
    def _debug_on_scan_progress(self, current, total, current_path):
        """Wrapper for _on_scan_progress with logging"""
        logger.debug(f"_on_scan_progress called with current={current}({type(current)}), total={total}({type(total)}), current_path={current_path}({type(current_path)})")
        try:
            return self._on_scan_progress(current, total, current_path)
        except Exception as e:
            logger.error(f"Exception in _on_scan_progress: {e}", exc_info=True)
            raise
    
    def _debug_on_scan_finished(self, results):
        """Wrapper for _on_scan_finished with logging"""
        logger.debug(f"_on_scan_finished called with results of type {type(results)}")
        try:
            return self._on_scan_finished(results)
        except Exception as e:
            logger.error(f"Exception in _on_scan_finished: {e}", exc_info=True)
            raise
    
    def _debug_on_scan_error(self, error_message):
        """Wrapper for _on_scan_error with logging"""
        logger.debug(f"_on_scan_error called with error_message={error_message} of type {type(error_message)}")
        try:
            return self._on_scan_error(error_message)
        except Exception as e:
            logger.error(f"Exception in _on_scan_error: {e}", exc_info=True)
            raise

def main():
    """Debug application entry point"""
    logger.info("Starting simple debug version of Storage Stats")
    
    # Print system information
    import platform
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    
    # Import PyQt6 modules
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QT_VERSION_STR
    logger.info(f"Qt version: {QT_VERSION_STR}")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Storage Stats [DEBUG]")
    
    # Add exception hook for unhandled exceptions
    def exception_hook(exc_type, exc_value, exc_traceback):
        logger.critical("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_hook
    
    # Create main window
    logger.info("Creating main window")
    main_window = DebugMainWindow()
    logger.info("Showing main window")
    main_window.show()
    
    # Start application event loop
    logger.info("Starting application event loop")
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True) 