#!/usr/bin/env python3
import os
import time

def human_readable_size(size):
    """Simple function to format file sizes"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"

def scan_directory(path):
    """Scan a directory and print file size statistics"""
    print(f"Scanning directory: {path}")
    start_time = time.time()
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for root, dirs, files in os.walk(path):
        dir_count += len(dirs)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.isfile(file_path) and not os.path.islink(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                    
                    # Print info for some of the larger files
                    if file_size > 1024*1024*10:  # Files larger than 10MB
                        print(f"Large file: {file_path}, Size: {human_readable_size(file_size)}")
            except (PermissionError, OSError) as e:
                print(f"Error accessing {file_path}: {e}")
    
    scan_time = time.time() - start_time
    print(f"\nScan completed in {scan_time:.2f} seconds")
    print(f"Total files: {file_count}")
    print(f"Total directories: {dir_count}")
    print(f"Total size: {human_readable_size(total_size)}")
    print(f"Total size (bytes): {total_size}")
    
    # Check for permissions
    print("\nChecking for permission issues...")
    sample_count = 0
    for root, dirs, files in os.walk(path):
        if sample_count > 10:
            break
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"Successfully read size of {file_path}: {size} bytes")
                    sample_count += 1
                    if sample_count >= 10:
                        break
            except Exception as e:
                print(f"Error: {e} for {file_path}")

if __name__ == "__main__":
    scan_directory("/Users/moonseer/Downloads") 