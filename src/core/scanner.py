#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Scanner module for traversing file system and collecting data
"""

import os
import time
import logging
import concurrent.futures
from datetime import datetime
import hashlib
from collections import defaultdict
from pathlib import Path
import threading
import queue
import sys
from functools import partial
import json
import pickle

from PyQt6.QtCore import QObject, pyqtSignal

from src.utils.helpers import human_readable_size, get_file_hash, is_path_excluded, categorize_file_by_type

logger = logging.getLogger("StorageStats.Scanner")

class FileInfo:
    """Class representing file information"""
    
    def __init__(self, path, size=0, mtime=0, atime=0, ctime=0, hash=None):
        """
        Initialize FileInfo
        
        Args:
            path (str): File path
            size (int): File size in bytes
            mtime (float): Modification time as Unix timestamp
            atime (float): Access time as Unix timestamp
            ctime (float): Creation time as Unix timestamp
            hash (str): File hash value
        """
        self.path = path
        self.size = size
        self.mtime = mtime
        self.atime = atime
        self.ctime = ctime
        self.hash = hash
    
    def to_dict(self):
        """Convert FileInfo to dictionary"""
        return {
            'size': self.size,
            'mtime': self.mtime,
            'atime': self.atime,
            'ctime': self.ctime,
            'hash': self.hash
        }

class DiskScanner(QObject):
    """
    Scanner class for traversing file system and collecting data
    Emits signals for progress tracking
    """
    # Define signals
    scan_started = pyqtSignal(str)
    scan_progress = pyqtSignal(int, int, str)  # current, total, current_path
    scan_finished = pyqtSignal(dict)
    scan_error = pyqtSignal(str)
    
    def __init__(self, max_threads=4):
        """
        Initialize DiskScanner
        
        Args:
            max_threads (int): Maximum number of threads to use for scanning
        """
        super().__init__()
        
        # Scanner configuration
        self.max_threads = max(1, min(32, max_threads))  # Limit threads between 1 and 32
        self.calculate_hashes = True
        self.hash_method = 'quick'  # 'quick' or 'full'
        self.skip_hidden = True
        self.follow_symlinks = False
        self.exclude_paths = []
        
        # Scan data
        self.root_path = ""
        self.scan_results = {}
        self.file_count = 0
        self.dir_count = 0
        self.total_size = 0
        self.errors = []
        
        # Internal state
        self._stop_requested = False
        self._mutex = threading.RLock()
        self._scan_queue = queue.Queue()
        self._file_queue = queue.Queue()
        self._paths_to_process = 0
        self._paths_processed = 0
        
        # State variables
        self._running = False
        self._scan_thread = None
        self._directory_workers = []
        self._file_workers = []
        self._root_info = None
        self._total_size = 0
        self._processed_files = 0
        self._total_files = 0
        self._processed_dirs = 0
        self._total_dirs = 0
        self._file_types = {}
        self._file_exts = {}
        self._seen_inodes = set()  # For duplicate detection on Unix
        self._directories = {}
        self._files = {}
        
        # Progress tracking
        self._progress_update_interval = 0.1  # seconds
        self._last_progress_update = 0
        self._current_path = ""
        
        # Cache directory for scan resume
        self._cache_dir = os.path.join(os.path.expanduser("~"), ".storage_stats", "cache")
        os.makedirs(self._cache_dir, exist_ok=True)
        
        # Partial scan state for resume
        self._partial_scan_data = None
        self._partial_scan_path = None
    
    def configure(self, config):
        """
        Configure scanner with user settings
        
        Args:
            config (dict): Configuration dictionary
        """
        if 'max_threads' in config:
            self.max_threads = max(1, min(32, config['max_threads']))
        
        if 'calculate_hashes' in config:
            self.calculate_hashes = config['calculate_hashes']
        
        if 'hash_method' in config:
            self.hash_method = config['hash_method']
        
        if 'skip_hidden' in config:
            self.skip_hidden = config['skip_hidden']
        
        if 'follow_symlinks' in config:
            self.follow_symlinks = config['follow_symlinks']
        
        if 'exclude_paths' in config:
            self.exclude_paths = config['exclude_paths']
        
        logger.info(f"Scanner configured: {config}")
    
    def scan(self, path, is_blocking=False, resume=False):
        """
        Start scanning a directory
        
        Args:
            path (str): Directory path to scan
            is_blocking (bool): If True, scan synchronously and block until complete
            resume (bool): If True, attempt to resume a previous scan
        
        Returns:
            dict: Scan results if is_blocking is True, otherwise None
        """
        if self._running:
            logger.warning("Scan already in progress")
            return None
        
        if not os.path.exists(path):
            error_msg = f"Path does not exist: {path}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)
            return None
        
        if not os.path.isdir(path):
            error_msg = f"Path is not a directory: {path}"
            logger.error(error_msg)
            self.scan_error.emit(error_msg)
            return None
        
        # Reset state
        self._stop_requested = False
        self._running = True
        self.root_path = path
        self.scan_results = {
            'root_path': path,
            'files': {},
            'dirs': {},
            'total_size': 0,
            'total_files': 0,
            'total_dirs': 0,
            'scan_time': 0,
            'errors': []
        }
        self.file_count = 0
        self.dir_count = 0
        self.total_size = 0  # Ensure this is explicitly set to 0
        self.errors = []
        self._paths_to_process = 0
        self._paths_processed = 0
        self._processed_files = 0
        self._total_files = 0
        self._processed_dirs = 0
        self._total_dirs = 0
        self._file_types = {}
        self._file_exts = {}
        self._seen_inodes = set()
        self._directories = {}
        self._files = {}
        self._root_info = None
        
        # Check if resuming a scan
        if resume:
            self._load_partial_scan(path)
        
        # Start the scan
        start_time = time.time()
        
        try:
            if is_blocking:
                # Perform synchronous scan
                self._scan_directory(path)
                self._finalize_scan_results(start_time)
                return self.scan_results
            else:
                # Start asynchronous scan in a separate thread
                self._scan_thread = threading.Thread(
                    target=self._scan_async,
                    args=(path, start_time),
                    daemon=True
                )
                self._scan_thread.start()
                logger.info("Scan thread started for path: %s", path)
                return None
        except Exception as e:
            self._running = False
            error_msg = f"Error starting scan: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.scan_error.emit(error_msg)
            return None
    
    def _scan_async(self, path, start_time):
        """
        Perform asynchronous scan in a separate thread
        
        Args:
            path (str): Directory path to scan
            start_time (float): Scan start time
        """
        try:
            self._scan_directory(path)
            self._finalize_scan_results(start_time)
        except Exception as e:
            logger.exception(f"Error during scan: {e}")
            self.scan_error.emit(f"Error during scan: {e}")
    
    def _scan_directory(self, root_path):
        """
        Perform the actual directory scan
        
        Args:
            root_path (str): Directory path to scan
        """
        logger.info(f"Starting scan of {root_path}")
        
        # Create initial directory task
        self._add_directory_to_queue(root_path)
        
        # Create worker threads for directory processing
        dir_workers = []
        for _ in range(min(self.max_threads, 2)):  # Use at most 2 threads for directory listing
            worker = threading.Thread(target=self._directory_worker)
            worker.daemon = True
            worker.start()
            dir_workers.append(worker)
        
        # Create worker threads for file processing
        file_workers = []
        for _ in range(self.max_threads):
            worker = threading.Thread(target=self._file_worker)
            worker.daemon = True
            worker.start()
            file_workers.append(worker)
        
        # Wait for directory queue to be processed
        self._scan_queue.join()
        
        # Wait for file queue to be processed
        self._file_queue.join()
        
        # Stop workers
        for _ in range(len(dir_workers)):
            self._scan_queue.put(None)  # Signal to terminate
        
        for _ in range(len(file_workers)):
            self._file_queue.put(None)  # Signal to terminate
        
        # Wait for all workers to finish
        for worker in dir_workers:
            worker.join()
        
        for worker in file_workers:
            worker.join()
        
        logger.info(f"Scan completed: {self.file_count} files, {self.dir_count} directories, {human_readable_size(self.total_size)}")
    
    def _add_directory_to_queue(self, dir_path):
        """
        Add a directory to the scan queue
        
        Args:
            dir_path (str): Directory path to add
        """
        with self._mutex:
            self._paths_to_process += 1
        
        self._scan_queue.put(dir_path)
    
    def _directory_worker(self):
        """Worker thread for processing directories"""
        while not self._stop_requested:
            try:
                dir_path = self._scan_queue.get(timeout=0.1)
                
                if dir_path is None:  # Termination signal
                    self._scan_queue.task_done()
                    break
                
                try:
                    self._process_directory(dir_path)
                except Exception as e:
                    logger.error(f"Error processing directory {dir_path}: {e}")
                    with self._mutex:
                        self.errors.append(f"Error processing directory {dir_path}: {e}")
                
                self._scan_queue.task_done()
                
                with self._mutex:
                    self._paths_processed += 1
                    # Emit progress update
                    self.scan_progress.emit(
                        self._paths_processed, 
                        max(self._paths_to_process, 1),  # Avoid division by zero
                        dir_path
                    )
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Directory worker error: {e}")
    
    def _file_worker(self):
        """Worker thread for processing files"""
        while not self._stop_requested:
            try:
                task = self._file_queue.get(timeout=0.1)
                
                if task is None:  # Termination signal
                    self._file_queue.task_done()
                    break
                
                file_path = task
                
                try:
                    self._process_file(file_path)
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    with self._mutex:
                        self.errors.append(f"Error processing file {file_path}: {e}")
                
                self._file_queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"File worker error: {e}")
    
    def _process_directory(self, dir_path):
        """
        Process a directory, adding its contents to the scan queue
        
        Args:
            dir_path (str): Directory path to process
        """
        # Skip excluded paths
        if is_path_excluded(dir_path, self.exclude_paths):
            logger.debug(f"Skipping excluded path: {dir_path}")
            return
        
        # Skip hidden directories if configured
        if self.skip_hidden and os.path.basename(dir_path).startswith('.'):
            logger.debug(f"Skipping hidden directory: {dir_path}")
            return
        
        # Check if it's a symlink
        if os.path.islink(dir_path) and not self.follow_symlinks:
            logger.debug(f"Skipping symlink: {dir_path}")
            return
        
        try:
            # Add directory to results
            with self._mutex:
                self.dir_count += 1
                self.scan_results['dirs'][dir_path] = {
                    'size': 0,
                    'file_count': 0,
                    'dir_count': 0
                }
            
            # List directory contents
            items = os.listdir(dir_path)
            
            # Process each item
            for item_name in items:
                if self._stop_requested:
                    return
                
                item_path = os.path.join(dir_path, item_name)
                
                # Skip excluded paths
                if is_path_excluded(item_path, self.exclude_paths):
                    continue
                
                # Skip hidden files if configured
                if self.skip_hidden and item_name.startswith('.'):
                    continue
                
                # Process directories
                if os.path.isdir(item_path):
                    # Skip symlinks if not following them
                    if os.path.islink(item_path) and not self.follow_symlinks:
                        continue
                    
                    # Add directory to queue
                    self._add_directory_to_queue(item_path)
                    
                    # Increment parent directory's dir count
                    with self._mutex:
                        self.scan_results['dirs'][dir_path]['dir_count'] += 1
                
                # Process files
                elif os.path.isfile(item_path):
                    # Add file to queue
                    self._file_queue.put(item_path)
                    
                    # Increment parent directory's file count
                    with self._mutex:
                        self.scan_results['dirs'][dir_path]['file_count'] += 1
        
        except PermissionError:
            logger.warning(f"Permission denied: {dir_path}")
            with self._mutex:
                self.errors.append(f"Permission denied: {dir_path}")
        
        except Exception as e:
            logger.error(f"Error processing directory {dir_path}: {e}")
            with self._mutex:
                self.errors.append(f"Error processing directory {dir_path}: {e}")
    
    def _process_file(self, file_path):
        """
        Process a file, collecting its information
        
        Args:
            file_path (str): File path to process
        """
        try:
            # Get file stats
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            # Ensure file_size is a standard integer type
            file_size = int(file_size)
            logger.debug(f"Processing file: {file_path}, size: {file_size} bytes")
            
            file_mtime = file_stat.st_mtime
            file_atime = file_stat.st_atime
            file_ctime = file_stat.st_ctime
            
            # Calculate file hash if enabled
            file_hash = None
            if self.calculate_hashes and file_size > 0:
                try:
                    quick_mode = (self.hash_method == 'quick')
                    file_hash = get_file_hash(file_path, algorithm='md5', quick_mode=quick_mode)
                except Exception as e:
                    logger.warning(f"Error calculating hash for {file_path}: {e}")
            
            # Create FileInfo object
            file_info = FileInfo(
                path=file_path,
                size=file_size,
                mtime=file_mtime,
                atime=file_atime,
                ctime=file_ctime,
                hash=file_hash
            )
            
            # Add file to results
            with self._mutex:
                self.file_count += 1
                # Explicitly handle the size addition
                self.total_size = self.total_size + file_size
                logger.debug(f"Added file size: {file_size}, new total: {self.total_size}")
                
                # Store file info with explicit size value
                file_dict = file_info.to_dict()
                self.scan_results['files'][file_path] = file_dict
                
                # Update directory size
                parent_dir = os.path.dirname(file_path)
                while parent_dir and parent_dir in self.scan_results['dirs']:
                    self.scan_results['dirs'][parent_dir]['size'] += file_size
                    parent_dir = os.path.dirname(parent_dir)
        
        except PermissionError:
            logger.warning(f"Permission denied: {file_path}")
            with self._mutex:
                self.errors.append(f"Permission denied: {file_path}")
        
        except FileNotFoundError:
            # File might have been deleted since directory listing
            logger.warning(f"File not found: {file_path}")
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            with self._mutex:
                self.errors.append(f"Error processing file {file_path}: {e}")
    
    def _finalize_scan_results(self, start_time):
        """
        Finalize scan results and emit finished signal
        
        Args:
            start_time (float): Scan start time
        """
        # Calculate scan time
        scan_time = time.time() - start_time
        
        # Update scan results with final values
        # Convert to int to ensure no floating point precision issues
        self.scan_results['total_size'] = int(self.total_size)
        self.scan_results['total_files'] = self.file_count
        self.scan_results['total_dirs'] = self.dir_count
        self.scan_results['scan_time'] = scan_time
        self.scan_results['errors'] = self.errors
        
        logger.info(f"Scan finished in {scan_time:.2f} seconds")
        logger.info(f"Total files: {self.file_count}")
        logger.info(f"Total directories: {self.dir_count}")
        logger.info(f"Total size (bytes): {self.total_size}")
        logger.info(f"Total size (GB): {human_readable_size(self.total_size, preferred_unit='GB')}")
        
        # Emit finished signal with the complete scan results
        self.scan_finished.emit(self.scan_results)
    
    def stop(self):
        """Stop the scanning process"""
        logger.info("Scan stop requested")
        self._stop_requested = True
    
    def is_running(self):
        """Check if scan is currently running"""
        return not self._stop_requested and (self._paths_processed < self._paths_to_process)
    
    def get_progress(self):
        """
        Get current scan progress
        
        Returns:
            tuple: (paths_processed, paths_to_process, progress_percentage)
        """
        with self._mutex:
            paths_processed = self._paths_processed
            paths_to_process = max(self._paths_to_process, 1)  # Avoid division by zero
        
        progress_percentage = min(100, int((paths_processed / paths_to_process) * 100))
        return (paths_processed, paths_to_process, progress_percentage)
    
    def get_results(self):
        """
        Get the scan results
        
        Returns:
            dict: Scan results dictionary
        """
        return self.scan_results 

    def _save_partial_scan(self, path):
        """
        Save partial scan data for resume capability
        
        Args:
            path (str): Path being scanned
        """
        try:
            # Create a dictionary with the current scan state
            partial_data = {
                "path": path,
                "root_info": self._root_info,
                "total_size": self._total_size,
                "processed_files": self._processed_files,
                "total_files": self._total_files,
                "processed_dirs": self._processed_dirs,
                "total_dirs": self._total_dirs,
                "file_types": self._file_types,
                "file_exts": self._file_exts,
                "seen_inodes": list(self._seen_inodes),
                "directories": self._directories,
                "files": self._files,
                "errors": self._errors,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get pending directories from the queue
            pending_dirs = []
            while not self._scan_queue.empty():
                try:
                    pending_dirs.append(self._scan_queue.get_nowait())
                    self._scan_queue.task_done()
                except queue.Empty:
                    break
            
            partial_data["pending_dirs"] = pending_dirs
            
            # Save to disk
            path_hash = hashlib.md5(path.encode()).hexdigest()
            cache_file = os.path.join(self._cache_dir, f"scan_{path_hash}.pickle")
            
            with open(cache_file, 'wb') as f:
                pickle.dump(partial_data, f)
            
            logger.info(f"Partial scan data saved to {cache_file}")
            
            # Save a mapping of path to cache file
            path_map_file = os.path.join(self._cache_dir, "path_map.json")
            path_map = {}
            
            try:
                if os.path.exists(path_map_file):
                    with open(path_map_file, 'r') as f:
                        path_map = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading path map: {e}")
            
            path_map[path] = {
                "cache_file": cache_file,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(path_map_file, 'w') as f:
                json.dump(path_map, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error saving partial scan data: {e}", exc_info=True)
    
    def _load_partial_scan(self, path):
        """
        Load partial scan data for resume capability
        
        Args:
            path (str): Path to scan
        
        Returns:
            bool: True if partial scan data was loaded, False otherwise
        """
        try:
            # Check if we have a cache for this path
            path_map_file = os.path.join(self._cache_dir, "path_map.json")
            if not os.path.exists(path_map_file):
                logger.info("No path map file found, cannot resume scan")
                return False
            
            with open(path_map_file, 'r') as f:
                path_map = json.load(f)
            
            if path not in path_map:
                logger.info(f"No cached scan found for path: {path}")
                return False
            
            cache_info = path_map[path]
            cache_file = cache_info["cache_file"]
            
            if not os.path.exists(cache_file):
                logger.warning(f"Cache file not found: {cache_file}")
                return False
            
            # Load the cached data
            with open(cache_file, 'rb') as f:
                self._partial_scan_data = pickle.load(f)
            
            self._partial_scan_path = path
            
            # Check if the cached data is for the same path
            if self._partial_scan_data.get("path") != path:
                logger.warning("Cache path mismatch, cannot resume scan")
                self._partial_scan_data = None
                self._partial_scan_path = None
                return False
            
            logger.info(f"Loaded partial scan data from {cache_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading partial scan data: {e}", exc_info=True)
            self._partial_scan_data = None
            self._partial_scan_path = None
            return False
    
    def _clear_partial_scan(self, path):
        """
        Clear partial scan data after a successful scan
        
        Args:
            path (str): Path that was scanned
        """
        try:
            path_map_file = os.path.join(self._cache_dir, "path_map.json")
            if not os.path.exists(path_map_file):
                return
            
            with open(path_map_file, 'r') as f:
                path_map = json.load(f)
            
            if path in path_map:
                cache_file = path_map[path]["cache_file"]
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                
                del path_map[path]
                
                with open(path_map_file, 'w') as f:
                    json.dump(path_map, f, indent=2)
                
                logger.info(f"Cleared partial scan data for {path}")
        
        except Exception as e:
            logger.error(f"Error clearing partial scan data: {e}", exc_info=True)

    def has_partial_scan(self, path):
        """
        Check if a partial scan exists for the given path
        
        Args:
            path (str): Path to check
        
        Returns:
            dict: Information about the partial scan, or None if no partial scan exists
        """
        try:
            # Check if we have a cache for this path
            path_map_file = os.path.join(self._cache_dir, "path_map.json")
            if not os.path.exists(path_map_file):
                return None
            
            with open(path_map_file, 'r') as f:
                path_map = json.load(f)
            
            if path not in path_map:
                return None
            
            cache_info = path_map[path]
            cache_file = cache_info["cache_file"]
            
            if not os.path.exists(cache_file):
                return None
            
            # Load the timestamp
            timestamp = cache_info.get("timestamp")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    # Format the timestamp for display
                    cache_info["formatted_time"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    cache_info["formatted_time"] = "Unknown"
            
            return cache_info
        
        except Exception as e:
            logger.error(f"Error checking for partial scan: {e}", exc_info=True)
            return None 