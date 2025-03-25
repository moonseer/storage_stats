# Storage Stats - Project Structure

This document outlines the structure of the Storage Stats project and provides a description of the purpose of each file and directory.

## Root Directory

- **main.py**: The main entry point of the application. It initializes the application, parses command-line arguments, sets up logging, and creates the enhanced main window.
- **cleanup.py**: A utility script to organize the project directory by moving test and debug files to an archive folder while preserving essential application files.
- **requirements.txt**: Lists all the Python dependencies required by the application.
- **README.md**: Provides an overview of the application, its features, installation instructions, and usage guide.
- **PROGRESS.md**: Tracks the development progress of the application, including completed tasks, current issues, and next steps.
- **.gitignore**: Specifies files and directories that Git should ignore.

## Source Code (`src/`)

The `src/` directory contains all the application source code, organized into several subdirectories:

### Core (`src/core/`)

Contains the core functionality of the application:

- **scanner.py**: Implements the `DiskScanner` class responsible for traversing the file system and collecting data about files and directories. Uses multi-threading for efficient scanning of large file systems.
- **analyzer.py**: Implements the `DataAnalyzer` class that processes the data collected by the Scanner to identify large files, duplicate files, and generate recommendations.
- **__init__.py**: Marks the directory as a Python package and may contain package-level initialization code.

### UI (`src/ui/`)

Contains all the user interface components:

- **main_window.py**: Implements the main application window that integrates all the UI components.
- **dashboard_view.py**: Provides an overview of disk usage, including total size, largest files/directories, and storage distribution.
- **file_browser_view.py**: Allows users to navigate through the file system and see the size of each file and folder.
- **file_types_view.py**: Visualizes storage distribution by file types and categories with charts and tables.
- **duplicates_view.py**: Allows users to find and manage duplicate files to reclaim wasted space.
- **recommendations_view.py**: Provides personalized suggestions for freeing up disk space.
- **settings_dialog.py**: Allows users to configure application settings.
- **filter_dialog.py**: Provides options for filtering scan results.
- **shortcuts_dialog.py**: Displays keyboard shortcuts available in the application.
- **report_generator.py**: Generates reports of scan results for saving or sharing.
- **__init__.py**: Marks the directory as a Python package and may contain package-level initialization code.

### Utils (`src/utils/`)

Contains utility functions used throughout the application:

- **helpers.py**: Contains various utility functions such as file size formatting, hash calculation, and file type categorization.
- **__init__.py**: Marks the directory as a Python package and may contain package-level initialization code.

### Resources (`src/resources/`)

Contains static resources used by the application, including:

- **docs/**: Documentation files for the project:
  - **architecture.md**: Describes the application architecture with a Mermaid diagram.
  - **project_structure.md**: This document, describing the project file structure.

## Archive Directories

- **debug_archive/**: Contains debug and test files that were moved by the cleanup script.
- **archive/**: May contain older versions of files or other archived content.

## Development Environment

- **venv/**: Python virtual environment containing all the installed dependencies.
- **.git/**: Git repository data.

## Project Evolution

The project has gone through several iterations of development, with recent fixes addressing:

1. Segmentation fault issues related to signal connections
2. File size calculation and display problems
3. Method name inconsistencies across the codebase
4. Dictionary access patterns
5. UI component reference issues

The application is built using the PyQt6 framework for the GUI, with additional libraries for data processing (pandas, numpy), visualization (matplotlib, seaborn), and utility functions (psutil, humanize). 