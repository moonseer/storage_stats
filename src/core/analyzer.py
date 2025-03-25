#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Data analyzer module for processing scan results
"""

import os
import logging
import time
from collections import defaultdict
from datetime import datetime
import hashlib
import concurrent.futures

from src.utils.helpers import human_readable_size, get_file_age_category, categorize_file_by_type

logger = logging.getLogger("StorageStats.Analyzer")

class DataAnalyzer:
    """
    Analyzes scan results to provide insights about disk usage
    """
    
    def __init__(self):
        """Initialize the DataAnalyzer"""
        self.scan_results = None
        self.duplicate_files = {}
        self.file_types = {}
        self.largest_files = []
        self.largest_dirs = []
        self.oldest_files = []
        self.newest_files = []
        self.empty_dirs = []
        self.file_age_distribution = {}
    
    def set_scan_results(self, scan_results):
        """
        Set the scan results to analyze
        
        Args:
            scan_results (dict): Dictionary containing scan results
        """
        self.scan_results = scan_results
        
        # Reset analysis results
        self.duplicate_files = {}
        self.file_types = {}
        self.largest_files = []
        self.largest_dirs = []
        self.oldest_files = []
        self.newest_files = []
        self.empty_dirs = []
        self.file_age_distribution = {}
        
        # Analyze data
        if scan_results:
            self._analyze_data()
    
    def _analyze_data(self):
        """Analyze the scan results to extract insights"""
        if not self.scan_results:
            logger.warning("No scan results to analyze")
            return
        
        logger.info("Starting data analysis...")
        start_time = time.time()
        
        # Analyze file types and extensions
        self._analyze_file_types()
        
        # Find duplicate files
        self._find_duplicate_files()
        
        # Find largest files
        self._find_largest_files()
        
        # Find largest directories
        self._find_largest_dirs()
        
        # Analyze file age
        self._analyze_file_age()
        
        # Find empty directories
        self._find_empty_dirs()
        
        end_time = time.time()
        logger.info(f"Data analysis completed in {end_time - start_time:.2f} seconds")
    
    def _analyze_file_types(self):
        """Analyze file types and extensions"""
        if not self.scan_results or 'files' not in self.scan_results:
            return
        
        self.file_types = defaultdict(lambda: {'count': 0, 'size': 0, 'size_human': '', 'percentage': 0.0})
        total_size = self.scan_results.get('total_size', 0)
        
        # Count and sum up sizes for each file extension
        for file_path, file_info in self.scan_results.get('files', {}).items():
            ext = os.path.splitext(file_path)[1].lower()
            if not ext:
                ext = "[No Extension]"
            
            self.file_types[ext]['count'] += 1
            self.file_types[ext]['size'] += file_info.get('size', 0)
        
        # Calculate percentages and human-readable sizes
        for ext, info in self.file_types.items():
            info['size_human'] = human_readable_size(info['size'])
            if total_size > 0:
                info['percentage'] = (info['size'] / total_size) * 100
            else:
                info['percentage'] = 0.0
    
    def _find_duplicate_files(self):
        """Find duplicate files based on file size and hash"""
        if not self.scan_results or 'files' not in self.scan_results:
            return
        
        # Group files by size first (potential duplicates must have the same size)
        size_groups = defaultdict(list)
        for file_path, file_info in self.scan_results.get('files', {}).items():
            size = file_info.get('size', 0)
            # Skip empty files
            if size > 0:
                size_groups[size].append((file_path, file_info))
        
        # For each size group with more than one file, check hashes
        self.duplicate_files = {}
        
        for size, files in size_groups.items():
            if len(files) < 2:
                continue
            
            # Group by hash
            hash_groups = defaultdict(list)
            for file_path, file_info in files:
                file_hash = file_info.get('hash', None)
                if file_hash:
                    hash_groups[file_hash].append((file_path, file_info))
            
            # Add groups with more than one file to duplicates
            for file_hash, duplicate_files in hash_groups.items():
                if len(duplicate_files) > 1:
                    # Calculate wasted space (size * (count - 1))
                    file_size = duplicate_files[0][1].get('size', 0)
                    wasted_space = file_size * (len(duplicate_files) - 1)
                    
                    # Store duplicate group with paths and metadata
                    self.duplicate_files[file_hash] = {
                        'size': file_size,
                        'count': len(duplicate_files),
                        'wasted_space': wasted_space,
                        'files': [
                            {
                                'path': file_path,
                                'mtime': file_info.get('mtime', 0),
                                'mtime_str': datetime.fromtimestamp(file_info.get('mtime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                                'atime': file_info.get('atime', 0)
                            }
                            for file_path, file_info in duplicate_files
                        ]
                    }
    
    def _find_largest_files(self, limit=100):
        """Find the largest files in the scan results"""
        if not self.scan_results or 'files' not in self.scan_results:
            return
        
        # Convert files dict to list of tuples (path, size)
        files_with_size = [(path, info.get('size', 0)) 
                          for path, info in self.scan_results.get('files', {}).items()]
        
        # Sort by size (descending) and get top 'limit'
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        largest = files_with_size[:limit]
        
        # Format the results
        self.largest_files = [
            {
                'path': path,
                'size': size,
                'size_human': human_readable_size(size),
                'ext': os.path.splitext(path)[1].lower(),
                'filename': os.path.basename(path)
            }
            for path, size in largest
        ]
    
    def _find_largest_dirs(self, limit=100):
        """Find the largest directories in the scan results"""
        if not self.scan_results or 'dirs' not in self.scan_results:
            return
        
        # Convert dirs dict to list of tuples (path, size)
        dirs_with_size = [(path, info.get('size', 0)) 
                         for path, info in self.scan_results.get('dirs', {}).items()]
        
        # Sort by size (descending) and get top 'limit'
        dirs_with_size.sort(key=lambda x: x[1], reverse=True)
        largest = dirs_with_size[:limit]
        
        # Format the results
        self.largest_dirs = [
            {
                'path': path,
                'size': size,
                'size_human': human_readable_size(size),
                'file_count': self.scan_results.get('dirs', {}).get(path, {}).get('file_count', 0),
                'dir_count': self.scan_results.get('dirs', {}).get(path, {}).get('dir_count', 0)
            }
            for path, size in largest
        ]
    
    def _analyze_file_age(self):
        """Analyze file age distribution and find oldest/newest files"""
        if not self.scan_results or 'files' not in self.scan_results:
            return
        
        # Initialize age distribution counters
        self.file_age_distribution = {
            "Last week": {"count": 0, "size": 0},
            "Last month": {"count": 0, "size": 0},
            "Last quarter": {"count": 0, "size": 0},
            "Last year": {"count": 0, "size": 0},
            "1-2 years": {"count": 0, "size": 0},
            "Older than 2 years": {"count": 0, "size": 0}
        }
        
        # Collect file modification times
        files_with_mtime = []
        for file_path, file_info in self.scan_results.get('files', {}).items():
            mtime = file_info.get('mtime', 0)
            size = file_info.get('size', 0)
            
            # Skip files with invalid mtime
            if mtime <= 0:
                continue
            
            files_with_mtime.append((file_path, mtime, size))
            
            # Update age distribution
            age_category = get_file_age_category(mtime)
            self.file_age_distribution[age_category]["count"] += 1
            self.file_age_distribution[age_category]["size"] += size
        
        # Add human-readable sizes to age distribution
        for category, data in self.file_age_distribution.items():
            data["size_human"] = human_readable_size(data["size"])
        
        # Find oldest files
        files_with_mtime.sort(key=lambda x: x[1])
        oldest = files_with_mtime[:100]
        
        self.oldest_files = [
            {
                'path': path,
                'mtime': mtime,
                'mtime_str': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': size,
                'size_human': human_readable_size(size),
                'filename': os.path.basename(path)
            }
            for path, mtime, size in oldest
        ]
        
        # Find newest files
        files_with_mtime.sort(key=lambda x: x[1], reverse=True)
        newest = files_with_mtime[:100]
        
        self.newest_files = [
            {
                'path': path,
                'mtime': mtime,
                'mtime_str': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': size,
                'size_human': human_readable_size(size),
                'filename': os.path.basename(path)
            }
            for path, mtime, size in newest
        ]
    
    def _find_empty_dirs(self):
        """Find empty directories in the scan results"""
        if not self.scan_results or 'dirs' not in self.scan_results:
            return
        
        self.empty_dirs = []
        for dir_path, dir_info in self.scan_results.get('dirs', {}).items():
            if dir_info.get('file_count', 0) == 0 and dir_info.get('dir_count', 0) == 0:
                self.empty_dirs.append(dir_path)
    
    def get_duplicate_files(self):
        """
        Get duplicate files found in the scan
        
        Returns:
            dict: Dictionary of duplicate file groups
        """
        return self.duplicate_files
    
    def get_total_wasted_space(self):
        """
        Get the total wasted space due to duplicate files
        
        Returns:
            int: Total wasted space in bytes
        """
        return sum(group['wasted_space'] for group in self.duplicate_files.values())
    
    def get_file_type_distribution(self):
        """
        Get distribution of files by type/extension
        
        Returns:
            dict: Dictionary of file types and their statistics
        """
        return self.file_types
    
    def get_largest_files(self, limit=10):
        """
        Get the largest files from the scan
        
        Args:
            limit (int): Maximum number of files to return
        
        Returns:
            list: List of dictionaries with file information
        """
        return self.largest_files[:limit]
    
    def get_largest_dirs(self, limit=10):
        """
        Get the largest directories from the scan
        
        Args:
            limit (int): Maximum number of directories to return
        
        Returns:
            list: List of dictionaries with directory information
        """
        return self.largest_dirs[:limit]
    
    def get_oldest_files(self, limit=10):
        """
        Get the oldest files from the scan
        
        Args:
            limit (int): Maximum number of files to return
        
        Returns:
            list: List of dictionaries with file information
        """
        return self.oldest_files[:limit]
    
    def get_newest_files(self, limit=10):
        """
        Get the newest files from the scan
        
        Args:
            limit (int): Maximum number of files to return
        
        Returns:
            list: List of dictionaries with file information
        """
        return self.newest_files[:limit]
    
    def get_empty_dirs(self):
        """
        Get empty directories from the scan
        
        Returns:
            list: List of empty directory paths
        """
        return self.empty_dirs
    
    def get_file_age_distribution(self):
        """
        Get distribution of files by age
        
        Returns:
            dict: Dictionary of age categories and their statistics
        """
        return self.file_age_distribution
    
    def get_recommendations(self, min_duplicate_size=1048576, min_large_file_size=104857600):
        """
        Generate storage optimization recommendations
        
        Args:
            min_duplicate_size (int): Minimum size to consider for duplicate recommendations
            min_large_file_size (int): Minimum size to consider for large file recommendations
        
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        # 1. Duplicate files recommendation
        duplicate_groups = sorted(
            self.duplicate_files.values(), 
            key=lambda x: x['wasted_space'], 
            reverse=True
        )
        large_duplicate_groups = [g for g in duplicate_groups if g['size'] >= min_duplicate_size]
        
        if large_duplicate_groups:
            wasted_space = sum(g['wasted_space'] for g in large_duplicate_groups)
            duplicate_count = sum(g['count'] - 1 for g in large_duplicate_groups)
            
            if wasted_space > 0:
                recommendations.append({
                    'title': 'Remove duplicate files',
                    'savings': wasted_space,
                    'savings_human': human_readable_size(wasted_space),
                    'description': f'Found {duplicate_count} duplicate files wasting {human_readable_size(wasted_space)} of space.'
                })
        
        # 2. Large files recommendation
        large_files = [f for f in self.largest_files if f['size'] >= min_large_file_size]
        if large_files:
            total_size = sum(f['size'] for f in large_files)
            recommendations.append({
                'title': 'Review large files',
                'savings': total_size,
                'savings_human': human_readable_size(total_size),
                'description': f'Found {len(large_files)} files larger than {human_readable_size(min_large_file_size)}.'
            })
        
        # 3. Old files recommendation
        old_files = []
        cutoff_days = 730  # 2 years
        now = time.time()
        
        for file_info in self.oldest_files:
            age_days = (now - file_info['mtime']) / (60 * 60 * 24)
            if age_days > cutoff_days:
                old_files.append(file_info)
        
        if old_files:
            total_size = sum(f['size'] for f in old_files)
            recommendations.append({
                'title': 'Clean up old files',
                'savings': total_size,
                'savings_human': human_readable_size(total_size),
                'description': f'Found {len(old_files)} files not modified in over 2 years.'
            })
        
        # 4. Empty directories recommendation
        if self.empty_dirs:
            recommendations.append({
                'title': 'Remove empty directories',
                'savings': 0,
                'savings_human': human_readable_size(0),
                'description': f'Found {len(self.empty_dirs)} empty directories.'
            })
        
        # 5. Specific file types that might be worth cleaning
        cleanup_extensions = ['.log', '.tmp', '.temp', '.bak', '.cache']
        cleanup_files = []
        cleanup_size = 0
        
        for ext, info in self.file_types.items():
            if ext.lower() in cleanup_extensions:
                cleanup_files.append((ext, info))
                cleanup_size += info['size']
        
        if cleanup_size > 0:
            recommendations.append({
                'title': 'Clean up temporary files',
                'savings': cleanup_size,
                'savings_human': human_readable_size(cleanup_size),
                'description': f'Found temporary and log files taking up {human_readable_size(cleanup_size)}.'
            })
        
        # Sort recommendations by potential savings
        recommendations.sort(key=lambda x: x['savings'], reverse=True)
        
        return recommendations
    
    def get_scan_summary(self):
        """
        Get a summary of the scan results
        
        Returns:
            dict: Dictionary with summary information
        """
        if not self.scan_results:
            return {}
        
        # Get total wasted space from duplicates
        wasted_space = self.get_total_wasted_space()
        
        # Count files by extension category
        ext_categories = {}
        for ext, info in self.file_types.items():
            category = categorize_file_by_type(ext)
            if category not in ext_categories:
                ext_categories[category] = {'count': 0, 'size': 0}
            ext_categories[category]['count'] += info['count']
            ext_categories[category]['size'] += info['size']
        
        # Convert to list and sort by size
        categories_list = [
            {
                'name': category,
                'count': info['count'],
                'size': info['size'],
                'size_human': human_readable_size(info['size'])
            }
            for category, info in ext_categories.items()
        ]
        categories_list.sort(key=lambda x: x['size'], reverse=True)
        
        # Calculate percentage of files by age
        age_data = {}
        total_files = self.scan_results.get('total_files', 0)
        
        for age, info in self.file_age_distribution.items():
            percentage = 0
            if total_files > 0:
                percentage = (info['count'] / total_files) * 100
            
            age_data[age] = {
                'count': info['count'],
                'size': info['size'],
                'size_human': info['size_human'],
                'percentage': percentage
            }
        
        return {
            'total_size': self.scan_results.get('total_size', 0),
            'total_size_human': human_readable_size(self.scan_results.get('total_size', 0)),
            'total_files': self.scan_results.get('total_files', 0),
            'total_dirs': self.scan_results.get('total_dirs', 0),
            'scan_time': self.scan_results.get('scan_time', 0),
            'wasted_space': wasted_space,
            'wasted_space_human': human_readable_size(wasted_space),
            'duplicate_groups': len(self.duplicate_files),
            'duplicate_files': sum(group['count'] for group in self.duplicate_files.values()),
            'empty_dirs': len(self.empty_dirs),
            'file_types': categories_list,
            'age_distribution': age_data
        } 