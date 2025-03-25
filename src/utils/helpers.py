#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Disk Space Analyzer
Helper utilities for the application
"""

import os
import re
import sys
import logging
import humanize
from datetime import datetime
import platform
import time
import psutil
import hashlib

logger = logging.getLogger("StorageStats.Utils")

def get_platform_info():
    """Get information about the current platform."""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }

def human_readable_size(size, binary=False, preferred_unit=None):
    """
    Convert a file size in bytes to a human-readable string representation.
    
    Args:
        size (int): Size in bytes
        binary (bool): If True, use binary units (KiB, MiB, etc.), otherwise use decimal (KB, MB, etc.)
        preferred_unit (str, optional): Force output in a specific unit (B, KB, MB, GB, TB, etc.)
    
    Returns:
        str: Human-readable string representation of the size
    """
    if size < 0:
        raise ValueError("Size cannot be negative")
    
    # For zero size, always return "0 B"
    if size == 0:
        if preferred_unit:
            return f"0 {preferred_unit}"
        return "0 B"
    
    if binary:
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
        base = 1024
    else:
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        base = 1000
    
    # If preferred unit is specified, convert directly to that unit
    if preferred_unit and preferred_unit in units:
        unit_index = units.index(preferred_unit)
        value = size / (base ** unit_index)
        
        # Format the output
        if unit_index == 0:
            # For bytes, we don't show decimal places
            return f"{int(value)} {units[unit_index]}"
        else:
            # For other units, we show 1 decimal place
            return f"{value:.1f} {units[unit_index]}"
    
    # Calculate the logarithm of the size with the appropriate base
    # This gives us the unit index to use
    unit_index = min(int(pow(abs(size), 1/3) // pow(base, 1/3)), len(units) - 1)
    
    # Calculate the value in the selected unit
    value = size / (base ** unit_index)
    
    # Format the output
    if unit_index == 0:
        # For bytes, we don't show decimal places
        return f"{int(value)} {units[unit_index]}"
    else:
        # For other units, we show 1 decimal place
        return f"{value:.1f} {units[unit_index]}"

def format_timestamp(timestamp):
    """Format a timestamp for display"""
    if not timestamp:
        return "N/A"
    
    if isinstance(timestamp, datetime):
        dt = timestamp
    else:
        try:
            dt = datetime.fromtimestamp(timestamp)
        except (TypeError, ValueError):
            return "Invalid timestamp"
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_time_delta(seconds):
    """Format a time delta for display"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

def get_file_icon(file_path):
    """Get an appropriate icon for a file type"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Map common extensions to icons
    # This would be expanded in a real implementation
    icon_map = {
        # Documents
        '.pdf': 'document-pdf',
        '.doc': 'document-word',
        '.docx': 'document-word',
        '.xls': 'document-excel',
        '.xlsx': 'document-excel',
        '.ppt': 'document-powerpoint',
        '.pptx': 'document-powerpoint',
        '.txt': 'document-text',
        
        # Images
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.tiff': 'image',
        
        # Audio
        '.mp3': 'audio',
        '.wav': 'audio',
        '.flac': 'audio',
        '.aac': 'audio',
        '.ogg': 'audio',
        
        # Video
        '.mp4': 'video',
        '.avi': 'video',
        '.mov': 'video',
        '.mkv': 'video',
        '.wmv': 'video',
        
        # Archives
        '.zip': 'archive',
        '.rar': 'archive',
        '.7z': 'archive',
        '.tar': 'archive',
        '.gz': 'archive',
        
        # Code
        '.py': 'code',
        '.js': 'code',
        '.html': 'code',
        '.css': 'code',
        '.c': 'code',
        '.cpp': 'code',
        '.java': 'code',
        
        # Executables
        '.exe': 'executable',
        '.app': 'executable',
        '.dmg': 'disk-image',
        
        # Special
        '': 'file'  # Default
    }
    
    return icon_map.get(ext, 'file')

def get_system_paths():
    """
    Get common system paths that might be excluded from scans.
    
    Returns:
        list: List of system paths
    """
    system = platform.system()
    paths = []
    
    if system == 'Darwin':  # macOS
        paths = [
            '/System',
            '/Library',
            '/private/var/vm',
            '/private/var/tmp',
            '/private/tmp',
            os.path.join(os.path.expanduser('~'), 'Library/Caches'),
            os.path.join(os.path.expanduser('~'), 'Library/Application Support/MobileSync/Backup')
        ]
    elif system == 'Windows':
        paths = [
            os.environ.get('WINDIR', r'C:\Windows'),
            os.path.join(os.environ.get('PROGRAMFILES', r'C:\Program Files')),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')),
            os.path.join(os.environ.get('APPDATA', r'C:\Users\Default\AppData\Roaming')),
            os.path.join(os.environ.get('LOCALAPPDATA', r'C:\Users\Default\AppData\Local')),
            os.path.join(os.environ.get('TEMP', r'C:\Users\Default\AppData\Local\Temp'))
        ]
    elif system == 'Linux':
        paths = [
            '/proc',
            '/sys',
            '/run',
            '/tmp',
            '/var/tmp',
            '/var/cache',
            '/var/log',
            '/dev',
            '/boot'
        ]
    
    return paths

def is_path_excluded(path, exclude_paths):
    """Check if a path should be excluded from analysis"""
    for exclude_path in exclude_paths:
        try:
            # Check if path is under an excluded path
            if os.path.commonpath([path, exclude_path]) == exclude_path:
                return True
        except ValueError:
            # Different drives on Windows or incompatible paths
            pass
    
    return False

def categorize_file_by_type(extension):
    """
    Categorize a file by its extension into broader categories.
    
    Args:
        extension (str): File extension without the dot
    
    Returns:
        str: Category name
    """
    # Remove the dot if it exists and convert to lowercase
    if extension.startswith('.'):
        extension = extension[1:]
    extension = extension.lower()
    
    # Define categories and their associated extensions
    categories = {
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "ico", "heic", "raw", "cr2", "nef", "arw"],
        "Videos": ["mp4", "avi", "mov", "wmv", "flv", "mkv", "webm", "m4v", "mpg", "mpeg", "3gp", "ts", "mts"],
        "Audio": ["mp3", "wav", "wma", "aac", "flac", "m4a", "ogg", "opus", "aiff", "alac"],
        "Documents": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "rtf", "odt", "ods", "odp", "pages", "numbers", "key", "md", "csv"],
        "Archives": ["zip", "rar", "tar", "gz", "7z", "bz2", "xz", "iso", "dmg", "tgz", "tbz2"],
        "Code": ["py", "java", "cpp", "c", "h", "js", "html", "css", "php", "swift", "go", "rs", "rb", "ts", "json", "xml", "yaml", "yml", "sh", "pl", "sql", "jsx", "tsx"],
        "Executables": ["exe", "app", "dll", "so", "dylib", "bin", "msi", "apk", "deb", "rpm"],
        "Databases": ["db", "sqlite", "sqlite3", "mdb", "accdb", "frm", "sql", "bak"],
        "Virtual Machines": ["vdi", "vmdk", "vhd", "qcow2", "ova", "ovf"],
        "Fonts": ["ttf", "otf", "woff", "woff2", "eot"],
        "System": ["sys", "log", "tmp", "cache", "ini", "cfg", "conf", "plist"]
    }
    
    # Check which category the extension belongs to
    for category, extensions in categories.items():
        if extension in extensions:
            return category
    
    # If no extension or not found in categories
    if not extension:
        return "No Extension"
    
    return "Other"

def safe_delete(path):
    """Safely delete a file (move to trash rather than permanent delete)"""
    # This is just a placeholder - in a real implementation, we'd use the send2trash library
    # But for this app, we're not implementing actual deletion
    return False, "This application does not perform deletions. Use your file manager to delete files."

def get_file_hash(file_path, algorithm='md5', quick_mode=False, chunk_size=8192):
    """
    Calculate the hash of a file.
    
    Args:
        file_path (str): Path to the file
        algorithm (str): Hash algorithm to use ('md5', 'sha1', 'sha256')
        quick_mode (bool): If True, only hash the first and last chunks of the file
        chunk_size (int): Size of chunks to read from the file
    
    Returns:
        str: Hexadecimal hash of the file
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    # Select the hash algorithm
    if algorithm == 'md5':
        hasher = hashlib.md5()
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
    elif algorithm == 'sha256':
        hasher = hashlib.sha256()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as f:
            # For quick mode, just hash the first and last chunks
            if quick_mode and file_size > chunk_size * 2:
                # Read first chunk
                hasher.update(f.read(chunk_size))
                
                # Seek to the last chunk
                f.seek(-chunk_size, os.SEEK_END)
                
                # Read last chunk
                hasher.update(f.read(chunk_size))
                
                # Include file size in the hash to reduce collisions
                hasher.update(str(file_size).encode())
            else:
                # Full file hash
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
        
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return None

def get_disk_info():
    """
    Get information about all mounted disks.
    
    Returns:
        list: List of dictionaries containing disk information
    """
    disks = []
    for partition in psutil.disk_partitions(all=False):
        if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
            # Skip CD-ROM drives on Windows
            continue
        
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info = {
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
            disks.append(disk_info)
        except PermissionError:
            # Some mountpoints may not be accessible
            continue
    
    return disks

def get_file_age_category(mtime):
    """
    Categorize a file by its age based on modification time.
    
    Args:
        mtime (float): File modification time as Unix timestamp
    
    Returns:
        str: Age category
    """
    now = time.time()
    age_days = (now - mtime) / (60 * 60 * 24)
    
    if age_days < 7:
        return "Last week"
    elif age_days < 30:
        return "Last month"
    elif age_days < 90:
        return "Last quarter"
    elif age_days < 365:
        return "Last year"
    elif age_days < 730:
        return "1-2 years"
    else:
        return "Older than 2 years"

def calculate_directory_size(path):
    """
    Calculate the total size of a directory.
    
    Args:
        path (str): Directory path
    
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    if os.path.islink(file_path):
                        continue
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
    except (PermissionError, OSError):
        pass
    
    return total_size 