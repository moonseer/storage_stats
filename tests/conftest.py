"""Pytest configuration file with fixtures for testing Storage Stats."""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_files(temp_dir):
    """Create test files for testing the scanner."""
    # Create a test file structure
    files = {
        'file1.txt': 1024,  # 1KB
        'file2.txt': 2048,  # 2KB
        'docs/doc1.pdf': 5120,  # 5KB
        'docs/doc2.pdf': 10240,  # 10KB
        'images/img1.jpg': 15360,  # 15KB
        'images/img2.jpg': 20480,  # 20KB
        'images/subfolder/img3.jpg': 25600,  # 25KB
        'duplicate1.txt': 1024,  # Duplicate of file1.txt
        'subfolder/duplicate2.txt': 1024  # Another duplicate
    }
    
    # Create the files
    for file_path, size in files.items():
        full_path = os.path.join(temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Create file of specified size
        with open(full_path, 'wb') as f:
            f.write(b'0' * size)
    
    return temp_dir


@pytest.fixture
def scanner():
    """Create a DiskScanner instance for testing."""
    return DiskScanner()


@pytest.fixture
def analyzer():
    """Create a DataAnalyzer instance for testing."""
    return DataAnalyzer()


@pytest.fixture
def scan_results(scanner, test_files):
    """Run a scan on the test files and return the results."""
    scanner.scan(test_files)
    return scanner.get_results()


@pytest.fixture
def analyzed_data(analyzer, scan_results):
    """Analyze the scan results and return the analyzer instance."""
    analyzer.set_scan_results(scan_results)
    return analyzer


@pytest.fixture
def qt_app():
    """Create a QApplication instance for UI testing."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    yield app
    app.quit() 