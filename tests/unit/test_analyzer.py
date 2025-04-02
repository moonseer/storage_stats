"""Unit tests for the analyzer module."""

import os
import pytest
from src.core.analyzer import DataAnalyzer


@pytest.mark.unit
class TestAnalyzer:
    """Tests for the DataAnalyzer class."""
    
    def test_init(self):
        """Test initialization of the analyzer."""
        analyzer = DataAnalyzer()
        assert analyzer is not None
        assert analyzer._scan_results is None
    
    def test_set_scan_results(self, scan_results):
        """Test setting scan results."""
        analyzer = DataAnalyzer()
        analyzer.set_scan_results(scan_results)
        
        assert analyzer._scan_results is not None
        assert analyzer._scan_results == scan_results
        assert analyzer.get_scan_results() == scan_results
    
    def test_get_largest_files(self, analyzed_data):
        """Test getting the largest files."""
        largest_files = analyzed_data.get_largest_files(limit=5)
        
        assert len(largest_files) <= 5
        assert isinstance(largest_files, list)
        
        # Files should be sorted by size (largest first)
        for i in range(len(largest_files) - 1):
            assert largest_files[i]['size'] >= largest_files[i + 1]['size']
        
        # Check that all returned items are files
        for file_info in largest_files:
            assert os.path.isfile(file_info['path'])
    
    def test_get_largest_dirs(self, analyzed_data):
        """Test getting the largest directories."""
        largest_dirs = analyzed_data.get_largest_dirs(limit=5)
        
        assert len(largest_dirs) <= 5
        assert isinstance(largest_dirs, list)
        
        # Directories should be sorted by size (largest first)
        for i in range(len(largest_dirs) - 1):
            assert largest_dirs[i]['size'] >= largest_dirs[i + 1]['size']
    
    def test_get_file_type_distribution(self, analyzed_data):
        """Test getting file type distribution."""
        distribution = analyzed_data.get_file_type_distribution()
        
        assert isinstance(distribution, dict)
        assert len(distribution) > 0
        
        # Check structure of distribution
        for file_type, data in distribution.items():
            assert isinstance(file_type, str)
            assert isinstance(data, dict)
            assert 'size' in data
            assert 'count' in data
            assert isinstance(data['size'], int)
            assert isinstance(data['count'], int)
    
    def test_get_file_age_distribution(self, analyzed_data):
        """Test getting file age distribution."""
        age_distribution = analyzed_data.get_file_age_distribution()
        
        assert isinstance(age_distribution, dict)
        
        # Check structure of age distribution
        for age_range, data in age_distribution.items():
            assert isinstance(age_range, str)
            assert isinstance(data, dict)
            assert 'size' in data
            assert 'count' in data
    
    def test_get_duplicate_files(self, analyzed_data):
        """Test getting duplicate files."""
        duplicates = analyzed_data.get_duplicate_files()
        
        assert isinstance(duplicates, dict)
        
        # Our test data has at least one set of duplicates
        assert len(duplicates) >= 1
        
        # Check structure of duplicates
        for file_hash, files in duplicates.items():
            assert isinstance(file_hash, str)
            assert isinstance(files, list)
            assert len(files) >= 2  # At least 2 files for a duplicate
            
            # All files in a duplicate group should have the same size
            sizes = [f['size'] for f in files]
            assert all(size == sizes[0] for size in sizes)
    
    def test_get_recommendations(self, analyzed_data):
        """Test getting recommendations."""
        recommendations = analyzed_data.get_recommendations()
        
        assert isinstance(recommendations, list)
        
        # Check structure of recommendations
        for rec in recommendations:
            assert isinstance(rec, dict)
            assert 'type' in rec
            assert 'description' in rec
            
            # Different recommendation types have different fields
            if rec['type'] == 'duplicate_files':
                assert 'count' in rec
                assert 'wasted_space' in rec
            elif rec['type'] == 'large_files':
                assert 'file_path' in rec
                assert 'size' in rec
            elif rec['type'] == 'old_files':
                assert 'file_path' in rec
                assert 'last_accessed' in rec

    def test_analyze_duplicate_files(self, analyzed_data):
        """Test analyzing duplicate files."""
        # Get duplicate files
        duplicate_files = analyzed_data.get_duplicate_files()
        
        # Calculate wasted space - it should match what the analyzer calculates
        calculated_wasted = 0
        for file_hash, files in duplicate_files.items():
            if len(files) > 1:
                # Wasted space is: (number of duplicates - 1) * file size
                calculated_wasted += (len(files) - 1) * files[0]['size']
        
        # Get the analyzer's calculation of wasted space
        duplicate_stats = analyzed_data.get_duplicate_stats()
        analyzer_wasted = duplicate_stats.get('wasted_space', 0)
        
        # They should match
        assert calculated_wasted == analyzer_wasted


@pytest.mark.integration
class TestAnalyzerIntegration:
    """Integration tests for the DataAnalyzer class."""
    
    def test_full_analysis_pipeline(self, scanner, test_files):
        """Test the full analysis pipeline from scan to recommendations."""
        # Scan the test files
        scanner.scan(test_files)
        scan_results = scanner.get_results()
        
        # Create analyzer and analyze results
        analyzer = DataAnalyzer()
        analyzer.set_scan_results(scan_results)
        
        # Run various analysis methods
        largest_files = analyzer.get_largest_files()
        largest_dirs = analyzer.get_largest_dirs()
        file_types = analyzer.get_file_type_distribution()
        duplicates = analyzer.get_duplicate_files()
        recommendations = analyzer.get_recommendations()
        
        # Verify basic structure
        assert len(largest_files) > 0
        assert len(largest_dirs) > 0
        assert len(file_types) > 0
        assert len(duplicates) > 0
        assert len(recommendations) > 0 