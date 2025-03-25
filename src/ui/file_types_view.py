#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
File Types view for visualizing storage usage by file type
"""

import os
import logging
from datetime import datetime
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QPushButton, QComboBox, QFrame, QSizePolicy,
    QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPainter, QBrush, QPen

from src.utils.helpers import human_readable_size, categorize_file_by_type

logger = logging.getLogger("StorageStats.FileTypesView")

class PieChartWidget(QWidget):
    """Custom widget for displaying a pie chart"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.data = {}
        self.total = 0
        self.colors = [
            QColor(33, 150, 243),   # Blue
            QColor(76, 175, 80),    # Green
            QColor(255, 152, 0),    # Orange
            QColor(156, 39, 176),   # Purple
            QColor(244, 67, 54),    # Red
            QColor(0, 188, 212),    # Cyan
            QColor(255, 87, 34),    # Deep Orange
            QColor(63, 81, 181),    # Indigo
            QColor(255, 235, 59),   # Yellow
            QColor(121, 85, 72),    # Brown
            QColor(158, 158, 158),  # Grey
            QColor(96, 125, 139)    # Blue Grey
        ]
        
        # Set widget properties
        self.setMinimumSize(QSize(300, 300))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def set_data(self, data, total):
        """Set the data for the pie chart"""
        self.data = data
        self.total = total
        self.update()
    
    def paintEvent(self, event):
        """Paint the pie chart"""
        if not self.data or self.total <= 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate chart dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        
        # Center the chart
        center_x = width / 2
        center_y = height / 2
        radius = size / 2 - 20
        
        # Draw pie segments
        start_angle = 0
        i = 0
        
        for label, value in self.data.items():
            if value > 0:
                # Calculate angle for this segment
                angle = int(360 * (value / self.total))
                
                # Select color
                color = self.colors[i % len(self.colors)]
                i += 1
                
                # Draw segment
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(Qt.GlobalColor.white, 1))
                painter.drawPie(int(center_x - radius), int(center_y - radius),
                               int(radius * 2), int(radius * 2),
                               int(start_angle * 16), int(angle * 16))
                
                # Update start angle for next segment
                start_angle += angle
        
        # Draw center hole for a donut chart effect
        painter.setBrush(QBrush(self.palette().window().color()))
        painter.setPen(Qt.PenStyle.NoPen)
        inner_radius = radius * 0.5
        painter.drawEllipse(int(center_x - inner_radius), int(center_y - inner_radius),
                           int(inner_radius * 2), int(inner_radius * 2))

class BarChartWidget(QWidget):
    """Custom widget for displaying a bar chart"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.data = {}
        self.max_value = 0
        self.colors = [
            QColor(33, 150, 243),   # Blue
            QColor(76, 175, 80),    # Green
            QColor(255, 152, 0),    # Orange
            QColor(156, 39, 176),   # Purple
            QColor(244, 67, 54),    # Red
            QColor(0, 188, 212),    # Cyan
            QColor(255, 87, 34),    # Deep Orange
            QColor(63, 81, 181),    # Indigo
            QColor(255, 235, 59),   # Yellow
            QColor(121, 85, 72),    # Brown
            QColor(158, 158, 158),  # Grey
            QColor(96, 125, 139)    # Blue Grey
        ]
        
        # Set widget properties
        self.setMinimumSize(QSize(300, 200))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def set_data(self, data):
        """Set the data for the bar chart"""
        self.data = data
        self.max_value = max(data.values()) if data else 0
        self.update()
    
    def paintEvent(self, event):
        """Paint the bar chart"""
        if not self.data or self.max_value <= 0:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate chart dimensions
        width = self.width()
        height = self.height()
        
        # Define chart area
        chart_top = 20
        chart_bottom = height - 40
        chart_left = 40
        chart_right = width - 20
        
        # Calculate bar width
        bar_count = len(self.data)
        if bar_count == 0:
            return
        
        available_width = chart_right - chart_left
        bar_width = min(available_width / bar_count * 0.8, 50)
        bar_spacing = bar_width * 0.25
        
        # Draw bars
        x = chart_left
        i = 0
        
        for label, value in self.data.items():
            # Skip if value is zero
            if value <= 0:
                continue
                
            # Calculate bar height
            bar_height = (value / self.max_value) * (chart_bottom - chart_top)
            
            # Select color
            color = self.colors[i % len(self.colors)]
            i += 1
            
            # Draw bar
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            
            bar_rect = Qt.QRectF(x, chart_bottom - bar_height, bar_width, bar_height)
            painter.drawRect(bar_rect)
            
            # Draw label
            painter.save()
            painter.translate(x + bar_width / 2, chart_bottom + 5)
            painter.rotate(-45)
            painter.drawText(0, 0, label)
            painter.restore()
            
            # Move to next bar position
            x += bar_width + bar_spacing
        
        # Draw y-axis
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawLine(chart_left, chart_top, chart_left, chart_bottom)
        painter.drawLine(chart_left, chart_bottom, chart_right, chart_bottom)
        
        # Draw y-axis labels (simplified for demonstration)
        num_labels = 5
        for i in range(num_labels + 1):
            y = chart_bottom - (i / num_labels) * (chart_bottom - chart_top)
            value = (i / num_labels) * self.max_value
            
            # Draw tick mark
            painter.drawLine(chart_left - 5, y, chart_left, y)
            
            # Draw label
            if i > 0:  # Skip zero to avoid overlap with x-axis
                painter.drawText(chart_left - 35, y + 5, f"{int(value)}")

class FileTypesView(QWidget):
    """File Types view for visualizing storage usage by file type"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.file_types = {}
        self.total_size = 0
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create header section
        header_layout = QHBoxLayout()
        
        self.stats_label = QLabel("File Types Distribution")
        stats_font = self.stats_label.font()
        stats_font.setPointSize(12)
        stats_font.setBold(True)
        self.stats_label.setFont(stats_font)
        
        # Group by selector
        group_label = QLabel("Group by:")
        self.group_combo = QComboBox()
        self.group_combo.addItems(["Extension", "Category"])
        self.group_combo.currentIndexChanged.connect(self._on_group_changed)
        
        # Sort by selector
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Size (largest first)", "Count", "Name"])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        
        # Add to header layout
        header_layout.addWidget(self.stats_label)
        header_layout.addStretch()
        header_layout.addWidget(group_label)
        header_layout.addWidget(self.group_combo)
        header_layout.addWidget(sort_label)
        header_layout.addWidget(self.sort_combo)
        
        main_layout.addLayout(header_layout)
        
        # Create chart section
        chart_layout = QHBoxLayout()
        
        # Create pie chart
        self.pie_chart = PieChartWidget()
        chart_layout.addWidget(self.pie_chart)
        
        # Create bar chart
        self.bar_chart = BarChartWidget()
        chart_layout.addWidget(self.bar_chart)
        
        main_layout.addLayout(chart_layout)
        
        # Create table for file types
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Extension", "Count", "Size", "Percentage"])
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)
        
        # Configure header
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        main_layout.addWidget(self.table_widget)
    
    def update_view(self, scan_results, analyzer):
        """Update the view with scan results"""
        if not scan_results:
            return
        
        # Get file type distribution
        self.file_types = analyzer.get_file_type_distribution()
        self.total_size = scan_results.get('total_size', 0)
        
        # Update table with file types
        self._update_table()
        
        # Update charts
        self._update_charts()
    
    def _update_table(self):
        """Update the table with file type data"""
        # Clear existing rows
        self.table_widget.setRowCount(0)
        
        # Get sort field
        sort_field = "size"
        if self.sort_combo.currentIndex() == 1:
            sort_field = "count"
        elif self.sort_combo.currentIndex() == 2:
            sort_field = "name"
        
        # Sort file types
        if sort_field == "name":
            sorted_types = sorted(self.file_types.items())
        else:
            sorted_types = sorted(self.file_types.items(), 
                                 key=lambda x: x[1][sort_field], 
                                 reverse=True)
        
        # Fill table
        for i, (ext, data) in enumerate(sorted_types):
            # Add row
            self.table_widget.insertRow(i)
            
            # Set extension
            ext_item = QTableWidgetItem(ext)
            self.table_widget.setItem(i, 0, ext_item)
            
            # Set count
            count_item = QTableWidgetItem(str(data['count']))
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            count_item.setData(Qt.ItemDataRole.UserRole, data['count'])
            self.table_widget.setItem(i, 1, count_item)
            
            # Set size
            size_item = QTableWidgetItem(data['size_human'])
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            size_item.setData(Qt.ItemDataRole.UserRole, data['size'])
            self.table_widget.setItem(i, 2, size_item)
            
            # Set percentage
            pct_item = QTableWidgetItem(f"{data['percentage']:.2f}%")
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            pct_item.setData(Qt.ItemDataRole.UserRole, data['percentage'])
            self.table_widget.setItem(i, 3, pct_item)
    
    def _update_charts(self):
        """Update charts with file type data"""
        # Get top N file types for charts
        top_n = 10
        
        # Group by selected option
        if self.group_combo.currentIndex() == 0:  # By Extension
            # Sort by size and get top N
            sorted_types = sorted(self.file_types.items(), 
                                 key=lambda x: x[1]['size'], 
                                 reverse=True)[:top_n]
            
            # Extract data for charts
            chart_data = {ext: data['size'] for ext, data in sorted_types}
            
            # Add "Others" category if there are more than top_n types
            if len(self.file_types) > top_n:
                others_size = sum(data['size'] for ext, data in self.file_types.items() 
                                  if ext not in chart_data)
                if others_size > 0:
                    chart_data["Others"] = others_size
        else:  # By Category
            # Group by category
            categories = {}
            for ext, data in self.file_types.items():
                category = categorize_file_by_type(ext)
                if category not in categories:
                    categories[category] = 0
                categories[category] += data['size']
            
            # Sort by size and get top N
            sorted_categories = sorted(categories.items(), 
                                      key=lambda x: x[1], 
                                      reverse=True)[:top_n]
            
            # Extract data for charts
            chart_data = dict(sorted_categories)
            
            # Add "Others" category if there are more than top_n categories
            if len(categories) > top_n:
                others_size = sum(size for cat, size in categories.items() 
                                  if cat not in chart_data)
                if others_size > 0:
                    chart_data["Others"] = others_size
        
        # Update pie chart
        self.pie_chart.set_data(chart_data, self.total_size)
        
        # Update bar chart
        self.bar_chart.set_data(chart_data)
    
    def _on_group_changed(self, index):
        """Handle group by option change"""
        self._update_charts()
    
    def _on_sort_changed(self, index):
        """Handle sort option change"""
        self._update_table() 