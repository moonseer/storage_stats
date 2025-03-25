#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal test - minimalist test to check if signal parameter order issues are causing the segfault
"""

import sys
import os
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SignalTest")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, QObject, Qt

class SignalEmitter(QObject):
    """Simple test class with same signal signature as DiskScanner"""
    
    # Use identical signal definitions as DiskScanner
    scan_started = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int, str)  # current, total, current_path
    scan_finished = pyqtSignal(dict)
    scan_error = pyqtSignal(str)

class TestWindow(QMainWindow):
    """Test window for signal parameter handling"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Test")
        self.resize(400, 200)
        
        # Create signal emitter
        self.signal_emitter = SignalEmitter()
        
        # Connect signals
        self.signal_emitter.scan_started.connect(self._on_scan_started)
        self.signal_emitter.scan_progress.connect(self._on_scan_progress)
        self.signal_emitter.scan_finished.connect(self._on_scan_finished)
        self.signal_emitter.scan_error.connect(self._on_scan_error)
        
        # Create UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add emit button
        emit_button = QPushButton("Emit Signals")
        emit_button.clicked.connect(self._emit_signals)
        layout.addWidget(emit_button)
        
        # Add status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def _emit_signals(self):
        """Emit test signals in sequence"""
        try:
            # Log and emit scan_started
            logger.info("Emitting scan_started")
            self.signal_emitter.scan_started.emit("/test/path")
            
            # Log and emit scan_progress with parameters in debug-friendly format 
            logger.info("Emitting scan_progress with int parameters")
            current = 50
            total = 100
            current_path = "/test/path/file.txt"
            logger.info(f"Parameters: current={current} ({type(current)}), total={total} ({type(total)}), current_path={current_path} ({type(current_path)})")
            self.signal_emitter.scan_progress.emit(current, total, current_path)
            
            # Log and emit with string parameters (which might be the issue)
            logger.info("Emitting scan_progress with string parameters")
            current_str = "50"
            total_str = "100" 
            self.signal_emitter.scan_progress.emit(current_str, total_str, current_path)
            
            # Log and emit scan_finished
            logger.info("Emitting scan_finished")
            results = {"total_size": 1000000, "total_files": 100}
            self.signal_emitter.scan_finished.emit(results)
            
            # Update status
            self.status_label.setText("Signals emitted successfully")
            logger.info("All signals emitted successfully")
            
        except Exception as e:
            logger.error(f"Error emitting signals: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        logger.info(f"_on_scan_started: {path} ({type(path)})")
    
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal - with the CORRECT PARAMETER ORDER"""
        try:
            logger.info(f"_on_scan_progress called with: current={current} ({type(current)}), total={total} ({type(total)}), current_path={current_path} ({type(current_path)})")
            
            # Convert parameters to integers if they're strings - same as in main_window.py
            if isinstance(total, str):
                logger.info(f"Converting total from string to int: {total}")
                total = int(total)
            if isinstance(current, str):
                logger.info(f"Converting current from string to int: {current}")
                current = int(current)
            
            # Calculate percentage
            if total > 0:
                percent = int((current / total) * 100)
                logger.info(f"Calculated percent: {percent}%")
            
            self.status_label.setText(f"Progress: {current}/{total} - {current_path}")
            
        except Exception as e:
            logger.error(f"Error in _on_scan_progress: {e}", exc_info=True)
            self.status_label.setText(f"Error: {str(e)}")
    
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        logger.info(f"_on_scan_finished: {results}")
        self.status_label.setText("Scan finished")
    
    def _on_scan_error(self, error_message):
        """Handle scan error signal"""
        logger.info(f"_on_scan_error: {error_message}")
        self.status_label.setText(f"Error: {error_message}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True) 