#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Recommendations view for suggesting files that could be removed to free up space
"""

import os
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QHeaderView, 
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QSplitter, QFrame, QScrollArea, QToolButton,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from src.utils.helpers import human_readable_size, format_timestamp

logger = logging.getLogger("StorageStats.RecommendationsView")

class RecommendationCard(QFrame):
    """Card widget for displaying a recommendation"""
    
    def __init__(self, recommendation, parent=None):
        super().__init__(parent)
        
        # Save recommendation data
        self.recommendation = recommendation
        
        # Set up frame
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(100)
        
        # Set up layout
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create header with title and priority indicator
        header_layout = QHBoxLayout()
        
        # Create title label
        title_label = QLabel(self.recommendation.get('title', ''))
        title_font = title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Create savings label
        savings_text = self.recommendation.get('potential_savings_human', 'Unknown')
        savings_label = QLabel(f"Potential Savings: {savings_text}")
        savings_font = savings_label.font()
        savings_font.setBold(True)
        savings_label.setFont(savings_font)
        
        # Add to header layout
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(savings_label)
        
        # Create description label
        description_label = QLabel(self.recommendation.get('description', ''))
        description_label.setWordWrap(True)
        
        # Create details button if there are details available
        details_layout = QHBoxLayout()
        details_layout.addStretch()
        
        if self.recommendation.get('type') in ['duplicate_files', 'old_files', 'temp_files']:
            details_button = QPushButton("View Details")
            details_button.clicked.connect(self._show_details)
            details_layout.addWidget(details_button)
        
        # Add widgets to layout
        layout.addLayout(header_layout)
        layout.addWidget(description_label)
        layout.addLayout(details_layout)
    
    def _show_details(self):
        """Show details for this recommendation"""
        rec_type = self.recommendation.get('type')
        
        # This is a simplified version - in a real app, this would navigate to the appropriate view
        if rec_type == 'duplicate_files':
            QMessageBox.information(
                self,
                "Duplicate Files",
                "This would navigate to the Duplicates tab to show duplicate files."
            )
        elif rec_type == 'old_files':
            QMessageBox.information(
                self,
                "Old Files",
                "This would show a list of old files that haven't been accessed in a long time."
            )
        elif rec_type == 'temp_files':
            QMessageBox.information(
                self,
                "Temporary Files",
                "This would show a list of temporary files that could be safely deleted."
            )

class RecommendationsView(QWidget):
    """Recommendations view for suggesting files that could be removed to free up space"""
    
    # Define signals
    navigate_to_tab = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up instance variables
        self.recommendations = []
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for recommendations
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create container widget for scroll area
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        
        # Add welcome message (for initial state)
        self.welcome_frame = QFrame()
        welcome_layout = QVBoxLayout(self.welcome_frame)
        
        welcome_label = QLabel("Storage Recommendations")
        welcome_font = welcome_label.font()
        welcome_font.setPointSize(16)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        intro_label = QLabel(
            "After scanning your storage, we'll provide smart recommendations to help you "
            "free up space. Run a scan to get personalized suggestions."
        )
        intro_label.setWordWrap(True)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(intro_label)
        
        # Add welcome frame to scroll layout
        self.scroll_layout.addWidget(self.welcome_frame)
        self.scroll_layout.addStretch()
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def update_view(self, scan_results, analyzer):
        """Update the view with scan results"""
        if not scan_results:
            return
        
        # Hide welcome frame
        self.welcome_frame.setVisible(False)
        
        # Get recommendations from analyzer
        self.recommendations = analyzer.get_recommendations()
        
        # Update recommendations list
        self._update_recommendations_list()
    
    def _update_recommendations_list(self):
        """Update the recommendations list"""
        # Clear existing recommendations
        self._clear_recommendations()
        
        # Check if recommendations were found
        if not self.recommendations:
            no_rec_label = QLabel("No recommendations found. Your storage looks good!")
            no_rec_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = no_rec_label.font()
            font.setPointSize(14)
            no_rec_label.setFont(font)
            
            self.scroll_layout.insertWidget(0, no_rec_label)
            self.welcome_frame.setVisible(False)
            return
        
        # Hide welcome frame
        self.welcome_frame.setVisible(False)
        
        # Add header
        header_label = QLabel("Storage Recommendations")
        header_font = header_label.font()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        
        sub_header_label = QLabel(
            "Here are personalized recommendations to help you free up storage space. "
            "Review each suggestion carefully."
        )
        sub_header_label.setWordWrap(True)
        
        self.scroll_layout.insertWidget(0, header_label)
        self.scroll_layout.insertWidget(1, sub_header_label)
        
        # Add recommendation cards
        total_savings = sum(rec.get('potential_savings', 0) for rec in self.recommendations)
        
        savings_label = QLabel(f"Total Potential Savings: {human_readable_size(total_savings)}")
        savings_font = savings_label.font()
        savings_font.setPointSize(12)
        savings_font.setBold(True)
        savings_label.setFont(savings_font)
        savings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_layout.insertWidget(2, savings_label)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.scroll_layout.insertWidget(3, separator)
        
        # Add recommendation cards
        for i, rec in enumerate(self.recommendations):
            card = RecommendationCard(rec)
            self.scroll_layout.insertWidget(4 + i, card)
    
    def _clear_recommendations(self):
        """Clear existing recommendations"""
        # Remove all widgets from scroll layout except welcome frame
        while self.scroll_layout.count() > 2:  # Keep welcome frame and stretch
            item = self.scroll_layout.takeAt(0)
            if item.widget() != self.welcome_frame:
                if item.widget():
                    item.widget().deleteLater() 