"""UI tests for the dashboard view."""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QFrame
from src.ui.dashboard_view import DashboardView
from src.core.analyzer import DataAnalyzer


@pytest.mark.ui
class TestDashboardView:
    """Tests for the DashboardView class."""
    
    def test_init(self, qt_app):
        """Test initialization of the dashboard view."""
        view = DashboardView()
        assert view is not None
        
        # Check that UI elements are created
        assert hasattr(view, 'scan_button')
        assert hasattr(view, 'welcome_label')
    
    def test_update_view_with_no_data(self, qt_app):
        """Test updating the view with no data."""
        view = DashboardView()
        view.update_view(None, None)
        
        # Welcome message should be visible when there's no data
        assert view.welcome_label.isVisible()
        assert view.scan_button.isVisible()
    
    def test_update_view_with_data(self, qt_app, scan_results, analyzed_data):
        """Test updating the view with scan results."""
        view = DashboardView()
        view.update_view(scan_results, analyzed_data)
        
        # Welcome message should be hidden when there's data
        assert not view.welcome_label.isVisible()
        assert not view.scan_button.isVisible()
        
        # Tables should be created and populated
        assert hasattr(view, 'largest_files_table')
        assert hasattr(view, 'largest_dirs_table')
    
    def test_largest_files_display(self, qt_app, scan_results, analyzed_data):
        """Test that largest files are displayed correctly."""
        # Get the largest files from the analyzer
        largest_files = analyzed_data.get_largest_files()
        
        # Create and update the view
        view = DashboardView()
        view.update_view(scan_results, analyzed_data)
        
        # Check that the table contains the correct number of rows
        assert view.largest_files_table.rowCount() == min(5, len(largest_files))
        
        # Check column count (usually 2: name, size)
        assert view.largest_files_table.columnCount() >= 2
    
    def test_largest_dirs_display(self, qt_app, scan_results, analyzed_data):
        """Test that largest directories are displayed correctly."""
        # Get the largest directories from the analyzer
        largest_dirs = analyzed_data.get_largest_dirs()
        
        # Create and update the view
        view = DashboardView()
        view.update_view(scan_results, analyzed_data)
        
        # Check that the table contains the correct number of rows
        assert view.largest_dirs_table.rowCount() == min(5, len(largest_dirs))
        
        # Check column count (usually 2: name, size)
        assert view.largest_dirs_table.columnCount() >= 2
    
    def test_recommendations_display(self, qt_app, scan_results, analyzed_data):
        """Test that recommendations are displayed correctly."""
        # Get recommendations from the analyzer
        recommendations = analyzed_data.get_recommendations()
        
        # Create and update the view
        view = DashboardView()
        view.update_view(scan_results, analyzed_data)
        
        # Verify recommendations section exists
        assert hasattr(view, 'recommendations_label')
        
        # Check that recommendations container is visible if there are recommendations
        if recommendations:
            # There should be a container for recommendations
            assert view.findChild(QFrame, "recommendationsFrame") is not None
        else:
            # If no recommendations, there should be a label indicating this
            no_recommendations_labels = [
                widget for widget in view.findChildren(QLabel) 
                if widget.text() and "No recommendations" in widget.text()
            ]
            assert len(no_recommendations_labels) > 0
    
    def test_scan_button_signal(self, qt_app):
        """Test that scan button emits the correct signal."""
        view = DashboardView()
        
        # Connect to the signal and verify it's emitted when the button is clicked
        signal_emitted = False
        
        def on_scan_requested():
            nonlocal signal_emitted
            signal_emitted = True
        
        view.scan_requested.connect(on_scan_requested)
        view.scan_button.click()
        
        assert signal_emitted is True 