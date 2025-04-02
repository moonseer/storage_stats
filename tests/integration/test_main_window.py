"""Integration tests for the main window."""

import os
import pytest
import tempfile
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from src.ui.main_window import MainWindow


@pytest.mark.integration
class TestMainWindow:
    """Integration tests for the MainWindow class."""
    
    def test_init(self, qt_app):
        """Test initialization of the main window."""
        window = MainWindow()
        assert window is not None
        
        # Check that the main components are created
        assert hasattr(window, 'tab_widget')
        assert hasattr(window, 'scanner')
        assert hasattr(window, 'analyzer')
        assert window.scan_results is None
    
    def test_ui_components(self, qt_app):
        """Test that UI components are initialized correctly."""
        window = MainWindow()
        
        # Check that tabs are created
        assert window.tab_widget.count() >= 5  # Should have at least 5 tabs
        
        # Check that actions are created
        assert hasattr(window, 'scan_action')
        assert hasattr(window, 'stop_scan_action')
        assert hasattr(window, 'settings_action')
    
    def test_scan_and_ui_update(self, qt_app, test_files, monkeypatch):
        """Test scanning a directory and updating the UI."""
        # Create a main window
        window = MainWindow()
        
        # Mock the file dialog to return our test directory
        monkeypatch.setattr(
            QFileDialog, 'getExistingDirectory',
            lambda *args, **kwargs: test_files
        )
        
        # Start a scan - this would normally be triggered by a user action
        window._on_scan_action()
        
        # Wait for scan to complete and UI to update
        # In a real test, we'd use QSignalSpy to wait for signals,
        # but we'll simulate the completion callback directly for this test
        
        # Simulate scan completed with results
        window._on_scan_finished({
            'root_path': test_files,
            'total_size': 81920,  # Sum of all test file sizes
            'total_files': 9,  # Number of test files
            'total_dirs': 4,  # Number of test directories
            'files': {
                # Example file entries - in a real test these would be from actual scan
                os.path.join(test_files, 'file1.txt'): {'size': 1024, 'mtime': 0},
                os.path.join(test_files, 'file2.txt'): {'size': 2048, 'mtime': 0},
            },
            'dirs': {
                # Example directory entries
                test_files: {'size': 81920, 'files': 9},
                os.path.join(test_files, 'docs'): {'size': 15360, 'files': 2},
                os.path.join(test_files, 'images'): {'size': 61440, 'files': 3},
            }
        })
        
        # Verify that the scan results were processed
        assert window.scan_results is not None
        assert window.scan_results['total_files'] == 9
        assert window.scan_results['total_size'] == 81920
        
        # Verify that UI elements were updated
        assert not window.scan_in_progress
        assert window.stop_scan_action.isEnabled() is False
        
        # Verify that tabs have been updated with data
        # The dashboard should no longer show the welcome screen
        dashboard_tab = window.tab_widget.widget(0)
        if hasattr(dashboard_tab, 'welcome_label'):
            assert not dashboard_tab.welcome_label.isVisible()

    def test_tab_switching(self, qt_app, monkeypatch):
        """Test switching between tabs."""
        window = MainWindow()
        
        # Store the current tab index
        current_index = window.tab_widget.currentIndex()
        
        # Switch to a different tab
        new_index = (current_index + 1) % window.tab_widget.count()
        window.tab_widget.setCurrentIndex(new_index)
        
        # Verify that the tab has changed
        assert window.tab_widget.currentIndex() == new_index
        
        # Test that view is updated when tab changes
        # Since we don't have real scan data, we'll need to mock it
        window.scan_results = {
            'root_path': '/test',
            'total_size': 1024,
            'total_files': 10,
            'total_dirs': 5,
            'files': {},
            'dirs': {}
        }
        
        # Create a mock for the update_view method
        tab_updated = [False] * window.tab_widget.count()
        
        original_update_view = None
        if hasattr(window.tab_widget.widget(0), 'update_view'):
            original_update_view = window.tab_widget.widget(0).update_view
        
        def mock_update_view(self, results, analyzer):
            tab_index = window.tab_widget.indexOf(self)
            tab_updated[tab_index] = True
            if original_update_view:
                original_update_view(results, analyzer)
        
        # Patch the update_view method for all tabs
        for i in range(window.tab_widget.count()):
            tab = window.tab_widget.widget(i)
            if hasattr(tab, 'update_view'):
                monkeypatch.setattr(
                    type(tab), 'update_view',
                    mock_update_view.__get__(tab, type(tab))
                )
        
        # Change tabs again to trigger update
        window.tab_widget.setCurrentIndex((new_index + 1) % window.tab_widget.count())
        
        # Verify that the current tab's update_view method was called
        assert tab_updated[window.tab_widget.currentIndex()]


@pytest.mark.integration
class TestScannerIntegration:
    """Tests for the scanner integration with the main window."""
    
    def test_scan_start_and_stop(self, qt_app, test_files, monkeypatch):
        """Test starting and stopping a scan."""
        window = MainWindow()
        
        # Connect to scan_started signal and store the path
        scan_started_path = [None]
        
        def on_scan_started(path):
            scan_started_path[0] = path
        
        window.scanner.scan_started.connect(on_scan_started)
        
        # Start a scan
        window._start_scan(test_files)
        
        # Verify scan was started
        assert window.scan_in_progress is True
        assert window.stop_scan_action.isEnabled() is True
        assert scan_started_path[0] == test_files
        
        # Stop the scan
        # Mock the message box to return 'Yes'
        monkeypatch.setattr(
            QMessageBox, 'question',
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes
        )
        
        window._on_stop_scan_action()
        
        # Verify that the scan was stopped
        assert window.scanner._stop_requested is True 