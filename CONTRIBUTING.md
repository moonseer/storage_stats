# Contributing to Storage Stats

Thank you for considering contributing to Storage Stats! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [License](#license)

## Code of Conduct

Please follow these guidelines when contributing to the project:

- Be respectful to other contributors
- Provide constructive feedback
- Focus on the issue or feature, not on individuals
- Accept constructive criticism

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/storage_stats.git`
3. Add the upstream repository as a remote: `git remote add upstream https://github.com/original-owner/storage_stats.git`

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Testing

All contributions must include appropriate tests. Storage Stats uses pytest for testing.

### Running Tests

Run the tests using the included script:

```bash
python run_tests.py
```

Or run pytest directly:

```bash
pytest
```

### Test Requirements

1. **All new features must include tests**
   - Unit tests for utilities and core functionality
   - Integration tests for components working together
   - UI tests for interface components

2. **Test structure**
   - Unit tests go in `tests/unit/`
   - Integration tests go in `tests/integration/`
   - UI tests go in `tests/ui/`

3. **Test naming**
   - Test files should be named `test_*.py`
   - Test classes should be named `Test*`
   - Test functions should be named `test_*`

4. **Test coverage**
   - Aim for at least 80% test coverage for new code
   - Run coverage reports: `pytest --cov=src`

### Test Documentation

Each test should include:

- A clear docstring explaining what's being tested
- Descriptive test names that explain the test's purpose
- Comments for complex test logic

## Pull Request Process

1. Update your branch with the latest changes from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Run tests to ensure all tests pass:
   ```bash
   python run_tests.py
   ```

3. Create a pull request with a clear title and description
   - Describe what changes were made
   - Reference any related issues
   - Explain how to test the changes

4. Address any feedback from reviewers

## Style Guide

1. Follow PEP 8 for Python code style
2. Use docstrings to document classes and functions
3. Use clear, descriptive variable and function names
4. Keep functions small and focused on a single task
5. Add comments for complex logic

## License

By contributing to Storage Stats, you agree that your contributions will be licensed under the project's MIT License. 