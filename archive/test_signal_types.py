#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test signal signatures of the DiskScanner class
"""

import sys
import os
import logging
import inspect

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SignalTest")

# Add src directory to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

def main():
    app = QApplication(sys.argv)
    
    # Import modules for testing
    logger.info("Importing DiskScanner...")
    try:
        from src.core.scanner import DiskScanner
        logger.info("DiskScanner imported successfully")
        
        # Create instance
        scanner = DiskScanner()
        logger.info("DiskScanner instance created")
        
        # Get class attributes
        attrs = dir(scanner)
        logger.info(f"DiskScanner attributes: {[a for a in attrs if not a.startswith('__')]}")
        
        # List signals
        signals = [attr for attr in attrs if isinstance(getattr(scanner.__class__, attr, None), pyqtSignal)]
        logger.info(f"Signals: {signals}")
        
        # Check signal signatures
        for signal_name in signals:
            signal = getattr(scanner.__class__, signal_name)
            logger.info(f"Signal: {signal_name}")
            
            # Get signal signature from doc or attributes
            if hasattr(signal, "__doc__") and signal.__doc__:
                logger.info(f"  Docstring: {signal.__doc__}")
            
            # Test connect and emit
            test_handler = lambda *args: logger.info(f"Signal '{signal_name}' emitted with args: {args}")
            getattr(scanner, signal_name).connect(test_handler)
            logger.info(f"  Connected test handler to {signal_name}")
            
            # Get actual parameter types if available
            # The only way to check parameter types is through signal metadata
            # But this is internal PyQt info and not easily accessible
            # We'll rely on documentation instead
        
        # Get signal documentation from scanner.py
        with open(os.path.join(src_dir, "core", "scanner.py"), "r") as f:
            scanner_code = f.read()
            
        # Find signal definitions
        import re
        signal_defs = re.findall(r"(\w+)\s*=\s*pyqtSignal\(([^)]*)\)", scanner_code)
        for name, params in signal_defs:
            logger.info(f"Signal definition: {name} = pyqtSignal({params})")
        
        # Look for the DiskScanner class definition
        disk_scanner_class = re.search(r"class DiskScanner\([^)]*\):(.*?)class", scanner_code, re.DOTALL)
        if disk_scanner_class:
            class_code = disk_scanner_class.group(1)
            # Find signal definitions within the class
            signal_defs = re.findall(r"(\w+)\s*=\s*pyqtSignal\(([^)]*)\)", class_code)
            logger.info(f"Found {len(signal_defs)} signal definitions in DiskScanner class")
            for name, params in signal_defs:
                logger.info(f"  Signal: {name} = pyqtSignal({params})")
                
                # Analyze parameters
                param_list = [p.strip() for p in params.split(',') if p.strip()]
                logger.info(f"  Parameters: {param_list}")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 