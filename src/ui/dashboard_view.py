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
        scan_button.setStatusTip("Scan a directory for storage analysis")
        scan_button.setToolTip("Scan a directory for storage analysis")
        
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
        recommendations_frame.setObjectName("recommendationsFrame")  # Add an object name for styling
        recommendations_layout = QVBoxLayout(recommendations_frame)
        
        recommendations_label = QLabel("Quick Recommendations")
        recommendations_label.setFont(largest_files_font)  # Reuse font
        recommendations_label.setObjectName("recommendationsLabel")  # Add an object name for styling
        
        self.recommendations_list = QLabel("Scan your disk to get recommendations")
        self.recommendations_list.setWordWrap(True)
        self.recommendations_list.setTextFormat(Qt.TextFormat.RichText)
        self.recommendations_list.setObjectName("recommendationsList")  # Add an object name for styling
        
        recommendations_layout.addWidget(recommendations_label)
        recommendations_layout.addWidget(self.recommendations_list)
        
        dashboard_layout.addWidget(recommendations_frame)
        
        # Apply some CSS styling
        self.setStyleSheet("""
            QFrame#recommendationsFrame {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QLabel#recommendationsLabel {
                color: #333;
                padding: 5px;
            }
            QLabel#recommendationsList {
                color: #333;
            }
        """)
        
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
            html = "<table width='100%' style='color:#333; border-collapse:collapse;'>"
            html += "<tr><th align='left' style='padding:8px; border-bottom:1px solid #ddd;'>File</th><th align='right' style='padding:8px; border-bottom:1px solid #ddd;'>Size</th></tr>"
            for i, file_info in enumerate(largest_files):
                # Alternate row colors
                bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
                html += f"<tr style='background-color:{bg_color}; color:#333;'>"
                # Use filename if available, otherwise use the basename from path
                filename = file_info.get('filename', os.path.basename(file_info.get('path', '')))
                html += f"<td style='padding:8px; border-bottom:1px solid #ddd;'>{filename}</td>"
                
                # Force size display in GB instead of using the auto-generated size_human
                file_size = file_info.get('size', 0)
                html += f"<td align='right' style='padding:8px; border-bottom:1px solid #ddd;'>{human_readable_size(file_size, preferred_unit='GB')}</td>"
                
                html += "</tr>"
            html += "</table>"
            self.largest_files_list.setText(html)
        else:
            self.largest_files_list.setText("<p style='color:#333;'>No files found</p>")
        
        # Update largest directories
        largest_dirs = analyzer.get_largest_dirs(limit=10)
        if largest_dirs:
            html = "<table width='100%' style='color:#333; border-collapse:collapse;'>"
            html += "<tr><th align='left' style='padding:8px; border-bottom:1px solid #ddd;'>Directory</th><th align='right' style='padding:8px; border-bottom:1px solid #ddd;'>Size</th></tr>"
            for i, dir_info in enumerate(largest_dirs):
                # Alternate row colors
                bg_color = "#f0f0f0" if i % 2 == 0 else "#ffffff"
                html += f"<tr style='background-color:{bg_color}; color:#333;'>"
                # Get the directory name from the path
                dirname = os.path.basename(dir_info.get('path', '')) or dir_info.get('path', '')
                html += f"<td style='padding:8px; border-bottom:1px solid #ddd;'>{dirname}</td>"
                
                # Force size display in GB instead of using the auto-generated size_human
                dir_size = dir_info.get('size', 0)
                html += f"<td align='right' style='padding:8px; border-bottom:1px solid #ddd;'>{human_readable_size(dir_size, preferred_unit='GB')}</td>"
                
                html += "</tr>"
            html += "</table>"
            self.largest_dirs_list.setText(html)
        else:
            self.largest_dirs_list.setText("<p style='color:#333;'>No directories found</p>")
        
        # Update recommendations
        recommendations = analyzer.get_recommendations()
        if recommendations:
            html = """
            <style>
                .recommendation-item {
                    margin-bottom: 15px;
                    padding: 12px;
                    background-color: #e9f5ff;
                    border-left: 4px solid #2196F3;
                    border-radius: 4px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .recommendation-title {
                    font-weight: bold;
                    color: #0d47a1;
                    font-size: 15px;
                    margin-bottom: 8px;
                }
                .recommendation-savings {
                    color: #2e7d32;
                    font-weight: bold;
                    display: inline-block;
                    background-color: #e8f5e9;
                    padding: 2px 6px;
                    border-radius: 3px;
                    margin-right: 5px;
                }
                .recommendation-description {
                    color: #333;
                    line-height: 1.4;
                }
            </style>
            """
            
            for rec in recommendations[:3]:  # Show top 3 recommendations
                # Access the correct property names in the recommendation objects
                title = rec.get('title', 'Unknown recommendation')
                description = rec.get('description', 'No description available')
                
                # Force savings display in GB if available
                savings = rec.get('savings', 0)
                savings_human = rec.get('savings_human', human_readable_size(savings, preferred_unit='GB') if savings else '')
                
                # Include the potential savings in the display if available
                html += '<div class="recommendation-item">'
                html += f'<div class="recommendation-title">{title}</div>'
                
                if savings_human and 'Found' in description:
                    # Split description to insert savings badge
                    parts = description.split(': ', 1)
                    if len(parts) == 2:
                        html += f'<div class="recommendation-description">{parts[0]}: <span class="recommendation-savings">{savings_human}</span> {parts[1]}</div>'
                    else:
                        html += f'<div class="recommendation-description"><span class="recommendation-savings">{savings_human}</span> {description}</div>'
                else:
                    html += f'<div class="recommendation-description">{description}</div>'
                
                html += '</div>'
            
            self.recommendations_list.setText(html)
        else:
            self.recommendations_list.setText("""
            <div style="color:#333; padding: 15px; text-align: center; background-color: #f5f5f5; border-radius: 4px;">
                No recommendations available at this time
            </div>
            """) 