"""Unit tests for the scanner module."""

import os
import pytest
import tempfile
import time
from src.core.scanner import DiskScanner


@pytest.mark.unit
class TestScanner:
    """Tests for the DiskScanner class."""
    
    def test_init(self):
        """Test initialization of the scanner."""
        scanner = DiskScanner()
        assert scanner is not None
        assert scanner._stop_requested is False
    
    def test_configure(self):
        """Test configuration of the scanner."""
        scanner = DiskScanner()
        config = {
            'ignore_hidden': True,
            'ignore_system': True,
            'max_threads': 4,
            'excluded_dirs': ['/tmp', '/var'],
            'excluded_types': ['.tmp', '.cache'],
        }
        scanner.configure(config)
        
        assert scanner._ignore_hidden is True
        assert scanner._ignore_system is True
        assert scanner._max_threads == 4
        assert scanner._excluded_dirs == ['/tmp', '/var']
        assert scanner._excluded_types == ['.tmp', '.cache']
    
    def test_scan_empty_dir(self, temp_dir):
        """Test scanning an empty directory."""
        scanner = DiskScanner()
        scanner.scan(temp_dir)
        results = scanner.get_results()
        
        assert results is not None
        assert results['root_path'] == temp_dir
        assert results['total_size'] == 0
        assert results['total_files'] == 0
        assert results['total_dirs'] == 1  # The root directory itself
        assert len(results['files']) == 0
        assert len(results['dirs']) == 1
    
    def test_scan_with_files(self, test_files):
        """Test scanning directory with files."""
        scanner = DiskScanner()
        scanner.scan(test_files)
        results = scanner.get_results()
        
        assert results is not None
        assert results['root_path'] == test_files
        
        # Verify total counts
        assert results['total_files'] == 9  # 9 files created in test_files fixture
        assert results['total_dirs'] >= 4  # Root + docs + images + subfolder
        
        # Verify file size
        expected_size = 1024 + 2048 + 5120 + 10240 + 15360 + 20480 + 25600 + 1024 + 1024
        assert results['total_size'] == expected_size
        
        # Check some specific files
        file1_path = os.path.join(test_files, 'file1.txt')
        assert file1_path in results['files']
        assert results['files'][file1_path]['size'] == 1024
    
    def test_stop_scan(self, test_files):
        """Test stopping a scan."""
        scanner = DiskScanner()
        
        # Set up a callback to stop the scan after a brief delay
        def stop_scan():
            time.sleep(0.1)  # Short delay to ensure scan has started
            scanner._stop_requested = True
        
        import threading
        stop_thread = threading.Thread(target=stop_scan)
        stop_thread.daemon = True
        stop_thread.start()
        
        # Start the scan - it should be stopped by the thread
        scanner.scan(test_files)
        
        # The scan should have been stopped, but some results might be available
        results = scanner.get_results()
        
        # We can't assert specific values since the scan was interrupted,
        # but we can verify the structure
        assert results is not None
        assert 'root_path' in results
        assert 'total_size' in results
        assert 'total_files' in results
        assert 'total_dirs' in results
    
    def test_get_stats(self, test_files):
        """Test getting stats for a specific file."""
        scanner = DiskScanner()
        file_path = os.path.join(test_files, 'file1.txt')
        
        stats = scanner._get_stats(file_path)
        
        assert stats is not None
        assert stats['size'] == 1024
        assert 'mtime' in stats
        assert os.path.isfile(file_path)
    
    @pytest.mark.parametrize("path,expected", [
        ('file.txt', False),
        ('.hidden', True),
        ('normal/file.txt', False),
        ('normal/.hiddenfile', True),
        ('.hidden/file.txt', True),
    ])
    def test_is_hidden(self, path, expected):
        """Test detection of hidden files."""
        scanner = DiskScanner()
        assert scanner._is_hidden(path) == expected
    
    @pytest.mark.parametrize("path,extensions,expected", [
        ('file.txt', ['.tmp', '.log'], False),
        ('file.tmp', ['.tmp', '.log'], True),
        ('file.log', ['.tmp', '.log'], True),
        ('file.txt.tmp', ['.tmp', '.log'], True),
        ('file', ['.tmp', '.log'], False),
    ])
    def test_has_excluded_extension(self, path, extensions, expected):
        """Test detection of excluded file extensions."""
        scanner = DiskScanner()
        scanner._excluded_types = extensions
        assert scanner._has_excluded_extension(path) == expected


@pytest.mark.integration
class TestScannerIntegration:
    """Integration tests for the DiskScanner class."""
    
    def test_scan_resume(self, test_files):
        """Test resuming a scan."""
        # First scan partially (we'll fake this by doing a full scan and saving checkpoint)
        scanner1 = DiskScanner()
        scanner1.scan(test_files)
        
        # Save checkpoint data
        checkpoint_file = os.path.join(tempfile.gettempdir(), 'scan_checkpoint.json')
        scanner1._save_checkpoint(checkpoint_file, scanner1.get_results())
        
        # Create new scanner and "resume" scan
        scanner2 = DiskScanner()
        scanner2._checkpoint_file = checkpoint_file
        scanner2.scan(test_files, resume=True)
        
        # Verify results are the same
        results1 = scanner1.get_results()
        results2 = scanner2.get_results()
        
        assert results1['total_size'] == results2['total_size']
        assert results1['total_files'] == results2['total_files']
        assert results1['total_dirs'] == results2['total_dirs']
        
        # Clean up
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file) 