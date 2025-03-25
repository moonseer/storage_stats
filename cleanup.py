#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Stats - Cleanup Script.

This script helps clean up the project directory by moving test and debug scripts
to an archive folder, while preserving essential application files.

Usage:
    $ python3 cleanup.py
"""

import os
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Cleanup")

# Essential files to preserve (not to be moved)
ESSENTIAL_FILES = [
    'main.py',
    'README.md',
    'PROGRESS.md',
    'requirements.txt',
    '.gitignore',
    'cleanup.py'  # Don't move self
]

# Create archive folder
def create_archive_folder():
    """
    Create the archive folder if it doesn't exist.
    
    Returns:
        str: Path to the archive folder
    """
    archive_path = os.path.join(os.getcwd(), 'debug_archive')
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        logger.info(f"Created archive folder: {archive_path}")
    return archive_path

def should_move_file(filename):
    """
    Determine if a file should be moved to the archive.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if the file should be moved, False otherwise
    """
    # Don't move essential files
    if filename in ESSENTIAL_FILES:
        return False
    
    # Don't move directories
    if os.path.isdir(filename) and not filename.startswith('.'):
        return False
    
    # Move all Python test/debug files
    if filename.endswith('.py') and filename != 'main.py':
        return True
    
    # Move log files
    if filename.endswith('.log'):
        return True
    
    # Move specific debug files
    if 'debug' in filename.lower() or 'test' in filename.lower():
        return True
    
    return False

def main():
    """
    Main function to archive test and debug files.
    """
    logger.info("Starting cleanup process")
    
    # Create archive folder
    archive_path = create_archive_folder()
    
    # Get list of files in current directory
    files = [f for f in os.listdir('.') if os.path.isfile(f) or (os.path.isdir(f) and not f.startswith('.'))]
    
    # Move files to archive
    moved_count = 0
    for filename in files:
        if should_move_file(filename):
            source_path = os.path.join(os.getcwd(), filename)
            dest_path = os.path.join(archive_path, filename)
            
            try:
                shutil.move(source_path, dest_path)
                logger.info(f"Moved: {filename} -> {dest_path}")
                moved_count += 1
            except Exception as e:
                logger.error(f"Failed to move {filename}: {e}")
    
    logger.info(f"Cleanup completed. Moved {moved_count} files to {archive_path}")

if __name__ == "__main__":
    main() 