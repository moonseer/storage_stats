#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnostic script to check scan results structure
"""

import os
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.core.scanner import DiskScanner
from src.utils.helpers import human_readable_size

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ScanChecker")

class ScanChecker(QObject):
    """Class to run scan and check the results"""
    
    def __init__(self):
        super().__init__()
        self.scanner = DiskScanner()
    
    def run_scan(self, path):
        """Run a scan and analyze the results"""
        logger.info(f"Starting scan of {path}")
        
        # Configure scanner with debug settings
        self.scanner.configure({
            'max_threads': 2,
            'calculate_hashes': False,
            'skip_hidden': False,
            'exclude_paths': []
        })
        
        # Run scan in blocking mode
        result = self.scanner.scan(path, is_blocking=True)
        
        # Check if result exists
        if not result:
            logger.error("Scan returned no results")
            return
        
        # Analyze the scan result structure
        self._analyze_result(result)
    
    def _analyze_result(self, result):
        """Analyze scan result structure to diagnose issues"""
        logger.info("Analyzing scan results:")
        
        # Check top-level fields
        for key in ['total_size', 'total_files', 'total_dirs', 'scan_time']:
            if key in result:
                logger.info(f"{key}: {result[key]}")
            else:
                logger.warning(f"Missing expected field: {key}")
        
        # Check total size
        total_size = result.get('total_size', 0)
        logger.info(f"Total size (human readable): {human_readable_size(total_size)}")
        
        # Check files dictionary
        files = result.get('files', {})
        logger.info(f"Number of files in result: {len(files)}")
        
        # Sample some files to check sizes
        file_sizes = 0
        large_files = 0
        for i, (file_path, file_info) in enumerate(list(files.items())[:10]):
            size = file_info.get('size', 0)
            file_sizes += size
            logger.info(f"Sample file {i+1}: {file_path} - Size: {size} bytes ({human_readable_size(size)})")
            if size > 1024*1024:  # Files larger than 1MB
                large_files += 1
        
        # Log size statistics
        if len(files) > 0:
            logger.info(f"Average size of sampled files: {file_sizes / min(10, len(files))} bytes")
            logger.info(f"Number of large files in sample: {large_files}")
            
        # Check the sum of file sizes vs. reported total
        manual_sum = sum(file_info.get('size', 0) for file_info in files.values())
        logger.info(f"Sum of all file sizes: {manual_sum} bytes ({human_readable_size(manual_sum)})")
        logger.info(f"Difference between sum and reported total: {manual_sum - total_size} bytes")
        
        # Check for errors
        errors = result.get('errors', [])
        logger.info(f"Number of errors: {len(errors)}")
        for i, error in enumerate(errors[:5]):
            logger.info(f"Error {i+1}: {error}")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Path to scan
    scan_path = "/Users/moonseer/Downloads"
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    
    # Run the checker
    checker = ScanChecker()
    checker.run_scan(scan_path)
    
    # No need to execute the app
    sys.exit(0)

if __name__ == "__main__":
    main() 