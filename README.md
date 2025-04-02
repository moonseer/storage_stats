# Storage Stats

A powerful disk space analyzer for macOS built with Python and PyQt6.

## Features

Storage Stats helps you analyze and visualize how your disk space is being used:

- **File System Analysis**: Fast and efficient scanning of directories and drives.
- **Interactive Dashboard**: Get a comprehensive overview of your storage usage.
- **File Browser**: Navigate through your file system and see the size of each file and folder.
- **File Types View**: Visualize storage distribution by file types and categories with charts and tables.
- **Duplicate Detection**: Find and manage duplicate files to reclaim wasted space.
- **Large Files Finder**: Quickly identify the largest files consuming your storage.
- **Old Files Detection**: Find files you haven't used in a long time.
- **Recommendations**: Get personalized suggestions for freeing up disk space.
- **Multi-threaded Scanning**: Utilize multiple CPU cores for faster analysis.
- **Customizable Settings**: Configure exclusions, hash methods, and more.

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS 10.15 or higher (may work on older versions, but not tested)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/storage_stats.git
   cd storage_stats
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the application with:

```
python main.py
```

Then use the "Scan Directory" button or menu option to select a directory to analyze.

### Command Line Options

The application supports the following command line options:

- `-p PATH, --path PATH`: Directory path to scan on startup
- `-d, --debug`: Enable debug logging
- `--style STYLE`: Qt style to use (fusion, mac, windows)

Example:

```
python main.py -p "/Users/username/Documents" --debug
```

## Usage Guide

### Dashboard View

The dashboard provides an overview of your disk usage, including:

- Total size of scanned files and directories
- Number of files and directories
- Largest files and directories
- Storage distribution by file type
- Storage recommendations

### File Browser

Navigate through your file system with the file browser:

- View file and directory sizes
- Sort by name, size, date, etc.
- View files in hierarchical tree structure
- See detailed file properties

### File Types View

The File Types view helps you understand how storage is distributed across different file types:

- Interactive pie chart and bar chart visualizations
- Table of file extensions with counts, sizes, and percentages
- Group files by extension or category
- Sort by size, count, or name
- Easily identify which file types are consuming the most space

### Duplicate Files

Find and manage duplicate files to free up disk space:

- Identifies exact file duplicates using content hash
- Groups duplicates and calculates wasted space
- Sorts duplicates by size or wasted space
- Provides options to select which files to keep

### Recommendations

Get personalized suggestions for freeing up disk space:

- Duplicate file cleanup recommendations
- Large files review suggestions
- Old files cleanup suggestions
- Temporary files cleanup recommendations

## Architecture Documentation

For developers interested in understanding the application architecture:

- View the [Architecture Documentation](src/resources/docs/architecture.md) for a visual diagram and explanation of how components interact
- See the [Project Structure Documentation](src/resources/docs/project_structure.md) for a breakdown of the project's directory structure and purpose of each file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Testing

Storage Stats includes a comprehensive test suite that covers unit tests, integration tests, and UI tests. The tests are built using pytest and are organized in the `tests` directory.

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests that verify components work together
- `tests/ui/` - UI tests that verify the user interface works correctly

### Running Tests

You can run the tests using the included `run_tests.py` script:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run only integration tests
python run_tests.py --type integration

# Run only UI tests
python run_tests.py --type ui

# Run tests with verbose output
python run_tests.py --verbose
```

Alternatively, you can run the tests directly with pytest:

```bash
# Run all tests
pytest

# Run tests with markers
pytest -m unit
pytest -m integration
pytest -m ui

# Run tests with verbose output
pytest -v
```

### Test Coverage

The test suite covers:

1. **Core Utilities** - Tests for helper functions like `human_readable_size`
2. **Scanner** - Tests for the file system scanner functionality
3. **Analyzer** - Tests for the data analysis components
4. **UI Components** - Tests for UI components like the dashboard view
5. **Integration** - Tests that verify different components work together correctly

### Adding New Tests

When adding new functionality, please ensure you add appropriate tests. Tests should follow the naming convention:

- Unit tests: `test_*.py` in the `tests/unit/` directory
- Integration tests: `test_*.py` in the `tests/integration/` directory
- UI tests: `test_*.py` in the `tests/ui/` directory

All test functions should be prefixed with `test_` and should include docstrings describing what they test.