#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run tests for Storage Stats application.
This script provides a convenient way to run different types of tests.
"""

import sys
import subprocess
import argparse


def run_tests(test_type=None, verbose=False, capture=False):
    """Run the tests with the specified options."""
    cmd = ["pytest"]
    
    # Add verbosity if requested
    if verbose:
        cmd.append("-v")
    
    # Add test type if specified
    if test_type == "unit":
        cmd.append("-m unit")
    elif test_type == "integration":
        cmd.append("-m integration")
    elif test_type == "ui":
        cmd.append("-m ui")
    
    # Run without capturing output if requested
    if not capture:
        cmd.append("-s")
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for Storage Stats application")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "ui", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--capture", "-c", 
        action="store_true",
        help="Capture output"
    )
    
    args = parser.parse_args()
    
    # Run the tests
    return run_tests(
        test_type=None if args.type == "all" else args.type,
        verbose=args.verbose,
        capture=args.capture
    )


if __name__ == "__main__":
    sys.exit(main()) 