#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Main window module
"""

import os
import sys
import logging
import time
import platform
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QFileDialog, QMessageBox, 
    QToolBar, QStatusBar, QProgressBar, QMenu, QMenuBar,
    QDialog, QDialogButtonBox, QTextBrowser, QComboBox, QSizePolicy,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal, pyqtSlot, QSize, QUrl
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QDesktopServices

from src.ui.dashboard_view import DashboardView
from src.ui.file_browser_view import FileBrowserView
from src.ui.duplicates_view import DuplicatesView
from src.ui.file_types_view import FileTypesView
from src.ui.recommendations_view import RecommendationsView
from src.ui.settings_dialog import SettingsDialog
from src.ui.shortcuts_dialog import ShortcutsDialog
from src.ui.filter_dialog import FilterDialog
from src.utils.helpers import human_readable_size, get_system_paths
from src.core.scanner import DiskScanner
from src.core.analyzer import DataAnalyzer
from src.ui.report_generator import ReportGenerator

logger = logging.getLogger("StorageStats.UI.MainWindow")

class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Storage Stats")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # App title
        title_label = QLabel("Storage Stats")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        desc_label = QTextBrowser()
        desc_label.setOpenExternalLinks(True)
        desc_label.setHtml("""
        <p>Storage Stats is a powerful disk space analyzer for macOS built with Python and PyQt6.</p>
        
        <p><b>Features:</b></p>
        <ul>
            <li>Fast and efficient file system scanning</li>
            <li>Interactive dashboard and visualizations</li>
            <li>Duplicate file detection</li>
            <li>Storage recommendations</li>
            <li>Multi-threaded analysis</li>
        </ul>
        
        <p><b>Developers:</b> Storage Stats Team</p>
        <p><b>Website:</b> <a href="https://storagestats.app">https://storagestats.app</a></p>
        """)
        
        # Copyright
        copyright_label = QLabel(f"© {datetime.now().year} Storage Stats")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addWidget(desc_label)
        layout.addWidget(copyright_label)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class MainWindow(QMainWindow):
    """Main window for the Storage Stats application"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.scanner = DiskScanner()
        self.analyzer = DataAnalyzer()
        self.current_scan_path = None
        self.scan_results = None
        self.settings = QSettings("StorageStats", "StorageStats")
        self.report_generator = ReportGenerator(self)
        self.scan_in_progress = False
        
        # Set up window properties
        self.setWindowTitle("Storage Stats - Disk Analyzer")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Restore window geometry if available
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        # Create UI components
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
        
        # Connect scanner signals
        self.scanner.scan_started.connect(self._on_scan_started)
        self.scanner.scan_progress.connect(self._on_scan_progress)
        self.scanner.scan_finished.connect(self._on_scan_finished)
        self.scanner.scan_error.connect(self._on_scan_error)
        
        # Load settings
        self._load_settings()
        
        # Check for partial scans at startup
        self._check_for_partial_scans()
        
        logger.info("Main window initialized")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        
        # Accept close event
        event.accept()
    
    def _create_actions(self):
        """Create actions for menus and toolbars"""
        # Scan actions
        self.scan_action = QAction("Scan Directory...", self)
        self.scan_action.setStatusTip("Scan a directory for storage analysis")
        self.scan_action.triggered.connect(self._on_scan_action)
        self.scan_action.setShortcut(QKeySequence("Ctrl+O"))
        
        self.stop_scan_action = QAction("Stop Scan", self)
        self.stop_scan_action.setStatusTip("Stop the current scan")
        self.stop_scan_action.setEnabled(False)
        self.stop_scan_action.triggered.connect(self._on_stop_scan_action)
        self.stop_scan_action.setShortcut(QKeySequence("Esc"))
        
        # Settings actions
        self.settings_action = QAction("Settings...", self)
        self.settings_action.setStatusTip("Configure application settings")
        self.settings_action.triggered.connect(self._on_settings_action)
        self.settings_action.setShortcut(QKeySequence("Ctrl+,"))
        
        # Filter action
        self.filter_action = QAction("Customize Filters...", self)
        self.filter_action.setStatusTip("Customize file filters")
        self.filter_action.triggered.connect(self._on_filter_action)
        self.filter_action.setShortcut(QKeySequence("Ctrl+F"))
        
        # Report actions
        self.save_html_report_action = QAction("Save HTML Report...", self)
        self.save_html_report_action.setStatusTip("Save scan results as an HTML report")
        self.save_html_report_action.triggered.connect(lambda: self._on_save_report("html"))
        self.save_html_report_action.setEnabled(False)
        
        self.save_csv_report_action = QAction("Save CSV Report...", self)
        self.save_csv_report_action.setStatusTip("Save scan results as CSV files")
        self.save_csv_report_action.triggered.connect(lambda: self._on_save_report("csv"))
        self.save_csv_report_action.setEnabled(False)
        
        self.save_text_report_action = QAction("Save Text Report...", self)
        self.save_text_report_action.setStatusTip("Save scan results as a text report")
        self.save_text_report_action.triggered.connect(lambda: self._on_save_report("text"))
        self.save_text_report_action.setEnabled(False)
        
        self.save_json_report_action = QAction("Save JSON Report...", self)
        self.save_json_report_action.setStatusTip("Save scan results as a JSON file")
        self.save_json_report_action.triggered.connect(lambda: self._on_save_report("json"))
        self.save_json_report_action.setEnabled(False)
        
        # Help actions
        self.about_action = QAction("About...", self)
        self.about_action.setStatusTip("Show information about the application")
        self.about_action.triggered.connect(self._on_about_action)
        
        self.help_action = QAction("Help", self)
        self.help_action.setStatusTip("Show help documentation")
        self.help_action.triggered.connect(self._on_help_action)
        self.help_action.setShortcut(QKeySequence("F1"))
    
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        scan_action = QAction("&Scan Directory...", self)
        scan_action.setShortcut("Ctrl+O")
        scan_action.setStatusTip("Scan a directory for disk usage")
        scan_action.triggered.connect(self._select_directory)
        file_menu.addAction(scan_action)
        
        resume_action = QAction("&Resume Scan...", self)
        resume_action.setShortcut("Ctrl+R")
        resume_action.setStatusTip("Resume a previous scan")
        resume_action.triggered.connect(self._show_resume_dialog)
        file_menu.addAction(resume_action)
        
        stop_action = QAction("Stop Scan", self)
        stop_action.setShortcut("Ctrl+C")
        stop_action.setStatusTip("Stop the current scan")
        stop_action.triggered.connect(self._stop_scan)
        stop_action.setEnabled(False)
        self.stop_action = stop_action
        file_menu.addAction(stop_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Report...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Export scan results to a file")
        export_action.triggered.connect(self._export_report)
        export_action.setEnabled(False)
        self.export_action = export_action
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self._show_settings_dialog)
        edit_menu.addAction(settings_action)
        
        edit_menu.addSeparator()
        
        filter_action = QAction("&Customize Filters...", self)
        filter_action.setShortcut("Ctrl+F")
        filter_action.setStatusTip("Customize file filters")
        filter_action.triggered.connect(self._show_filter_dialog)
        edit_menu.addAction(filter_action)
        
        # View menu
        view_menu = menu_bar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh the current view")
        refresh_action.triggered.connect(self._refresh_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Tab switching actions
        tab_actions = []
        
        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        tab_actions.append(dashboard_action)
        
        files_action = QAction("&Files && Folders", self)
        files_action.setShortcut("Ctrl+2")
        files_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        tab_actions.append(files_action)
        
        duplicates_action = QAction("&Duplicates", self)
        duplicates_action.setShortcut("Ctrl+3")
        duplicates_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        tab_actions.append(duplicates_action)
        
        types_action = QAction("File &Types", self)
        types_action.setShortcut("Ctrl+4")
        types_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        tab_actions.append(types_action)
        
        recommendations_action = QAction("&Recommendations", self)
        recommendations_action.setShortcut("Ctrl+5")
        recommendations_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(4))
        tab_actions.append(recommendations_action)
        
        tabs_menu = view_menu.addMenu("Tabs")
        for action in tab_actions:
            tabs_menu.addAction(action)
        
        # Zoom actions
        zoom_menu = view_menu.addMenu("Zoom")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._zoom_in)
        zoom_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._zoom_out)
        zoom_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self._zoom_reset)
        zoom_menu.addAction(zoom_reset_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        self.fullscreen_action = fullscreen_action
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.setStatusTip("Show keyboard shortcuts")
        shortcuts_action.triggered.connect(self._show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show information about the application")
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """Create the main toolbar"""
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Add scan directory button
        toolbar.addAction(self.scan_action)
        toolbar.addAction(self.stop_scan_action)
        toolbar.addSeparator()
        
        # Add location combo box
        location_label = QLabel("Location: ")
        toolbar.addWidget(location_label)
        
        self.location_combo = QComboBox()
        self.location_combo.setMinimumWidth(300)
        self.location_combo.setEditable(True)
        self.location_combo.currentIndexChanged.connect(self._on_scan_location)
        toolbar.addWidget(self.location_combo)
        
        # Add scan button
        scan_button = QPushButton("Scan")
        scan_button.clicked.connect(self._on_scan_location)
        toolbar.addWidget(scan_button)
        
        # Add right-aligned settings button
        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)
        
        toolbar.addAction(self.filter_action)
        toolbar.addAction(self.settings_action)
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m (%p%)")
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Set initial status
        self.status_bar.showMessage("Ready")
    
    def _create_central_widget(self):
        """Create the central widget with tab layout"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tab pages
        self.dashboard_view = DashboardView()
        self.file_browser_view = FileBrowserView()
        self.duplicates_view = DuplicatesView()
        self.file_types_view = FileTypesView()
        self.recommendations_view = RecommendationsView()
        
        # Connect dashboard scan button to the scan action
        self.dashboard_view.scan_requested.connect(self._on_scan_action)
        
        # Add tabs
        self.tab_widget.addTab(self.dashboard_view, "Dashboard")
        self.tab_widget.addTab(self.file_browser_view, "Files & Folders")
        self.tab_widget.addTab(self.duplicates_view, "Duplicates")
        self.tab_widget.addTab(self.file_types_view, "File Types")
        self.tab_widget.addTab(self.recommendations_view, "Recommendations")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _populate_location_combo(self):
        """Populate the location combo box with common paths"""
        # Clear existing items
        self.location_combo.clear()
        
        # Get current user's home directory
        home_dir = os.path.expanduser("~")
        self.location_combo.addItem(home_dir)
        
        # Add other common locations
        if platform.system() == "Darwin":  # macOS
            self.location_combo.addItem("/")  # Root
            self.location_combo.addItem(os.path.join(home_dir, "Documents"))
            self.location_combo.addItem(os.path.join(home_dir, "Downloads"))
            self.location_combo.addItem(os.path.join(home_dir, "Desktop"))
            self.location_combo.addItem(os.path.join(home_dir, "Pictures"))
            self.location_combo.addItem(os.path.join(home_dir, "Music"))
            self.location_combo.addItem(os.path.join(home_dir, "Movies"))
        elif platform.system() == "Windows":
            for drive in range(ord('A'), ord('Z')+1):
                drive_letter = chr(drive) + ":/"
                if os.path.exists(drive_letter):
                    self.location_combo.addItem(drive_letter)
            
            # Add common Windows folders
            self.location_combo.addItem(os.path.join(home_dir, "Documents"))
            self.location_combo.addItem(os.path.join(home_dir, "Downloads"))
            self.location_combo.addItem(os.path.join(home_dir, "Desktop"))
            self.location_combo.addItem(os.path.join(home_dir, "Pictures"))
        else:  # Linux and others
            self.location_combo.addItem("/")
            self.location_combo.addItem(os.path.join(home_dir, "Documents"))
            self.location_combo.addItem(os.path.join(home_dir, "Downloads"))
    
    @pyqtSlot()
    def _on_scan_action(self):
        """Handle scan action"""
        if self.scan_in_progress:
            QMessageBox.warning(
                self,
                "Scan in Progress",
                "A scan is already in progress. Please wait for it to complete or stop it before starting a new scan."
            )
            return
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Scan",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self._start_scan(directory)
    
    @pyqtSlot()
    def _on_scan_location(self):
        """Handle scan from location combo box"""
        location = self.location_combo.currentText()
        if location and os.path.exists(location) and os.path.isdir(location):
            self._start_scan(location)
        else:
            QMessageBox.warning(
                self,
                "Invalid Location",
                f"The location '{location}' does not exist or is not a directory."
            )
    
    def _start_scan(self, directory, resume=False):
        """Start scanning a directory"""
        if self.scan_in_progress:
            return
        
        self.current_scan_path = directory
        self.scan_in_progress = True
        
        # Get scanner configuration from settings
        config = self._get_scanner_config()
        self.scanner.configure(config)
        
        # Start the scan
        logger.info(f"Starting scan of {directory}")
        self.scanner.scan(directory, resume=resume)
        
        # Update UI state
        self.stop_scan_action.setEnabled(True)
        self.status_bar.showMessage(f"Scanning {directory}...")
    
    @pyqtSlot()
    def _on_stop_scan_action(self):
        """Handle stop scan action"""
        if not self.scan_in_progress:
            return
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            "Are you sure you want to stop the current scan? Progress will be saved and you can resume later.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner._stop_requested = True
            self.status_bar.showMessage("Stopping scan...")
    
    @pyqtSlot(str)
    def _on_scan_started(self, path):
        """Handle scan started signal"""
        self.status_bar.showMessage(f"Scanning {path}...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.stop_scan_action.setEnabled(True)
        self.scan_in_progress = True
        
        # Update widget states
        self._update_ui_state()
    
    @pyqtSlot(int, int, str)
    def _on_scan_progress(self, current, total, current_path):
        """Handle scan progress signal"""
        try:
            # Convert parameters to integers if they're strings
            if isinstance(total, str):
                total = int(total)
            if isinstance(current, str):
                current = int(current)
                
            if total > 0:
                percent = int((current / total) * 100)
                self.progress_bar.setValue(percent)
            self.status_bar.showMessage(f"Scanning: {current_path}")
        except Exception as e:
            logger.error(f"Error in scan progress handler: {e}")
            # Don't crash on progress updates
    
    @pyqtSlot(object)
    def _on_scan_finished(self, results):
        """Handle scan finished signal"""
        self.progress_bar.setVisible(False)
        self.stop_scan_action.setEnabled(False)
        self.scan_in_progress = False
        
        if results:
            # Update widget states
            self.scan_results = results
            
            # Process the scan results with the analyzer
            logger.info("Processing scan results with analyzer")
            self.analyzer.set_scan_results(results)
            
            self.save_html_report_action.setEnabled(True)
            self.save_csv_report_action.setEnabled(True)
            self.save_text_report_action.setEnabled(True)
            self.save_json_report_action.setEnabled(True)
            
            # Add to recent paths
            self._add_to_recent_paths(self.current_scan_path)
            
            # Show message in status bar
            total_size = results.get("total_size", 0)
            total_files = results.get("total_files", 0)
            status_msg = f"Scan completed: {human_readable_size(total_size, preferred_unit='GB')}, {total_files:,} files"
            self.status_bar.showMessage(status_msg)
            
            # Update all tabs with the results
            self._refresh_view()
        else:
            # Scan was stopped by user
            self.status_bar.showMessage("Scan stopped")
        
        # Update widget states
        self._update_ui_state()
    
    @pyqtSlot(str)
    def _on_scan_error(self, error_msg):
        """Handle scan error signal"""
        logger.error(f"Scan error: {error_msg}")
        
        # Reset UI
        self.scan_action.setEnabled(True)
        self.stop_scan_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Show error message
        QMessageBox.critical(
            self,
            "Scan Error",
            f"An error occurred during the scan:\n\n{error_msg}"
        )
        
        # Update status bar
        self.status_bar.showMessage("Scan failed")
    
    @pyqtSlot(int)
    def _on_tab_changed(self, index):
        """Handle tab change signal"""
        # Update active tab with current data if scan results are available
        if self.scan_results:
            tab_widget = self.tab_widget.widget(index)
            if hasattr(tab_widget, 'update_view') and callable(tab_widget.update_view):
                tab_widget.update_view(self.scan_results, self.analyzer)
    
    def _update_ui_state(self):
        """Update UI element states based on application state"""
        has_results = self.scan_results is not None
        
        # Update menu actions
        self.save_html_report_action.setEnabled(has_results)
        self.save_csv_report_action.setEnabled(has_results)
        self.save_text_report_action.setEnabled(has_results)
        self.save_json_report_action.setEnabled(has_results)
        
        # Update toolbar actions
        if hasattr(self, 'stop_button'):
            self.stop_button.setEnabled(self.scan_in_progress)
        
        if hasattr(self, 'scan_button'):
            self.scan_button.setEnabled(not self.scan_in_progress)
        
        # Update tab visibility
        if hasattr(self, 'tab_widget'):
            dashboard_tab = self.tab_widget.widget(0)
            if isinstance(dashboard_tab, QWidget):
                # If scan is in progress, show a message
                if hasattr(dashboard_tab, 'update_view'):
                    if self.scan_in_progress:
                        dashboard_tab.update_view(None, None)
                    elif has_results:
                        dashboard_tab.update_view(self.scan_results, self.analyzer)
    
    @pyqtSlot()
    def _on_settings_action(self):
        """Handle Settings action"""
        dialog = SettingsDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Reload settings
            pass
    
    @pyqtSlot()
    def _on_filter_action(self):
        """Handle Filter action"""
        dialog = FilterDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Apply filters to views
            filter_settings = dialog.get_filter_settings()
            if filter_settings['enabled']:
                # Update views with filter settings
                self._apply_filters(filter_settings)
                self.status_bar.showMessage("Filters applied")
            else:
                # Clear filters
                self._clear_filters()
                self.status_bar.showMessage("Filters cleared")
    
    def _apply_filters(self, filter_settings):
        """Apply filters to the views"""
        # In a real implementation, this would update each view with the filter settings
        # For now, we'll just show what filters are applied
        message = "Filters applied:\n"
        
        if filter_settings['size']['enabled']:
            message += "- Size filter\n"
        
        if filter_settings['date']['enabled']:
            message += "- Date filter\n"
        
        if filter_settings['type']['enabled']:
            message += "- Type filter\n"
            
        if filter_settings['name']['enabled']:
            message += "- Name filter\n"
        
        logger.info(message)
        
        # Update each view with the filters
        # This would be implemented in each view class
        # self.file_browser_view.apply_filters(filter_settings)
        # self.duplicates_view.apply_filters(filter_settings)
        # self.file_types_view.apply_filters(filter_settings)
    
    def _clear_filters(self):
        """Clear all filters from the views"""
        logger.info("Filters cleared")
        
        # Clear filters from each view
        # This would be implemented in each view class
        # self.file_browser_view.clear_filters()
        # self.duplicates_view.clear_filters()
        # self.file_types_view.clear_filters()
    
    @pyqtSlot()
    def _on_about_action(self):
        """Handle about action"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    @pyqtSlot()
    def _on_help_action(self):
        """Handle help action"""
        # In a real app, this would open actual documentation
        QMessageBox.information(
            self,
            "Help",
            "For help using Storage Stats, please refer to the user documentation."
        )
    
    @pyqtSlot()
    def _on_save_report(self, format_type):
        """Handle saving report"""
        scan_results = self.analyzer.get_scan_results()
        
        if not scan_results:
            QMessageBox.warning(
                self,
                "No Data",
                "There is no scan data to generate a report from. Please run a scan first."
            )
            return
        
        # Generate the report using the report generator
        success = self.report_generator.generate_report(
            scan_results, 
            self.analyzer, 
            format_type, 
            self
        )
        
        if success:
            self.status_bar.showMessage(f"{format_type.upper()} report generated successfully")
        else:
            self.status_bar.showMessage(f"Failed to generate {format_type.upper()} report")
            QMessageBox.warning(
                self,
                "Report Generation Failed",
                f"Failed to generate the {format_type.upper()} report. Please check the logs for details."
            )

    def _get_scanner_config(self):
        """Get scanner configuration from settings"""
        # This method should be implemented to return the appropriate scanner configuration
        # based on the current settings and environment
        return {}

    def _add_to_recent_paths(self, path):
        """Add a path to the list of recently scanned paths"""
        settings = QSettings("Storage Stats", "Storage Stats")
        recent_paths = settings.value("recent_paths", [])
        
        # Convert from QVariant if necessary
        if isinstance(recent_paths, str):
            recent_paths = [recent_paths]
        elif not isinstance(recent_paths, list):
            recent_paths = []
        
        # Add to the beginning of the list and remove duplicates
        if path in recent_paths:
            recent_paths.remove(path)
        
        recent_paths.insert(0, path)
        
        # Limit to 10 recent paths
        recent_paths = recent_paths[:10]
        
        settings.setValue("recent_paths", recent_paths)

    def _check_for_partial_scans(self):
        """Check for partial scans at startup and offer to resume"""
        # Delay this check to allow the main window to show first
        QTimer.singleShot(1000, self._delayed_check_for_partial_scans)

    def _delayed_check_for_partial_scans(self):
        """Delayed check for partial scans"""
        partial_scans = self._get_partial_scans()
        
        if not partial_scans:
            return
        
        # If there's only one partial scan, ask if the user wants to resume it
        if len(partial_scans) == 1:
            path = list(partial_scans.keys())[0]
            info = partial_scans[path]
            formatted_time = info.get("formatted_time", "Unknown")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Resume Scan")
            msg_box.setText(f"A partially completed scan was found for:\n{path}\n\nInterrupted at: {formatted_time}")
            msg_box.setInformativeText("Would you like to resume this scan?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self._start_scan(path, resume=True)
        else:
            # If there are multiple partial scans, inform the user they can resume from the menu
            QMessageBox.information(
                self,
                "Partial Scans Available",
                f"There are {len(partial_scans)} partially completed scans available to resume.\n\nYou can resume them from the File > Resume Scan menu."
            )

    def _get_partial_scans(self):
        """Get a list of partial scans that can be resumed"""
        partial_scans = {}
        
        # Check for special folders
        for path in self._get_common_directories():
            info = self.scanner.has_partial_scan(path)
            if info:
                partial_scans[path] = info
        
        # Check for recent paths from settings
        recent_paths = self._get_recent_paths()
        for path in recent_paths:
            if path not in partial_scans:
                info = self.scanner.has_partial_scan(path)
                if info:
                    partial_scans[path] = info
        
        return partial_scans

    def _get_common_directories(self):
        """Get a list of common directories to check for partial scans"""
        directories = [
            os.path.expanduser("~"),  # Home directory
            "/",  # Root
        ]
        
        # Add additional directories like Documents, Downloads, etc.
        home = os.path.expanduser("~")
        for dir_name in ["Documents", "Downloads", "Pictures", "Music", "Movies", "Desktop"]:
            path = os.path.join(home, dir_name)
            if os.path.isdir(path):
                directories.append(path)
        
        return directories

    def _get_recent_paths(self):
        """Get a list of recently scanned paths from settings"""
        settings = QSettings("Storage Stats", "Storage Stats")
        recent_paths = settings.value("recent_paths", [])
        
        # Convert from QVariant if necessary
        if isinstance(recent_paths, str):
            recent_paths = [recent_paths]
        
        return recent_paths

    def _refresh_view(self):
        """Refresh all views with current scan results"""
        # Get the current tab
        current_tab = self.tab_widget.currentWidget()
        
        # Update current tab first
        if hasattr(current_tab, 'update_view') and callable(current_tab.update_view):
            current_tab.update_view(self.scan_results, self.analyzer)
        
        # Update other tabs in the background (for responsiveness)
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) != current_tab:
                tab = self.tab_widget.widget(i)
                if hasattr(tab, 'update_view') and callable(tab.update_view):
                    # Use a small delay to avoid freezing the UI
                    QTimer.singleShot(100 * i, lambda t=tab: t.update_view(self.scan_results, self.analyzer))
    
    def _load_settings(self):
        """Load settings from QSettings"""
        # Implement loading settings from QSettings
        pass

    def _export_report(self):
        """Export scan results to a file"""
        if not self.scan_results:
            return
        
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Report",
            os.path.expanduser("~/storage_stats_report.html"),
            "HTML Files (*.html);;CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if not filename:
            return
        
        try:
            # Determine export format based on selected filter or file extension
            format_type = None
            if filename.lower().endswith(".html"):
                format_type = "html"
            elif filename.lower().endswith(".csv"):
                format_type = "csv"
            elif filename.lower().endswith(".json"):
                format_type = "json"
            else:
                # Default to HTML if no extension specified
                filename += ".html"
                format_type = "html"
            
            if format_type == "html":
                self._export_html_report(filename)
            elif format_type == "csv":
                self._export_csv_report(filename)
            elif format_type == "json":
                self._export_json_report(filename)
            
            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Report exported successfully to {filename}"
            )
            
            # Open the file if it's HTML
            if format_type == "html":
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error exporting report: {str(e)}"
            )
            logger.error(f"Error exporting report: {str(e)}", exc_info=True)

    def _export_html_report(self, filename):
        """Export scan results to an HTML file"""
        if not self.scan_results or not self.current_scan_path:
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Write HTML header
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Storage Stats Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1, h2, h3 {
            color: #444;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .summary {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 15px;
            flex: 1;
            min-width: 200px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            margin-top: 0;
            color: #666;
        }
        .summary-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        .section {
            margin-bottom: 40px;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            color: #777;
            font-size: 14px;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
""")
            
            # Header section
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"""
        <div class="header">
            <h1>Storage Stats Report</h1>
            <p><strong>Scan path:</strong> {self.current_scan_path}</p>
            <p><strong>Generated on:</strong> {scan_time}</p>
        </div>
""")
            
            # Summary section
            total_size = self.scan_results.get("total_size", 0)
            total_files = self.scan_results.get("total_files", 0)
            total_dirs = self.scan_results.get("total_dirs", 0)
            
            f.write("""
        <div class="section">
            <h2>Summary</h2>
            <div class="summary">
""")
            
            f.write(f"""
                <div class="summary-card">
                    <h3>Total Size</h3>
                    <div class="value">{human_readable_size(total_size)}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Files</h3>
                    <div class="value">{total_files:,}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Directories</h3>
                    <div class="value">{total_dirs:,}</div>
                </div>
""")
            
            if total_files > 0:
                avg_file_size = total_size / total_files
                f.write(f"""
                <div class="summary-card">
                    <h3>Average File Size</h3>
                    <div class="value">{human_readable_size(avg_file_size)}</div>
                </div>
""")
            
            f.write("""
            </div>
        </div>
""")
            
            # Largest files section
            largest_files = self.analyzer.get_largest_files(limit=50)
            if largest_files:
                f.write("""
        <div class="section">
            <h2>Largest Files</h2>
            <table>
                <thead>
                    <tr>
                        <th>Path</th>
                        <th>Size</th>
                        <th>Modified</th>
                    </tr>
                </thead>
                <tbody>
""")
                
                for file_info in largest_files:
                    path = file_info.get("path", "")
                    size = file_info.get("size", 0)
                    mtime = file_info.get("mtime", 0)
                    mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S") if mtime else ""
                    
                    f.write(f"""
                    <tr>
                        <td>{path}</td>
                        <td>{human_readable_size(size)}</td>
                        <td>{mtime_str}</td>
                    </tr>
""")
                
                f.write("""
                </tbody>
            </table>
        </div>
""")
            
            # Largest directories section
            largest_dirs = self.analyzer.get_largest_dirs(limit=50)
            if largest_dirs:
                f.write("""
        <div class="section">
            <h2>Largest Directories</h2>
            <table>
                <thead>
                    <tr>
                        <th>Path</th>
                        <th>Size</th>
                        <th>Files</th>
                    </tr>
                </thead>
                <tbody>
""")
                
                for dir_info in largest_dirs:
                    path = dir_info.get("path", "")
                    size = dir_info.get("size", 0)
                    files = dir_info.get("files", 0)
                    
                    f.write(f"""
                    <tr>
                        <td>{path}</td>
                        <td>{human_readable_size(size)}</td>
                        <td>{files:,}</td>
                    </tr>
""")
                
                f.write("""
                </tbody>
            </table>
        </div>
""")
            
            # File types section
            file_types = self.analyzer.get_file_type_distribution()
            if file_types:
                f.write("""
        <div class="section">
            <h2>File Types</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
""")
                
                for file_type, data in sorted(file_types.items(), key=lambda x: x[1]["size"], reverse=True):
                    size = data.get("size", 0)
                    count = data.get("count", 0)
                    percent = (size / total_size * 100) if total_size > 0 else 0
                    
                    f.write(f"""
                    <tr>
                        <td>{file_type}</td>
                        <td>{human_readable_size(size)}</td>
                        <td>{count:,}</td>
                        <td>{percent:.1f}%</td>
                    </tr>
""")
                
                f.write("""
                </tbody>
            </table>
        </div>
""")
            
            # Duplicate files section
            duplicate_groups = self.analyzer.get_duplicate_files()
            if duplicate_groups:
                f.write("""
        <div class="section">
            <h2>Duplicate Files</h2>
""")
                
                # Calculate total wasted space
                wasted_space = sum(
                    (len(files) - 1) * files[0].get("size", 0)
                    for files in duplicate_groups.values()
                )
                
                f.write(f"""
            <p><strong>Total duplicate groups:</strong> {len(duplicate_groups)}</p>
            <p><strong>Wasted space:</strong> {human_readable_size(wasted_space)}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Size</th>
                        <th>Count</th>
                        <th>Paths</th>
                    </tr>
                </thead>
                <tbody>
""")
                
                # Sort duplicate groups by wasted space
                sorted_groups = sorted(
                    duplicate_groups.items(),
                    key=lambda x: (len(x[1]) - 1) * x[1][0].get("size", 0),
                    reverse=True
                )
                
                for hash_key, files in sorted_groups[:50]:  # Limit to 50 groups
                    if len(files) < 2:
                        continue
                    
                    size = files[0].get("size", 0)
                    count = len(files)
                    wasted = (count - 1) * size
                    
                    paths = "<br>".join(f.get("path", "") for f in files)
                    
                    f.write(f"""
                    <tr>
                        <td>{human_readable_size(size)}<br><small>({human_readable_size(wasted)} wasted)</small></td>
                        <td>{count}</td>
                        <td>{paths}</td>
                    </tr>
""")
                
                f.write("""
                </tbody>
            </table>
        </div>
""")
            
            # Footer
            f.write("""
        <div class="footer">
            <p>Generated by Storage Stats - Disk Space Analyzer</p>
        </div>
    </div>
</body>
</html>
""")

    def _export_csv_report(self, filename):
        """Export scan results to a CSV file"""
        if not self.scan_results or not self.current_scan_path:
            return
        
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["Storage Stats Report"])
            writer.writerow(["Scan Path", self.current_scan_path])
            writer.writerow(["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            
            # Write summary
            total_size = self.scan_results.get("total_size", 0)
            total_files = self.scan_results.get("total_files", 0)
            total_dirs = self.scan_results.get("total_dirs", 0)
            
            writer.writerow(["Summary"])
            writer.writerow(["Total Size", human_readable_size(total_size)])
            writer.writerow(["Total Files", total_files])
            writer.writerow(["Total Directories", total_dirs])
            
            if total_files > 0:
                avg_file_size = total_size / total_files
                writer.writerow(["Average File Size", human_readable_size(avg_file_size)])
            
            writer.writerow([])
            
            # Write largest files
            largest_files = self.analyzer.get_largest_files(limit=50)
            if largest_files:
                writer.writerow(["Largest Files"])
                writer.writerow(["Path", "Size", "Modified"])
                
                for file_info in largest_files:
                    path = file_info.get("path", "")
                    size = human_readable_size(file_info.get("size", 0))
                    mtime = file_info.get("mtime", 0)
                    mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S") if mtime else ""
                    
                    writer.writerow([path, size, mtime_str])
            
            writer.writerow([])
            
            # Write largest directories
            largest_dirs = self.analyzer.get_largest_dirs(limit=50)
            if largest_dirs:
                writer.writerow(["Largest Directories"])
                writer.writerow(["Path", "Size", "Files"])
                
                for dir_info in largest_dirs:
                    path = dir_info.get("path", "")
                    size = human_readable_size(dir_info.get("size", 0))
                    files = dir_info.get("files", 0)
                    
                    writer.writerow([path, size, files])
            
            writer.writerow([])
            
            # Write file types
            file_types = self.analyzer.get_file_type_distribution()
            if file_types:
                writer.writerow(["File Types"])
                writer.writerow(["Type", "Size", "Count", "Percentage"])
                
                for file_type, data in sorted(file_types.items(), key=lambda x: x[1]["size"], reverse=True):
                    size = human_readable_size(data.get("size", 0))
                    count = data.get("count", 0)
                    percent = (data.get("size", 0) / total_size * 100) if total_size > 0 else 0
                    
                    writer.writerow([file_type, size, count, f"{percent:.1f}%"])

    def _export_json_report(self, filename):
        """Export scan results to a JSON file"""
        if not self.scan_results or not self.current_scan_path:
            return
        
        import json
        
        # Create a report object with all the data
        report = {
            "scan_path": self.current_scan_path,
            "generated_on": datetime.now().isoformat(),
            "summary": {
                "total_size": self.scan_results.get("total_size", 0),
                "total_size_human": human_readable_size(self.scan_results.get("total_size", 0)),
                "total_files": self.scan_results.get("total_files", 0),
                "total_dirs": self.scan_results.get("total_dirs", 0)
            }
        }
        
        # Add average file size if we have files
        total_files = self.scan_results.get("total_files", 0)
        if total_files > 0:
            avg_file_size = self.scan_results.get("total_size", 0) / total_files
            report["summary"]["average_file_size"] = avg_file_size
            report["summary"]["average_file_size_human"] = human_readable_size(avg_file_size)
        
        # Add largest files
        largest_files = self.analyzer.get_largest_files(limit=100)
        if largest_files:
            report["largest_files"] = [
                {
                    "path": file_info.get("path", ""),
                    "size": file_info.get("size", 0),
                    "size_human": human_readable_size(file_info.get("size", 0)),
                    "mtime": file_info.get("mtime", 0),
                    "mtime_human": datetime.fromtimestamp(file_info.get("mtime", 0)).isoformat() if file_info.get("mtime", 0) else None
                }
                for file_info in largest_files
            ]
        
        # Add largest directories
        largest_dirs = self.analyzer.get_largest_dirs(limit=100)
        if largest_dirs:
            report["largest_directories"] = [
                {
                    "path": dir_info.get("path", ""),
                    "size": dir_info.get("size", 0),
                    "size_human": human_readable_size(dir_info.get("size", 0)),
                    "files": dir_info.get("files", 0)
                }
                for dir_info in largest_dirs
            ]
        
        # Add file types
        file_types = self.analyzer.get_file_type_distribution()
        if file_types:
            report["file_types"] = {
                file_type: {
                    "size": data.get("size", 0),
                    "size_human": human_readable_size(data.get("size", 0)),
                    "count": data.get("count", 0),
                    "percentage": (data.get("size", 0) / self.scan_results.get("total_size", 1) * 100)
                }
                for file_type, data in file_types.items()
            }
        
        # Add duplicate files (summarized)
        duplicate_groups = self.analyzer.get_duplicate_files()
        if duplicate_groups:
            # Calculate total wasted space
            wasted_space = sum(
                (len(files) - 1) * files[0].get("size", 0)
                for files in duplicate_groups.values()
            )
            
            report["duplicates"] = {
                "total_groups": len(duplicate_groups),
                "wasted_space": wasted_space,
                "wasted_space_human": human_readable_size(wasted_space),
                "groups": [
                    {
                        "hash": hash_key,
                        "size": files[0].get("size", 0),
                        "size_human": human_readable_size(files[0].get("size", 0)),
                        "count": len(files),
                        "wasted_space": (len(files) - 1) * files[0].get("size", 0),
                        "wasted_space_human": human_readable_size((len(files) - 1) * files[0].get("size", 0)),
                        "files": [f.get("path", "") for f in files]
                    }
                    for hash_key, files in sorted(
                        duplicate_groups.items(),
                        key=lambda x: (len(x[1]) - 1) * x[1][0].get("size", 0),
                        reverse=True
                    )
                    if len(files) >= 2
                ][:100]  # Limit to 100 groups
            }
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2) 

    def _show_shortcuts_dialog(self):
        """Show the keyboard shortcuts dialog"""
        ShortcutsDialog.show_dialog(self)
    
    def _show_filter_dialog(self):
        """Show the filter customization dialog"""
        # Get current filters if any
        current_filters = self._get_current_filters()
        
        # Show dialog
        filters = FilterDialog.get_filters_dialog(self, current_filters)
        
        if filters:
            # Apply the new filters
            self._apply_filters(filters)
    
    def _get_current_filters(self):
        """Get the current filter settings"""
        # This would typically get filters from settings or state
        return {}
    
    def _apply_filters(self, filters):
        """Apply the selected filters to the current view"""
        # Store filters in settings
        self.settings.setValue("filters", filters)
        
        # Apply to current view if it supports filters
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'apply_filters') and callable(current_tab.apply_filters):
            current_tab.apply_filters(filters)
    
    def _zoom_in(self):
        """Zoom in the current view"""
        # This method could adjust font size or scale factor in views
        pass
    
    def _zoom_out(self):
        """Zoom out the current view"""
        # This method could adjust font size or scale factor in views
        pass
    
    def _zoom_reset(self):
        """Reset zoom level in the current view"""
        # This method could reset font size or scale factor to default
        pass
    
    def _toggle_fullscreen(self, checked):
        """Toggle fullscreen mode"""
        if checked:
            self.showFullScreen()
        else:
            self.showNormal()

    def scan_directory(self, directory):
        """Scan the specified directory - called from main.py"""
        if os.path.exists(directory) and os.path.isdir(directory):
            self._start_scan(directory)
        else:
            logger.error(f"Invalid directory path: {directory}")
            QMessageBox.warning(
                self,
                "Invalid Directory",
                f"The directory '{directory}' does not exist or is not a directory."
            )

    def _select_directory(self):
        """Open directory selection dialog and start scan"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Scan",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self._start_scan(directory)

    def _show_resume_dialog(self):
        """Show dialog to resume a previous scan"""
        partial_scans = self._get_partial_scans()
        
        if not partial_scans:
            QMessageBox.information(
                self,
                "No Partial Scans",
                "No partial scans were found that can be resumed."
            )
            return
            
        # If there's only one partial scan, ask if the user wants to resume it
        if len(partial_scans) == 1:
            path = list(partial_scans.keys())[0]
            info = partial_scans[path]
            formatted_time = info.get("formatted_time", "Unknown")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Resume Scan")
            msg_box.setText(f"Resume the following partial scan?\n\nPath: {path}\nInterrupted at: {formatted_time}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self._start_scan(path, resume=True)
        else:
            # If there are multiple partial scans, show a dialog to select one
            dialog = QDialog(self)
            dialog.setWindowTitle("Resume Scan")
            dialog.setMinimumWidth(500)
            
            layout = QVBoxLayout(dialog)
            layout.addWidget(QLabel("Select a partial scan to resume:"))
            
            list_widget = QListWidget()
            for path, info in partial_scans.items():
                formatted_time = info.get("formatted_time", "Unknown")
                item = QListWidgetItem(f"{path} (Interrupted at: {formatted_time})")
                item.setData(Qt.ItemDataRole.UserRole, path)
                list_widget.addItem(item)
            
            layout.addWidget(list_widget)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec() == QDialog.DialogCode.Accepted and list_widget.currentItem():
                path = list_widget.currentItem().data(Qt.ItemDataRole.UserRole)
                self._start_scan(path, resume=True)
    
    def _stop_scan(self):
        """Stop the current scan"""
        if not self.scan_in_progress:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            "Are you sure you want to stop the current scan?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scanner._stop_requested = True
            self.status_bar.showMessage("Stopping scan...")
    
    def _show_settings_dialog(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Apply settings
            self._load_settings()
    
    def _show_about_dialog(self):
        """Show the about dialog"""
        dialog = AboutDialog(self)
        dialog.exec() 