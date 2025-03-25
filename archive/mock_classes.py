#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock classes for testing
"""

from PyQt6.QtCore import QTimer

class MockSignal:
    """Mock PyQt signal"""
    def __init__(self):
        self.callbacks = []
    
    def connect(self, callback):
        self.callbacks.append(callback)
    
    def emit(self, *args):
        for callback in self.callbacks:
            callback(*args)

class MockScanner:
    """Mock scanner class"""
    def __init__(self):
        self.scan_started = MockSignal()
        self.scan_progress = MockSignal()
        self.scan_finished = MockSignal()
        self.scan_error = MockSignal()
        self._stop_requested = False
    
    def configure(self, config):
        pass
    
    def scan(self, directory, resume=False):
        # Simulate immediate completion for testing
        self.scan_started.emit(directory)
        
        # Simulate progress updates
        self._progress_value = 0
        self._total_value = 100
        self._directory = directory
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_progress)
        self._timer.start(100)  # Update every 100ms
    
    def _update_progress(self):
        """Update progress"""
        self._progress_value += 5
        if self._progress_value >= self._total_value or self._stop_requested:
            self._timer.stop()
            if self._stop_requested:
                self.scan_finished.emit(None)
            else:
                result = {
                    "total_size": 1000000, 
                    "total_files": 100,
                    "total_dirs": 10,
                    "scan_path": self._directory,
                    "scan_time": 5.0
                }
                self.scan_finished.emit(result)
        else:
            mock_path = f"{self._directory}/file_{self._progress_value}.txt"
            self.scan_progress.emit(self._progress_value, self._total_value, mock_path)
    
    def has_partial_scan(self, path):
        return None

class MockAnalyzer:
    """Mock analyzer class"""
    def __init__(self):
        pass
    
    def get_scan_results(self):
        return {"total_size": 1000000, "total_files": 100, "total_dirs": 10}
    
    def get_largest_files(self, results, limit=50):
        # Return some mock files
        mock_files = []
        for i in range(1, min(limit+1, 10)):
            mock_files.append({
                "path": f"/mock/path/to/large_file_{i}.dat",
                "size": 1000000 // i,
                "mtime": 1648000000 + i*1000
            })
        return mock_files
    
    def get_largest_directories(self, results, limit=50):
        # Return some mock directories
        mock_dirs = []
        for i in range(1, min(limit+1, 10)):
            mock_dirs.append({
                "path": f"/mock/path/to/dir_{i}",
                "size": 1000000 // i,
                "files": 50 // i
            })
        return mock_dirs
    
    def get_file_type_breakdown(self, results):
        # Return mock file type breakdown
        return {
            "text": {"size": 200000, "count": 30},
            "image": {"size": 300000, "count": 20},
            "document": {"size": 150000, "count": 15},
            "video": {"size": 250000, "count": 5},
            "other": {"size": 100000, "count": 30}
        }
    
    def get_duplicate_files(self, results):
        # Return mock duplicates
        mock_duplicates = {}
        for i in range(1, 5):
            hash_key = f"mock_hash_{i}"
            files = []
            for j in range(1, i+2):
                files.append({
                    "path": f"/mock/path/to/duplicate_{i}_{j}.dat",
                    "size": 100000 * i,
                    "mtime": 1648000000 + j*1000
                })
            mock_duplicates[hash_key] = files
        return mock_duplicates 