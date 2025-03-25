#!/usr/bin/env python3
import os

def main():
    """Check file sizes in the Downloads directory"""
    downloads_path = os.path.expanduser("~/Downloads")
    print(f"Checking file sizes in: {downloads_path}")
    
    if not os.path.exists(downloads_path):
        print(f"Error: Path {downloads_path} does not exist")
        return
    
    total_size = 0
    file_count = 0
    
    # Check a few files directly
    print("\nChecking some individual files:")
    for i, entry in enumerate(os.scandir(downloads_path)):
        if i >= 10:  # Only check the first 10 entries
            break
            
        if entry.is_file():
            try:
                size = os.path.getsize(entry.path)
                print(f"File: {entry.name}, Size: {size} bytes ({size / (1024**3):.6f} GB)")
                total_size += size
                file_count += 1
            except Exception as e:
                print(f"Error with {entry.path}: {e}")
    
    print(f"\nSampled {file_count} files, total size: {total_size} bytes ({total_size / (1024**3):.6f} GB)")
    
    # Now scan the entire directory
    print("\nScanning entire directory...")
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(downloads_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
            except Exception:
                pass  # Ignore errors for this quick check
    
    print(f"Found {file_count} files with total size: {total_size} bytes ({total_size / (1024**3):.6f} GB)")

if __name__ == "__main__":
    main() 