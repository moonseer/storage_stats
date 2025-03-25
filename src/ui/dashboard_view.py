#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Dashboard view for displaying overview statistics
"""

import os
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QScrollArea, QSizePolicy, QPushButton,
    QGridLayout, QSpacerItem
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

from src.utils.helpers import human_readable_size, format_timestamp, format_time_delta

logger = logging.getLogger("StorageStats.DashboardView")

class StatsCard(QFrame):
    """A card widget for displaying a statistic"""
    
    def __init__(self, title, value="", icon=None, parent=None):
        super().__init__(parent)
        
        # Set up frame
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(100)
        
        # Set up layout
        layout = QVBoxLayout(self)
        
        # Create title label
        self.title_label = QLabel(title)
        title_font = self.title_label.font()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create value label
        self.value_label = QLabel(value)
        value_font = self.value_label.font()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
    
    def set_value(self, value):
        """Update the value displayed in the card"""
        self.value_label.setText(str(value))

class DashboardView(QWidget):
    """Dashboard view for displaying overview statistics"""
    
    # Define signals
    scan_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for dashboard content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create container widget for scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        
        # Create welcome section for initial state
        self.welcome_frame = QFrame()
        self.welcome_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.welcome_frame.setFrameShadow(QFrame.Shadow.Raised)
        welcome_layout = QVBoxLayout(self.welcome_frame)
        
        welcome_label = QLabel("Welcome to Storage Stats")
        welcome_font = welcome_label.font()
        welcome_font.setPointSize(18)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        intro_label = QLabel(
            "Storage Stats helps you analyze disk usage and identify files that take up space. "
            "Click 'Scan Directory' to begin analyzing a directory."
        )
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        scan_button = QPushButton("Scan Directory")
        scan_button.setMinimumWidth(200)
        scan_button.clicked.connect(self.scan_requested.emit)
        
        welcome_layout.addItem(QSpacerItem(20, 40))
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(intro_label)
        welcome_layout.addItem(QSpacerItem(20, 20))
        welcome_layout.addWidget(scan_button, 0, Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addItem(QSpacerItem(20, 40))
        
        # Add welcome frame to scroll layout
        scroll_layout.addWidget(self.welcome_frame)
        
        # Create dashboard content (initially hidden)
        self.dashboard_content = QWidget()
        self.dashboard_content.setVisible(False)
        dashboard_layout = QVBoxLayout(self.dashboard_content)
        
        # Add header section
        header_layout = QHBoxLayout()
        
        self.path_label = QLabel()
        path_font = self.path_label.font()
        path_font.setPointSize(12)
        path_font.setBold(True)
        self.path_label.setFont(path_font)
        
        self.scan_time_label = QLabel()
        
        header_layout.addWidget(self.path_label)
        header_layout.addStretch()
        header_layout.addWidget(self.scan_time_label)
        
        dashboard_layout.addLayout(header_layout)
        
        # Add summary cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(10)
        
        self.total_size_card = StatsCard("Total Size")
        self.total_files_card = StatsCard("Total Files")
        self.total_dirs_card = StatsCard("Total Directories")
        self.avg_file_size_card = StatsCard("Average File Size")
        
        cards_layout.addWidget(self.total_size_card, 0, 0)
        cards_layout.addWidget(self.total_files_card, 0, 1)
        cards_layout.addWidget(self.total_dirs_card, 1, 0)
        cards_layout.addWidget(self.avg_file_size_card, 1, 1)
        
        dashboard_layout.addLayout(cards_layout)
        
        # Add section for largest files
        largest_files_frame = QFrame()
        largest_files_frame.setFrameShape(QFrame.Shape.StyledPanel)
        largest_files_layout = QVBoxLayout(largest_files_frame)
        
        largest_files_label = QLabel("Largest Files")
        largest_files_font = largest_files_label.font()
        largest_files_font.setPointSize(12)
        largest_files_font.setBold(True)
        largest_files_label.setFont(largest_files_font)
        
        self.largest_files_list = QLabel("No files scanned yet")
        self.largest_files_list.setWordWrap(True)
        self.largest_files_list.setTextFormat(Qt.TextFormat.RichText)
        
        largest_files_layout.addWidget(largest_files_label)
        largest_files_layout.addWidget(self.largest_files_list)
        
        dashboard_layout.addWidget(largest_files_frame)
        
        # Add section for largest directories
        largest_dirs_frame = QFrame()
        largest_dirs_frame.setFrameShape(QFrame.Shape.StyledPanel)
        largest_dirs_layout = QVBoxLayout(largest_dirs_frame)
        
        largest_dirs_label = QLabel("Largest Directories")
        largest_dirs_label.setFont(largest_files_font)  # Reuse font
        
        self.largest_dirs_list = QLabel("No directories scanned yet")
        self.largest_dirs_list.setWordWrap(True)
        self.largest_dirs_list.setTextFormat(Qt.TextFormat.RichText)
        
        largest_dirs_layout.addWidget(largest_dirs_label)
        largest_dirs_layout.addWidget(self.largest_dirs_list)
        
        dashboard_layout.addWidget(largest_dirs_frame)
        
        # Add recommendations section
        recommendations_frame = QFrame()
        recommendations_frame.setFrameShape(QFrame.Shape.StyledPanel)
        recommendations_layout = QVBoxLayout(recommendations_frame)
        
        recommendations_label = QLabel("Quick Recommendations")
        recommendations_label.setFont(largest_files_font)  # Reuse font
        
        self.recommendations_list = QLabel("Scan your disk to get recommendations")
        self.recommendations_list.setWordWrap(True)
        self.recommendations_list.setTextFormat(Qt.TextFormat.RichText)
        
        recommendations_layout.addWidget(recommendations_label)
        recommendations_layout.addWidget(self.recommendations_list)
        
        dashboard_layout.addWidget(recommendations_frame)
        
        # Add dashboard content to scroll layout
        scroll_layout.addWidget(self.dashboard_content)
        scroll_layout.addStretch()
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def update_view(self, scan_results, analyzer):
        """Update the view with scan results"""
        if not scan_results:
            return
        
        # Hide welcome frame and show dashboard content
        self.welcome_frame.setVisible(False)
        self.dashboard_content.setVisible(True)
        
        # Update header
        root_info = scan_results.get('root_info', {})
        root_path = root_info.get('path', '') if isinstance(root_info, dict) else getattr(root_info, 'path', '')
        self.path_label.setText(f"Scan Results: {root_path}")
        self.scan_time_label.setText(f"Scan Time: {format_time_delta(scan_results.get('scan_time', 0))}")
        
        # Update summary cards
        total_size = scan_results.get('total_size', 0)
        total_files = scan_results.get('total_files', 0)
        total_dirs = scan_results.get('total_dirs', 0)
        
        # Use GB as the preferred unit for file sizes
        self.total_size_card.set_value(human_readable_size(total_size, preferred_unit='GB'))
        self.total_files_card.set_value(f"{total_files:,}")
        self.total_dirs_card.set_value(f"{total_dirs:,}")
        
        # Calculate average file size
        avg_file_size = total_size / total_files if total_files > 0 else 0
        # Use MB for average file size to show smaller values better
        self.avg_file_size_card.set_value(human_readable_size(avg_file_size, preferred_unit='MB'))
        
        # Update largest files
        largest_files = analyzer.get_largest_files(limit=10)
        if largest_files:
            html = "<table width='100%'>"
            html += "<tr><th align='left'>File</th><th align='right'>Size</th></tr>"
            for i, file_info in enumerate(largest_files):
                # Alternate row colors
                bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
                html += f"<tr style='background-color:{bg_color};'>"
                html += f"<td>{file_info['name']}</td>"
                html += f"<td align='right'>{file_info['size_human']}</td>"
                html += "</tr>"
            html += "</table>"
            self.largest_files_list.setText(html)
        else:
            self.largest_files_list.setText("No files found")
        
        # Update largest directories
        largest_dirs = analyzer.get_largest_dirs(limit=10)
        if largest_dirs:
            html = "<table width='100%'>"
            html += "<tr><th align='left'>Directory</th><th align='right'>Size</th></tr>"
            for i, dir_info in enumerate(largest_dirs):
                # Alternate row colors
                bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
                html += f"<tr style='background-color:{bg_color};'>"
                html += f"<td>{dir_info['name']}</td>"
                html += f"<td align='right'>{dir_info['size_human']}</td>"
                html += "</tr>"
            html += "</table>"
            self.largest_dirs_list.setText(html)
        else:
            self.largest_dirs_list.setText("No directories found")
        
        # Update recommendations
        recommendations = analyzer.get_recommendations()
        if recommendations:
            html = "<ul>"
            for rec in recommendations[:3]:  # Show top 3 recommendations
                html += f"<li><b>{rec['title']}</b>: {rec['description']}</li>"
            html += "</ul>"
            self.recommendations_list.setText(html)
        else:
            self.recommendations_list.setText("No recommendations available") 